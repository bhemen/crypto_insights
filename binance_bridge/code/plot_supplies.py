import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

chains = ['avax','polygon','ethereum' ]

decimals={ 'avax': { 'DAI.e': 18, 'USDC': 6, 'DAI': 18, 'USDC.e': 6, 'USDT': 6, 'USDT.e': 6 },
          'polygon': { 'AXLUSDC': 6, 'USDC': 6, 'DAI': 18, 'USDC.e': 6, 'USDT': 6, 'USDT.e': 6, 'USDC (Wormhole) II': 6, 'USDC (Wormhole)': 6 },
          'ethereum': { 'BUSD': 18, 'USDC': 6, 'DAI': 18, 'FDUSD': 18, 'USDT': 6 } }

titles = { 'avax': 'Avalanche', 'polygon': 'Polygon', 'ethereum': 'Ethereum', 'bnb': 'Binance BNB' }

df = pd.read_csv( '../data/busd_balances.csv', parse_dates=['ts'] )

binance_addresses = [ a for a in df.columns if a[0:2] == '0x' ]
df['binance_reserves'] = df[binance_addresses].sum(axis=1)

bnb_df = pd.read_csv('../data/bnb/BUSD.csv', parse_dates=['ts'], dtype={'supply':float} )

plt.plot( df.ts, df.total_supply/(10**(9+18)), label='BUSD supply' )
plt.plot( df.ts, df.binance_reserves/(10**(9+18)), label='Binance Reserves' )
plt.plot( bnb_df.ts, bnb_df.supply/(10**(9+18)), label='Binance-Peg BUSD Supply' )

plt.xticks(rotation=45)

plt.axvline(pd.Timestamp('2023-02-13'),linewidth=.5,linestyle='-',color='grey' )
plt.text( pd.Timestamp('2022-12-15'), 2, 'NYDFS Action', rotation='vertical', color='grey')
#plt.text( pd.Timestamp('2023-3-20'), 5, 'against BUSD', rotation='vertical', color='grey')

plt.xlabel( "" )
plt.ylabel( "Billions of BUSD" )
plt.legend(loc='upper left' )
plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig( '../figures/busd.png', dpi=1200 )
