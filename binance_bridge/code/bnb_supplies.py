from web3.providers.rpc import HTTPProvider
from web3 import Web3
from web3.exceptions import TooManyRequests
import json
import csv
import pandas as pd
from web3.middleware import ExtraDataToPOAMiddleware
import datetime
import time

#api = "bnb_getblock_api_key"
api = "alchemy_eth_api_key"

with open(api,"r") as f:
    api_key = f.readline().rstrip()

url = f"https://bnb-mainnet.g.alchemy.com/v2/{api_key}"

print( f"url = {url}" )

w3 = Web3(Web3.HTTPProvider(url))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]') 

tokens = { 'BUSD': '0xe9e7cea3dedca5984780bafc599bd69add087d56',
            'BSC-USD': '0x55d398326f99059fF775485246999027B3197955',
            'FDUSD': '0xc5f0f7b66764F6ec8C8Dff7BA683102295E16409',
            'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d' }

deploy_blocks = { 'BUSD': 124241,
                'BSC-USD': 176416,
                'FDUSD': 27850220,
                'USDC': 1477489 }

tokens = { k : w3.to_checksum_address( v ) for k,v in tokens.items() }
contracts = { k : w3.eth.contract(a, abi=ERC20_ABI) for k,a in tokens.items() }
files = { k: f'../data/bnb/{k}.csv' for k in tokens.keys() }

columns = [ 'address', 'symbol', 'block', 'supply', 'ts' ]

latest_block = w3.eth.get_block_number()
step_size = 5000

min_blocks = { k: latest_block for k in tokens.keys() }
finished = { k: False for k in tokens.keys() }

for k, outfile in files.items():
    try:
        df = pd.read_csv( outfile )
        min_blocks[k] = df.block.min() - step_size
    except Exception as e:
        print( e )
        print( f"Creating {outfile}" )
        with open( outfile, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
            writer.writeheader()

block = int( max( [ b for b in min_blocks.values() ] ) )
while True:
    try:
        block_ts = w3.eth.get_block(block)['timestamp']
    except TooManyRequests as te:
        print( te )
        time.sleep(30)
        continue
    except Exception as e:
        print( e )
        time.sleep(5)
        continue
    ts = datetime.datetime.fromtimestamp(block_ts)
    print( f'Grabbing block {block} at time {ts}' )

    for symbol, a in tokens.items():
        if deploy_blocks[symbol] > block:
            finished[symbol] = True
            continue
        try:
            supply = contracts[symbol].functions.totalSupply().call(block_identifier=block)
            row = { 'block': block, 'ts': ts, 'address': a, 'symbol': symbol, 'supply': supply  }
            with open( files[symbol], 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
                writer.writerow( row )
        except Exception as e:
            print( f"Error {symbol} at block {block}" )
            print( e ) 
            finished[symbol] = True
            continue

    if all( finished.values() ):
        break

    block = block - step_size
    
