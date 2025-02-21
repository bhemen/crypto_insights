import requests
from tqdm import tqdm
from datetime import datetime, timedelta
from pathlib import Path
import csv
import time

with open("alchemy_api_key","r") as f:
    api_key = f.readline().rstrip()

url = f"https://api.g.alchemy.com/prices/v1/{api_key}/tokens/historical"

tokens = [
    "USDe",
    "USDC",
    "USDT",
    "DAI",
    "USDS"
]

start_date = datetime(2022, 1, 1)
end_date = datetime.today()
batch_size = 365 #Alchemy max batch size is 365 days (https://docs.alchemy.com/reference/get-historical-token-prices)
start_backoff = 5
backoff = start_backoff

for symbol in tqdm(tokens, desc="Processing tokens"):
    outfile = f'data/{symbol}.csv'
    current_date = start_date
    total_days = (end_date - start_date).days
    num_batches = (total_days + batch_size - 1) // batch_size  # Round up division
    
    for current_date in tqdm(range(num_batches), desc=f"Fetching {symbol} data", leave=False):
        # Calculate end time for this interval (either 30 days later or end_date)
        interval_end = min(start_date + timedelta(days=(current_date + 1) * batch_size), end_date)
        start_time = start_date + timedelta(days=current_date * batch_size)
        
        payload = {
            "symbol": symbol,
            "startTime": start_time.strftime("%Y-%m-%dT00:00:00Z"),
            "endTime": interval_end.strftime("%Y-%m-%dT23:59:59Z"),
            "interval": "1d"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Alchemy-API-Key": api_key
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            backoff = start_backoff
            data = response.json()['data']
            rows = [ { 'price': v['value'], 'timestamp': datetime.strptime(v['timestamp'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d") } for v in data ]
            if Path(outfile).exists():
                with( open(outfile,'a') as f ):
                    dw = csv.DictWriter( f, fieldnames=['timestamp','price'] )
                    for row in rows:
                        dw.writerow(row)
            else:
                with( open(outfile,'w') as f ):
                    dw = csv.DictWriter( f, fieldnames=['timestamp','price'] )
                    dw.writeheader()
                    for row in rows:
                        dw.writerow(row)
        elif response.status_code == 400:
            tqdm.write( f"Error: {response.text}" )
            break
        elif response.status_code == 404:
            tqdm.write( f"Token {symbol} not found" )
            break
        elif response.status_code == 429:
            time.sleep(backoff)
            backoff *= 2
        else:
            tqdm.write(f"Error: {response.status_code}")
            tqdm.write(f"Error: {response.text}")
