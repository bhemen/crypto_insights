"""
    Plot Aave lending activity around the time of the Ethereum merge

    Requires the data file "../data/v2_aave_tvl.csv"

"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import os
import re
import sys
#import matplotlib.dates as mdates
#myFmt = mdates.DateFormatter('%m-%d-%Y')

df = pd.read_csv( "../data/v2_aave_tvl.csv", dtype={'variableDebt':float,'stableDebt':float,'aTokenSupply':float,'variableBorrowRate':float,'stableBorrowRate':float} )
df = df[df.symbol=='WETH'] #Aave handles ERC20 tokens, so it does not handle ETH directly, but instead handles WETH
df.ts = pd.to_datetime( df.ts, format='%Y-%m-%d %H:%M:%S+00:00' )

start_date = pd.to_datetime( "2022-09-01",format="%Y-%m-%d")
end_date = pd.to_datetime( "2022-09-30", format="%Y-%m-%d" )
merge_date = pd.to_datetime( "2022-09-15", format="%Y-%m-%d" ) #Date of the Ethereum merge

df.stableDebt = df.stableDebt/10**18                    #ETH (and WETH) use 18 digits of precision
df.variableDebt = df.variableDebt/10**18
df.aTokenSupply = df.aTokenSupply/10**18
df.stableBorrowRate = 100*(df.stableBorrowRate/10**27) #Aave uses 'Ray' math for internal variables (https://docs.aave.com/developers/v/2.0/glossary)
df.variableBorrowRate = 100*(df.variableBorrowRate/10**27)

########################################################
#Plot dates where ETH borrowing is allowed
#######################################################

#Ethereum borrowing was paused in the lead-up to the merge (https://governance-v2.aave.com/governance/proposal/97/), and we can see that on-chain

ax = plt.gca()
ax.set_xlim([start_date,end_date])

plt.yticks(ticks=[0,1], labels=['Disabled','Enabled'])
plt.xlabel( "" )

#Simple solution is plot the days where ETH borrowing was enabled
#But this has *vertical* lines
#plt.step( df.ts, df.borrowingEnabled, label='Borrowing Enabled' )
#plt.xticks(rotation=45)

#Complicated method to remove vertical lines using plt.hlines()
left = ~( df.borrowingEnabled.shift(1) == df.borrowingEnabled )
right = ~( df.borrowingEnabled.shift(-1) == df.borrowingEnabled )

left = left[left].index
right = right[right].index
yvals = [df.borrowingEnabled.iloc[0]]
for _ in range(len(left)-1):
    yvals += [not yvals[-1]]

x = df.ts
plt.hlines( yvals,x[left],x[right], colors=['green' if y else 'red' for y in yvals], linewidth=5.0 )
plt.title( "Ethereum borrowing disabled" )

plt.axvline(merge_date,linewidth=.5,linestyle='-',color='grey' )
plt.text(merge_date - pd.to_timedelta(1,unit='d'), .4, 'Merge', rotation='vertical', color='grey')

plt.xticks( [start_date,x[left[1]],x[right[1]],end_date], rotation=45, ha='right' )
plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig( "../figures/eth_borrowing_enabled.png" )
plt.clf()

########################################################
#Plot amount of ETH borrowed
#######################################################

#Stable debt zoomed in
plt.plot( df.ts, df.stableDebt, label='Stable Debt' )

ax = plt.gca()
ax.set_xlim([start_date,end_date])

plt.axvline(merge_date,linewidth=.5,linestyle='-',color='grey' )
plt.text(merge_date - pd.to_timedelta(1,unit='d'), .4, 'Merge', rotation='vertical', color='grey')

plt.xticks( rotation=45, ha='right' )

plt.title( "ETH stable debt" )
plt.tight_layout() #Prevent the xticks from being cut off
plt.savefig( "../figures/eth_stable_debt_close.png" )
plt.clf()

#Stable debt zoomed out
plt.plot( df.ts, df.stableDebt, label='Stable Debt' )

ax = plt.gca()

plt.axvline(merge_date,linewidth=.5,linestyle='-',color='grey' )
plt.text(merge_date + pd.to_timedelta(20,unit='d'), 200000, 'Merge', rotation='vertical', color='grey')

plt.xticks( rotation=45, ha='right' )

plt.title( "ETH stable debt" )
plt.tight_layout() #Prevent the xticks from being cut off
plt.savefig( "../figures/eth_stable_debt_full.png" )
plt.clf()

#Variable debt zoomed out
plt.plot( df.ts, df.variableDebt, label='Variable Debt' )
#plt.plot( df.ts, df.stableDebt + df.variableDebt, label='Total Debt' )

ax = plt.gca()

plt.axvline(merge_date,linewidth=.5,linestyle='-',color='grey' )
plt.text(merge_date - pd.to_timedelta(40,unit='d'), 0, 'Merge', rotation='vertical', color='grey')

plt.xticks( rotation=45, ha='right' )

plt.title( "ETH variable debt" )
plt.tight_layout() #Prevent the xticks from being cut off
plt.savefig( "../figures/eth_variable_debt_full.png" )
plt.clf()

########################################################
#Plot amount of ETH deposited
#######################################################

#The aToken supply gives the amount of ETH owed to lenders by the platform, so the supply of aETH is the amount of ETH in the lending pool *plus* the amount of ETH lent to borrowers
plt.plot( df.ts, df.aTokenSupply, label='Total ETH Deposits' )
#plt.plot( df.ts, df.variableDebt, label='Variable Debt' )
#plt.plot( df.ts, df.stableDebt + df.variableDebt, label='Total Debt' )

ax = plt.gca()

ax.set_xlim([merge_date - pd.to_timedelta(2,unit='d'),merge_date + pd.to_timedelta(2,unit='d')])

plt.axvline(merge_date,linewidth=.5,linestyle='-',color='grey' )
plt.text(merge_date - pd.to_timedelta(4,unit='h'), 10**6, 'Merge', rotation='vertical', color='grey')

plt.xticks( [merge_date + pd.to_timedelta(x,unit='d') for x in range(-2,3)], rotation=45, ha='right' )
plt.title("Total ETH deposited by lenders")

plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig( "../figures/eth_liquidity.png" )
plt.clf()

########################################################
#Plot Variable Borrow Rate
#######################################################

plt.plot( df.ts, df.variableBorrowRate, label='Variable Borrow Rate' )

ax = plt.gca()
ax.yaxis.set_major_formatter(mticker.PercentFormatter())

ax.set_xlim([start_date,end_date])

plt.axvline(merge_date,linewidth=.5,linestyle='-',color='grey' )
plt.text(merge_date - pd.to_timedelta(1,unit='d'), 0, 'Merge', rotation='vertical', color='grey')

#plt.xticks( [merge_date + pd.to_timedelta(x,unit='d') for x in range(-10,11)], rotation=45, ha='right' )
plt.xticks( rotation=45, ha='right' )
plt.title("Variable borrow rate")
plt.legend()

plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig( "../figures/eth_variable_borrow_rate.png" )
plt.clf()

########################################################
#Plot Stable Borrow Rate
#######################################################

plt.plot( df.ts, df.stableBorrowRate, label='Stable Borrow Rate' )
#plt.plot( df.ts, df.variableDebt, label='Variable Debt' )
#plt.plot( df.ts, df.stableDebt + df.variableDebt, label='Total Debt' )

ax = plt.gca()
ax.yaxis.set_major_formatter(mticker.PercentFormatter())
#ax.xaxis.set_major_formatter(myFmt)

ax.set_xlim([start_date,end_date])

plt.axvline(merge_date,linewidth=.5,linestyle='-',color='grey' )
plt.text(merge_date - pd.to_timedelta(1,unit='d'), 10**6, 'Merge', rotation='vertical', color='grey')

#plt.xticks( [merge_date + pd.to_timedelta(x,unit='d') for x in range(-10,11)], rotation=45, ha='right' )
plt.xticks( rotation=45, ha='right' )
plt.title("Stable borrow rate")

plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig( "../figures/eth_stable_borrow_rate.png" )
plt.clf()

########################################################
#Plot Combined Debts
#######################################################

plt.plot( df.ts, df.variableDebt, label='Variable Debt' )
plt.plot( df.ts, df.stableDebt, label='Stable Debt' )
#plt.plot( df.ts, df.stableDebt + df.variableDebt, label='Total Debt' )

ax = plt.gca()

plt.axvline(merge_date,linewidth=1,linestyle='-',color='grey' )
plt.text(merge_date - pd.to_timedelta(40,unit='d'), 500000, 'Merge', rotation=90, color='grey')

plt.xticks( rotation=45, ha='right' )

plt.title("ETH Debt")

plt.tight_layout() #Prevent the xticks from being cut off

plt.savefig( "../figures/eth_combined_full.png" )
plt.clf()

#symbol,stableDebt,variableDebt,variableBorrowRate,stableBorrowRate,borrowingEnabled,atokenSupply,ts,block_num



