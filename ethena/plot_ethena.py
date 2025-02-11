import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys
import numpy as np

df = pd.read_csv( 'data/ethena_staking.csv', converters = { 'block': int, 'staked': float, 'staked_s': float, 'supply': float }, parse_dates=['ts'] )

df['staked_pct'] = df.staked / df.supply

plt.plot( df.ts, df.staked_pct )

plt.xlabel( "" )
plt.ylabel( "Fraction of USDe staked" )
plt.xticks(rotation=45)

#plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
plt.title( f'Ethena Staked USDe' )
plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig(f':igures/ethena_staked.png')
plt.clf()

df = pd.read_csv( 'data/ethena_returns.csv', converters = { 'block': int, 'deposit_amt': float, 'weekly': float, 'monthly': float, 'sixty_days': float, 'quarterly': float, 'yearly': float }, parse_dates=['ts'] )
#df['ts'] = pd.to_datetime( df.ts, format='%Y-%m-%d %H:%M:%S' )

durations = { 'weekly': 7, 'monthly': 30, 'sixty_days': 60, 'quarterly': 90, 'yearly': 365 }

for k,v in durations.items(): #Convert to annualized returns
    df.loc[df[k] < 0, k] = np.nan
    df[f'returns_{k}'] = (df[k]/df.deposit_amt)**(365/v) - 1

for k in ['monthly','quarterly']:
#for k in durations.keys():
    plt.plot( df.ts, df[f'returns_{k}'], label=f'Compounded {k}' )

plt.xlabel( "" )
plt.ylabel( "sUSDe Returns" )
plt.xticks(rotation=45)

import matplotlib.ticker as mtick


plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.))

plt.legend(loc='upper right')
plt.title( f'sUSDe Returns' )
plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig(f'figures/ethena_returns.png')
plt.clf()
