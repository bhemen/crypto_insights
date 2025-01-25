from web3.providers.rpc import HTTPProvider
from web3 import Web3
from web3.exceptions import BlockNumberOutOfRange
import json
import csv
import pandas as pd
from web3.middleware import ExtraDataToPOAMiddleware
import datetime
import time
from tqdm import tqdm

provider = 'alchemy'

if provider == 'alchemy':
    api = "alchemy_eth_api_key"
    base_url = "https://eth-mainnet.g.alchemy.com/v2/"

with open(api,"r") as f:
    api_key = f.readline().rstrip()

url = base_url + api_key

#url = 'http://127.0.0.1:8545'
print( f"url = {url}" )

w3 = Web3(Web3.HTTPProvider(url))

addresses = pd.read_csv( '../data/binance_addresses.csv' )

tokens = { 'BUSD': { 'address': w3.to_checksum_address('0x4Fabb145d64652a948d72533023f6E7A623C7C53'), 'deploy_block': 8493105, 'binance_addresses': [], 'contract': None },
          'USDC': { 'address': w3.to_checksum_address('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'), 'deploy_block': 6082465, 'binance_addresses': [], 'contract': None } }

for symbol in tokens.keys():
    binance_addresses = list( addresses[ (addresses.Coin == symbol ) & (addresses.Network == 'ETH')  ]['Address'] )
    binance_addresses = [ w3.to_checksum_address(a) for a in binance_addresses ]
    tokens[symbol]['binance_addresses'] = binance_addresses

    with open( f'abis/{symbol.lower()}.abi', 'r' ) as f:
        abi = json.load( f )

    tokens[symbol]['contract'] = w3.eth.contract( address=tokens[symbol]['address'], abi=abi )

step_size = 5000

for symbol in tokens.keys():
    outfile = f'../data/{symbol.lower()}_balances.csv'

    latest_block = int( w3.eth.get_block_number() )
    print( f'Latest block = {latest_block}' )

    columns = ['block','ts','total_supply'] 
    columns += tokens[symbol]['binance_addresses']

    try:
        df = pd.read_csv( outfile )
        start_block = int( df.block.max() )
    except Exception as e:
        print( e )
        print( f"Creating {outfile}" )
        with open( outfile, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
            writer.writeheader()
        start_block = tokens[symbol]['deploy_block']

    for block_num in tqdm( range( start_block, latest_block, step_size) ):
        try:
            block_ts = w3.eth.get_block(block_num)['timestamp']
        except Exception as e:
            print( e )
            time.sleep(5)
            continue

        ts = datetime.datetime.fromtimestamp(block_ts)
        #print( f'Grabbing block {block_num} at time {ts}' )

        try:
            supply = tokens[symbol]['contract'].functions.totalSupply().call(block_identifier=block_num)
        except Exception as e:
            print( e )
            continue

        row = { 'block': block_num, 'ts': ts, 'total_supply': float(supply) }

        for a in tokens[symbol]['binance_addresses']:
            try:
                balance = tokens[symbol]['contract'].functions.balanceOf(a).call(block_identifier=block_num)
            except Exception as e:
                balance = 0
                print( e )
                continue
            row.update( {a: float( balance )} )

        with open( outfile, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
            writer.writerow( row )
