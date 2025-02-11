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

with open( 'abis/susde.abi', 'r' ) as f:
    susde_abi = json.load( f )

with open( 'abis/usde.abi', 'r' ) as f:
    usde_abi = json.load( f )

w3 = Web3(Web3.HTTPProvider(url))

usde_address = w3.to_checksum_address('0x4c9EDD5852cd905f086C759E8383e09bff1E68B3')
susde_address = w3.to_checksum_address('0x9D39A5DE30e57443BfF2A8307A4256c8797A3497')
susde = w3.eth.contract( susde_address, abi=susde_abi )
usde = w3.eth.contract( usde_address, abi=usde_abi )

assert w3.to_checksum_address( susde.functions.asset().call() ) == usde_address

outfile = f'../data/ethena_staking.csv'
susde_deploy_block = 18571359
usde_deploy_block = 18571358

step_size = 5000

latest_block = int( w3.eth.get_block_number() )
print( f'Latest block = {latest_block}' )
step_size = 5000

columns = ['block','ts','supply','staked','staked_s']

try:
    df = pd.read_csv( outfile )
    start_block = int( df.block.max() )
except Exception as e:
    print( e )
    print( f"Creating {outfile}" )
    with open( outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
    start_block = susde_deploy_block

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
        supply = usde.functions.totalSupply().call(block_identifier=block_num)
        staked = usde.functions.balanceOf(susde_address).call(block_identifier=block_num)
        staked_s = susde.functions.totalAssets().call(block_identifier=block_num)
    except Exception as e:
        print( e )
        continue

    row = { 'block': block_num, 'ts': ts, 'supply': supply, 'staked': staked, 'staked_s': staked_s }

    with open( outfile, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
        writer.writerow( row )
