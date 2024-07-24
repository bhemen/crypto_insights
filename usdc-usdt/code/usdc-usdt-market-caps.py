import matplotlib.pyplot as plt
import pandas as pd

usdc = pd.read_csv('../data/USDC_history.csv', dtype={'snapped_at': str, 'price': float, 'market_cap': float, 'total_volume': float } )
usdc.snapped_at = pd.to_datetime(usdc.snapped_at)
usdt = pd.read_csv('../data/USDT_history.csv', dtype={'snapped_at': str, 'price': float, 'market_cap': float, 'total_volume': float } )
usdt.snapped_at = pd.to_datetime(usdt.snapped_at)

combined = pd.merge_asof( usdc, usdt, on='snapped_at', direction='nearest' )
combined['market_cap'] = combined.market_cap_x + combined.market_cap_y
combined.drop( set(combined.columns).difference( ['snapped_at','market_cap'] ), axis=1, inplace=True )

plt.plot( usdc.snapped_at,usdc.market_cap/10**9, label='USDC' )
plt.plot( usdt.snapped_at,usdt.market_cap/10**9, label='USDT' )
#plt.plot( combined.snapped_at,combined.market_cap/10**9, label='Total' )

ax = plt.gca()
ax.set_xlim([pd.to_datetime('2022-01-01',format='%Y-%m-%d'),usdc.snapped_at.max()] )
plt.xticks(rotation=45)

plt.xlabel( "" )
plt.ylabel( "Market cap (billions)" )
plt.axvline(pd.Timestamp('2023-03-10'),linewidth=.5,linestyle='-',color='grey' )
plt.text( pd.Timestamp('2023-02-10'), 1, 'SVB Collapse', rotation='vertical', color='grey')

plt.axvline(pd.Timestamp('2022-05-09'),linewidth=.5,linestyle='-',color='grey' )
plt.text( pd.Timestamp('2022-04-09'), 1, 'Terra Collapse', rotation='vertical', color='grey')

plt.legend()
plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig('../figures/usdc-usdt-market-caps.png')

