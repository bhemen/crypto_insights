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
from dotenv import load_dotenv
import os

load_dotenv('.env.api')

alchemy_api_key = os.getenv('ALCHEMY_API_KEY')

alchemy_api_url = f"https://polygon-mainnet.g.alchemy.com/v2/{alchemy_api_key}"


provider = 'alchemy'

if provider == 'alchemy':
    url = alchemy_api_url
else:
    url = 'http://127.0.0.1:8545'

w3 = Web3(Web3.HTTPProvider(url))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

print( f"url = {url}" )

with open( 'abis/usdc.abi', 'r' ) as f:
    usdc_abi = json.load( f )
with open( 'abis/usdc.e.abi', 'r' ) as f:
    usdce_abi = json.load( f )

addresses = { 'USDC.e': w3.eth.contract( w3.to_checksum_address( '0x2791bca1f2de4661ed88a30c99a7a9449aa84174' ), abi=usdce_abi ),
             'USDC': w3.eth.contract( w3.to_checksum_address( '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359' ), abi=usdc_abi ) }

latest_block = int( w3.eth.get_block_number() )
print( f'Latest block = {latest_block}' )
step_size = 5000

columns = ['block','token_address','token_symbol','ts','supply']
usdc_deploy_block = 45319261
usdce_deploy_block = 5013591
outfile = '../data/polygon_usdc.csv'

try:
    df = pd.read_csv( outfile )
    # Get the max block for each address
    address_last_block = df.groupby('token_address')['block'].max().to_dict()
    for address in addresses:
        if address not in address_last_block.keys():
            address_last_block[address] = usdce_deploy_block
    # Start from the earliest block that needs updating
    start_block = min(address_last_block.values()) if address_last_block else usdce_deploy_block
except Exception as e:
    print( e )
    print( f"Creating {outfile}" )
    with open( outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
    start_block = usdc_deploy_block
    address_last_block = {}

for block_num in tqdm( range( start_block, latest_block, step_size) ):
    try:
        block_ts = w3.eth.get_block(block_num)['timestamp']
    except Exception as e:
        print( e )
        time.sleep(5)
        continue

    ts = datetime.datetime.fromtimestamp(block_ts)
    #print( f'Grabbing block {block_num} at time {ts}' )

    for symbol, contract in addresses.items():
        # Skip if block is before contract deployment
        deploy_block = usdc_deploy_block if symbol == 'USDC' else usdce_deploy_block
        if block_num < deploy_block:
            continue

        try:
            supply = contract.functions.totalSupply().call(block_identifier=block_num)
            row = { 'block': block_num, 'ts': ts, 'token_symbol': symbol, 'token_address': contract.address, 'supply': supply }
            with open( outfile, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
                writer.writerow( row )
        except Exception as e:
            print( e )
            continue


