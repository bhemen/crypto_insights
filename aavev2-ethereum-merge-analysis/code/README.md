# Code

## Grabbing data

[get_lending_data.py](get_lending_data.py) grabs data from the Aave v2 (and v3) lending pool contracts using the python web3 library.
The code queries historical balances, so it requires an Ethereum Full Archive node to run.
If you don't run your own node, [Alchemy's free tier](https://www.alchemy.com/pricing) is more than sufficient to run this script.

The data collected by this script is available in this repository [v2_aave_tvl.csv](../../aave_data/v2_aave_tvl.csv) and [v3_aave_tvl.csv](../../aave_data/v3_aave_tvl.csv).

## Plotting

[plot.py](plot.py) uses matplotlib to create basic plots of the data collected by [get_lending_data.py](get_lending_data.py).

## Interactive analysis

[aave_v2_analysis_plots.ipynb](aave_v2_analysis_plots.ipynb) is an interactive Python notebook that allows you to explore Aave data around the 
time of the Ethereum merge.

This script does not use the data collected by [get_lending_data.py](get_lending_data.py), but instead uses a larger Aave v2 data set (that contains individual-level data) 
that is available on Box:

- [aave_collateralization_v2.csv](https://upenn.box.com/shared/static/rjgq5fjkmh1blem46c4edibjsfk056jx.csv)
- [aave_collateralization_meta_v2.csv](https://upenn.box.com/s/rnuz37qc03en2grs6h4xu58n880azu1u)

These files need to be downloaded and placed in the `aave_data` folder before running the Python notebook.

These files are described in more depth in our Aave repository: [https://github.com/bhemen/aave-data](https://github.com/bhemen/aave-data).

