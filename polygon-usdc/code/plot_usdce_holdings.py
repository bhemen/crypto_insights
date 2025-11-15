import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Read the data
df = pd.read_csv('../data/polymarket_usdce_holdings.csv')

# Convert timestamp to datetime
df['ts'] = pd.to_datetime(df['ts'])

# Convert balance to millions (assuming balance is in wei, 6 decimals for USDC.e)
df['balance_millions'] = df['balance'] / 1e12

# Get unique holders
holders = df['holder'].unique()

holders = [ holder for holder in holders if holder.startswith('Polymarket') ]

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot each holder's balance over time
for holder in holders:
    holder_data = df[df['holder'] == holder].copy()
    ax.plot(holder_data['ts'], holder_data['balance_millions'], label=holder, linewidth=2)

# Add vertical lines for key events
events = [
    (datetime(2024, 11, 5), 'US presidential election'),
]

for event_date, event_label in events:
    ax.axvline(x=event_date, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.text(event_date, ax.get_ylim()[1] * 0.95, event_label,
            rotation=90, verticalalignment='top', horizontalalignment='right',
            fontsize=9, alpha=0.8)

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Balance (Millions)', fontsize=12)
ax.set_title('Polymarket USDC.e Holdings', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()

# Save the figure
plt.savefig('../figures/polymarket_usdce_holdings.png', dpi=300, bbox_inches='tight')
print("Plot saved to ../figures/polymarket_usdce_holdings.png")

# Show the plot
plt.show()
