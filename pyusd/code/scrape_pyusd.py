from dotenv import load_dotenv
from get_contract_logs import getContractEvents
import os
from web3 import Web3

load_dotenv('.env.api')

alchemy_api_key = os.getenv('ALCHEMY_API_KEY')
chainstack_api_key = os.getenv('CHAINSTACK_API_KEY')

alchemy_api_url = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_api_key}"
chainstack_api_url = f"https://ethereum-mainnet.core.chainstack.com/{chainstack_api_key}"
api_url = chainstack_api_url

deploy_block = start_block = 15921958
contract_address = "0x6c3ea9036406852006290770bedfcaba0e23a0e8" #PyUSD token

contract_address = Web3.to_checksum_address(contract_address)
target_events = ['SupplyIncreased','SupplyDecreased']

outfile = "../data/pyusd_admin_logs.csv"

getContractEvents( contract_address, target_events, outfile, api_url=api_url, start_block=deploy_block ,end_block=None )
