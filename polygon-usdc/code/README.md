# Scripts

## Data collection 
* [get_supply.py](get_supply.py) Grabs the historical supplies of USDC and USDC.e on Polygon from a Polygon archive node.  Output is written to [polygon_usdc.csv](../data/polygon_usdc.csv)
* [get_polymarket_balances.py](get_polymarket_balances.py) Grabs the USDC.e balances of the Polymarket contract from a Polygon archive node.  Output is written to [polymarket_usdce_holdings.csv](../data/polymarket_usdce_holdings.csv)

## Plotting

* [plot_supply.py](plot_supply.py) Creates [polygon_usdc_supply.png](../figures/polygon_usdc_supply.png)
* [plot_uscde_holdings.py](plot_usdce_holdings.py) Creates [polymarket_usdce_holdings.png](../figures/polymarket_usdce_holdings.png)

## Getting started

If you are using Alchemy as your node provider, set 
```
ALCHEMY_API_KEY=<API_KEY>
```
in the file `.env.api`

Install the requirements

```
pip install -r requirements.txt
```

or
```
uv add -r requirements.txt
```


