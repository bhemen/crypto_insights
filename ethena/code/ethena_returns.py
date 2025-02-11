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

w3 = Web3(Web3.HTTPProvider(url))

susde_address = '0x9D39A5DE30e57443BfF2A8307A4256c8797A3497'
susde = w3.eth.contract( w3.to_checksum_address(susde_address), abi=susde_abi )
outfile = f'../data/ethena_returns.csv'
susde_deploy_block = 18571359
step_size = 5000

seconds_per_day = 86400
block_time = 12
blocks_per_day = seconds_per_day/ block_time

durations = { 'weekly': 7,
                'monthly': 30,
                'sixty_days': 60,
                'quarterly': 90,
                'yearly': 365 }

durations = { k: int(v*blocks_per_day) for k,v in durations.items() }

latest_block = int( w3.eth.get_block_number() )
print( f'Latest block = {latest_block}' )
step_size = 5000
deposit_amt = 1000*10**18

columns = ['block','ts','deposit_amt'] + list( durations.keys() )

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
        lp_shares = susde.functions.previewDeposit(deposit_amt).call(block_identifier=block_num) 
    except Exception as e:
        print( e )
        continue
    returns = {}
    for k,d in durations.items():
        later_block = int( block_num + d )
        returns[k] = -2
        if later_block < latest_block:
            try:
                returns[k] = susde.functions.previewRedeem(lp_shares).call(block_identifier=later_block )
            except Exception as e:
                with open( 'ethena_errors.txt', 'a' ) as f:
                    f.write( f"Error at block {block_num + d}\n" )
                    f.write( str(e) )
                    f.write( "\n" )
                returns[k] = -1

    row = { 'block': block_num, 'ts': ts, 'deposit_amt': deposit_amt }
    row.update( returns )

    with open( outfile, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
        writer.writerow( row )
