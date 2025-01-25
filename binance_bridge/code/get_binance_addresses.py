"""
    Scrape a list of Binance custody addresses from the Binance blog
"""

import pandas as pd

url = 'https://www.binance.com/en/blog/community/our-commitment-to-transparency-2895840147147652626'
tables = pd.read_html(url)

df = tables[0]

df.columns = df.iloc[0]  # Set the first row as column headers
df = df.drop(0).reset_index(drop=True)

print( df.columns )

df.to_csv( "../data/binance_addresses.csv", index=False )
