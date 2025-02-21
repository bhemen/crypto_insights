# Stablecoin Price Data

As of February 2025, the top three stablecoins by market cap are USDT, USDC, and USDe.

This repository contains scripts for scraping stablecoin price data from [Alchemy](https://docs.alchemy.com/reference/get-historical-token-prices), and plotting the data.

The plot below shows big dips in the USDC price at the [Voyager collapse](https://www.coindesk.com/layer2/2022/07/12/behind-voyagers-fall-crypto-broker-acted-like-a-bank-went-bankrupt) and the [FTX collapse](https://www.forbes.com/sites/forbesstaff/article/the-fall-of-ftx/).  Somewhat surprisingly the [collapse of 3AC](https://cointelegraph.com/news/3ac-a-10b-hedge-fund-gone-bust-with-founders-on-the-run) (immediately before Voyager) and [Celsius](https://www.coindesk.com/markets/2022/07/15/the-fall-of-celsius-network-a-timeline-of-the-crypto-lenders-descent-into-insolvency) (immediately after Voyager) did not lead to a big dips in the USDC price.  The Chicago Fed has a nice [timeline of these events](https://www.chicagofed.org/publications/chicago-fed-letter/2023/479).

![USDC and USDT Price Data](figures/USDC-USDT.png)

Note that USDe was not [launched until November 14 2023](https://etherscan.io/tx/0xc8119dfca3e004587af37affd06ff7e73bfe47035147c1d478a17daa71dcfcc6), and Alchemy does not have data for USDe 
before 12-14-2023.  The plot below shows the price data for USDe, USDC, and USDT, during the period when all three were available.

![USDe, USDC, and USDT Price Data](figures/USDe-USDC-USDT.png)

From this plot, it is clear that USDe is significantly more volatile than USDC and USDT.

# Data

[scrape_prices.py](scrape_prices.py) scrapes historical price data from [Alchemy](https://docs.alchemy.com/reference/get-historical-token-prices).  Data is stored in `data/`.  For example

* [data/USDC.csv](data/USDC.csv) contains USDC prices
* [data/USDT.csv](data/USDT.csv) contains USDT prices
* [data/USDe.csv](data/USDe.csv) contains USDe prices
* [data/USDS.csv](data/USDS.csv) contains USDS prices
* [data/DAI.csv](data/DAI.csv) contains DAI prices

The columns are `timestamp` and `price` (in USD).  

Note that this pricing data is not directly available on the blockchain, instead, Alchemy aggregates both on-chain and off-chain prices to produce these data sets.  As far as I know, Alchemy does not provide the methodology by which they produce these prices, i.e., if the prices vary during the course of a day, or if there is price discrepancy between different sources (e.g., a difference in price between Binance and Uniswap).
