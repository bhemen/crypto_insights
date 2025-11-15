import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Read the data
df = pd.read_csv('../data/polygon_usdc.csv')

# Convert timestamp to datetime
df['ts'] = pd.to_datetime(df['ts'])

# Convert supply to billions (supply is in wei, 6 decimals for USDC, so dividing by 10^(9+6) is scaling to billions)
df['supply_billions'] = df['supply'] / 1e15

# Separate data for each token
usdc = df[df['token_symbol'] == 'USDC'].copy()
usdce = df[df['token_symbol'] == 'USDC.e'].copy()

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(usdce['ts'], usdce['supply_billions'], label='USDC.e', linewidth=2)
ax.plot(usdc['ts'], usdc['supply_billions'], label='USDC', linewidth=2)

# Add shaded region for DeFi Summer
#defi_summer_start = datetime(2021, 6, 1)
#defi_summer_end = datetime(2021, 8, 31)
#defi_summer_mid = datetime(2021, 7, 15)
#ax.axvspan(defi_summer_start, defi_summer_end, alpha=0.2, color='gray')
#ax.text(defi_summer_mid, ax.get_ylim()[0] * 1.05, 'DeFi Summer',
#        horizontalalignment='center', verticalalignment='bottom',
#        fontsize=9, alpha=0.8, style='italic')

# Add vertical lines for key events
events = [
    (datetime(2021, 3, 11), 'First 5000 Days Sells for \$69M'),
    (datetime(2021, 4, 20), 'Aave launches on Polygon'),
    (datetime(2022, 5, 11), 'Terra/Luna Crash'),
    (datetime(2023, 3, 10), 'SVB Collapse'),
    (datetime(2023, 11, 10), 'Circle halts USDC.e withdrawals'),
    (datetime(2024, 11, 5), 'US Presidential Election'),
]

for event_date, event_label in events:
    ax.axvline(x=event_date, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(event_date, ax.get_ylim()[1] * 0.95, event_label,
            rotation=90, verticalalignment='top', horizontalalignment='right',
            fontsize=9, alpha=0.8)

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Total Supply (Billions)', fontsize=12)
ax.set_title('USDC and USDC.e Total Supply on Polygon', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()

# Save the figure
plt.savefig('../figures/polygon_usdc_supply.png', dpi=300, bbox_inches='tight')
print("Plot saved to ../figures/polygon_usdc_supply.png")

# Show the plot
plt.show()
