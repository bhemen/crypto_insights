# pyUSD Analysis Scripts

* [scrape-pyusd.py](scrape_pyusd.py) - Scrapes the `SupplyIncreased` and `SupplyDecreased` events from the PyUSD Token contract deployed at address [0x6c3ea9036406852006290770bedfcaba0e23a0e8](https://etherscan.io/address/0x6c3ea9036406852006290770bedfcaba0e23a0e8).  Results are saved to [data/pyusd_admin_logs.csv](data/pyusd_admin_logs.csv).  Running this script against a remote node (e.g. Alchemy / Chainstack) is very slow.  But if you need new data, just re-run the script and it will pick up where it left off.

* [plot_pyusd_analysis.py](plot_pyusd_analysis.py) - Reads the data from [data/pyusd_admin_logs.csv](data/pyusd_admin_logs.csv), and plots the token supply by adding the `SupplyIncreased` and subtracting the `SupplyDecreased` calls.  The output is stored in [figures/total_supply_over_time.png](figures/total_supply_over_time.png)

* [descriptive_stats.py](descriptive_stats.py) - Reads the data from [data/pyusd_admin_logs.csv](data/pyusd_admin_logs.csv) and generates the table found in the [README](../README.md), showing how many PyUSD each address has minted. 

## Usage

1. **Setup**: Ensure `.env.api` file contains your API keys:
   ```
   ALCHEMY_API_KEY=your_alchemy_key
   CHAINSTACK_API_KEY=your_chainstack_key
   ```
   This is needed for [scrape_pyusd.py](scrape_pyusd.py).
   If you're running a local Ethereum Archive Node, you should change the `api_url` in 
   [scrape_pyusd.py](scrape_pyusd.py), as it will be much faster.
1. Get the event scrapers
    1. [get_contract_logs.py](https://github.com/bhemen/ethereum-scraping/blob/main/event-scraper/get_contract_logs.py) from [Event Scraper](https://github.com/bhemen/ethereum-scraping/tree/main/event-scraper)
    1. [utils.py](https://github.com/bhemen/ethereum-scraping/blob/main/event-scraper/utils.py) from [Event Scraper](https://github.com/bhemen/ethereum-scraping/tree/main/event-scraper)
    You can grab these by running:
    ```
    wget https://raw.githubusercontent.com/bhemen/ethereum-scraping/refs/heads/main/event-scraper/utils.py
    wget https://raw.githubusercontent.com/bhemen/ethereum-scraping/refs/heads/main/event-scraper/get_contract_logs.py
    ```
