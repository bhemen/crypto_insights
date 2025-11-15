"""
This script gets the historical information from the Aave v2 and v3 lending pools
The script collects
    * Interest rates (both stable and variable)
    * Total debt
for every token supported by Aave

Data is written to:
../../aave_data/v2_aave_tvl.csv
../../aave_data/v3_aave_tvl.csv
"""

from web3.providers.rpc import HTTPProvider
from web3 import Web3
import json
import datetime
import pandas as pd
from pathlib import Path
import requests
import time
from tqdm import tqdm

api_url = 'http://127.0.0.1:8545' #Change this if you are not running a local node

provider = HTTPProvider(api_url) 
web3 = Web3(provider)

error_file = "errors.txt"

def getABI( v, a, n ):
    """
        Get a contract ABI from Etherscan

        To avoid excessive calls to Etherscan, ABIs are cached locally in the "abis" folder
        v = Aave version (either v = 'v2' or v = 'v3')
        a = Contract address
        n = name (string used in the cached filename)
    """
    abifile = f"abis/{v}_{n}.abi"
    path = Path( abifile )
    if not path.exists():
        print( f'Downloading {v} oracle ABI' )
        response = requests.get(f"https://api.etherscan.io/api?module=contract&action=getabi&address={a}&format=raw")
        time.sleep(5) #Without an API key from Etherscan, you must wait between queries
        with open( abifile, 'wb' ) as f:
            f.write(response.content)
    with open(abifile,'r') as f:
        abi = json.load(f)
    return abi

#https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts
#https://docs.aave.com/developers/deployed-contracts/v3-mainnet/ethereum-mainnet
oracles = { 'v2': Web3.to_checksum_address("0xa50ba011c48153de246e5192c8f9258a2ba79ca9"), 'v3': Web3.to_checksum_address("0x54586bE62E3c3580375aE3723C145253060Ca0C2") }
data_providers = { 'v2' :Web3.to_checksum_address("0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d"), 'v3': Web3.to_checksum_address("0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3") }
deploy_blocks = { 'v2': 11362589, 'v3': 16291078 } #Block numbers where the contracts were deployed

oracle_contracts = {}
for v,a in oracles.items():
    abi = getABI( v, a, 'oracle' )
    oracle_contracts.update( {v: web3.eth.contract( address=a, abi=abi ) } )

data_provider_contracts = {}
for v,a in data_providers.items():
    abi = getABI( v, a, 'data_provider' )
    data_provider_contracts.update( { v: web3.eth.contract( address=a, abi=abi ) } )


########
#Get a list of all the tokens Aave considers 'reserve' tokens
#Aave tracks the price for all these tokens
#https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider#getallreservestokens
#tokens = { 'v2' : [ (symbol,address,atoken_contract) ... ], 'v3' : [(symbol,address,atoken_contract) ...] }
tokens = {}
for v,c in data_provider_contracts.items():
    with open( f'abis/atoken{v}.abi', 'r' ) as f:
        abi = json.load(f)
    token_list = c.functions.getAllReservesTokens().call()
    atoken_list = c.functions.getAllATokens().call()
    token_dict = { symbol:address for (symbol,address) in token_list }
    atoken_dict = { symbol: web3.eth.contract(address=address,abi=abi)  for (symbol,address) in atoken_list }
    if v == 'v2':
        vtokens = [ (symbol,token_dict[symbol],atoken_dict["a" + symbol.upper()]) for symbol in token_dict.keys() ]
    if v == 'v3':
        vtokens = [ (symbol,token_dict[symbol],atoken_dict["aEth" + symbol]) for symbol in token_dict.keys() ]
    tokens.update( { v : vtokens} )

current_block = web3.eth.block_number

for v,c in data_provider_contracts.items():
    print( f"Grabbing data for Aave {v}" )
    blocks = [int(b) for b in range( deploy_blocks[v], current_block, 500 ) ]
    rows = []
    for block in tqdm(blocks):
        block_ts = web3.eth.get_block(block)['timestamp']
        ts = datetime.datetime.fromtimestamp(block_ts, datetime.timezone.utc)
        for symbol,address,atoken_contract in tokens[v]:
            row = {}
            try:
                reserve_data = c.functions.getReserveData(address).call(block_identifier=block)
                reserve_configuration_data = c.functions.getReserveConfigurationData(address).call(block_identifier=block)
                if v == 'v3':
                    #https://docs.aave.com/developers/core-contracts/aaveprotocoldataprovider#getreservedata
                    availableLiquidity = 0 #No function to get this in v3 from the lending pool contract
                    aTokenSupply = reserve_data[2]
                    stableDebt = reserve_data[3]
                    variableDebt = reserve_data[4]
                    variableBorrowRate = reserve_data[6]
                    stableBorrowRate = reserve_data[7]
                    borrowingEnabled = reserve_configuration_data[6]
                if v == 'v2':
                    aTokenSupply = atoken_contract.functions.totalSupply().call(block_identifier=block) #In v3 you can get the aToken supply from the pool itself, from v2, you have to call the aToken contract
                    #https://docs.aave.com/developers/v/2.0/the-core-protocol/protocol-data-provider#getreservedata
                    availableLiquidity = reserve_data[0]
                    stableDebt = reserve_data[1]
                    variableDebt = reserve_data[2]
                    variableBorrowRate = reserve_data[4]
                    stableBorrowRate = reserve_data[5]
                    borrowingEnabled = reserve_configuration_data[6]
                row.update( { 'symbol': symbol, 'availableLiquidity': availableLiquidity, 'stableDebt': stableDebt, 'variableDebt': variableDebt, 'variableBorrowRate': variableBorrowRate, 'stableBorrowRate': stableBorrowRate, 'borrowingEnabled': borrowingEnabled, 'aTokenSupply': aTokenSupply } )
            except Exception as e:
                with open( error_file, 'a' ) as f:
                    f.write( f"{v},{block},{c.address},{address},{e}\n" )
                    continue
            row.update( { 'ts': ts, 'block_num': block } )
            rows.append(row)

    df = pd.DataFrame(rows)
    rows=[]
    df.to_csv( f'../../aave_data/{v}_aave_tvl.csv', index=False )

    
