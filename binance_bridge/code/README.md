# Overview

There are four scripts used in this analysis

* [get_binance_addresses.py](get_binance_addresses.py) - scrapes [this site](https://www.binance.com/en/blog/community/our-commitment-to-transparency-2895840147147652626') to get a list of addresses controlled by Binance.  Addresses are written to [binance_addresses.csv](data/binance_addresses.csv).
* [bnb_supplies.py](bnb_supplies.py) - Connects to a BNB archive node (we used [alchemy](https://www.alchemy.com)), and gets the historical supplies of different stablecoins on the BNB chain.  The data are written to the folder [../data/bnb/](data/bnb)
* [get_binance_reserves.py](get_binance_reserves.py) - Connects to an Ethereum archive node (we used [alchemy](https://www.alchemy.com)), and gets the historical BUSD balances for the addresses in [binance_addresses.csv](data/binance_addresses.csv).  The data are written to [data/busd_balances.csv](data/busd_balances.csv) 
* [plot_supplies.py](plot_supplies.py) - Plots the historical supply data to generate [busd.png](../figures/busd.png), which can be found in the [main story](../README.md)