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
chainstack_api_key = os.getenv('CHAINSTACK_API_KEY')

alchemy_api_url = f"https://polygon-mainnet.g.alchemy.com/v2/{alchemy_api_key}"

addresses = { 'Polymarket Conditional Tokens': '0x4D97DCd97eC945f40cF65F87097ACe5EA0476045',
            'Polymarket Wrapped Collateral': '0x3A3BD7bb9528E159577F7C2e685CC81A765002E2', 
            'ByBit': '0x1347378B1d0Eb69d3462e09b3dFa2Fe28ebE74eC',
             'Wormhole': '0x5a58505a96D1dbf8dF91cB21B54419FC36e93fdE',
             'Uniswap v3 USDCe/USDC Pool': '0xD36ec33c8bed5a9F7B6630855f1533455b98a418' }


provider = 'alchemy'

if provider == 'alchemy':
    url = alchemy_api_url
elif provider == 'chainstack':
    url = chainstack_api_url
else:
    url = 'http://127.0.0.1:8545'

w3 = Web3(Web3.HTTPProvider(url))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

print( f"url = {url}" )

with open( 'abis/usdc.e.abi', 'r' ) as f:
    usdce_abi = json.load( f )

usdce_address = w3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
usdce = w3.eth.contract( usdce_address, abi=usdce_abi )

latest_block = int( w3.eth.get_block_number() )
print( f'Latest block = {latest_block}' )
step_size = 5000

columns = ['block','ts','supply','holder','holder_address','balance']
usdce_deploy_block = 5013591
outfile = '../data/polymarket_usdce_holdings.csv'

try:
    df = pd.read_csv( outfile )
    # Get the max block for each address
    address_last_block = df.groupby('holder_address')['block'].max().to_dict()
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
    start_block = usdce_deploy_block
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
    try:
        supply = usdce.functions.totalSupply().call(block_identifier=block_num)
    except Exception as e:
        print( e )
        continue

    row = { 'block': block_num, 'ts': ts, 'supply': supply }

    for holder,address in addresses.items():
        # Only query if this block is after the last recorded block for this address
        last_block = address_last_block.get(address, usdce_deploy_block-1)
        if block_num <= last_block:
            continue

        try:
            balance = usdce.functions.balanceOf(address).call(block_identifier=block_num)
            row.update( { 'holder': holder, 'holder_address': address, 'balance': balance } )
        except Exception as e:
            continue

        with open( outfile, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
            writer.writerow( row )
