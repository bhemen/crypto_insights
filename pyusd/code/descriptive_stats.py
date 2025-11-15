import pandas as pd

def format_large_number(num):
    """Format large numbers with human-readable suffixes"""
    if num >= 1e12:
        return f"{num/1e12:.1f}T"
    elif num >= 1e9:
        return f"{num/1e9:.1f}B"
    elif num >= 1e6:
        return f"{num/1e6:.1f}M"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return f"{num:.1f}"

df = pd.read_csv('../data/pyusd_admin_logs.csv', dtype={'value':float})

df.value = df.value/1e6
mints = df[df['event'] == 'SupplyIncreased']
burns = df[df['event'] == 'SupplyDecreased']

table = mints.groupby('msg.sender')['value'].sum().sort_values(ascending=False) 

# Convert to DataFrame and format addresses as links
table_df = table.to_frame(name='Total Value')
table_df.index.name = 'Minter'
table_df['Total Value'] = table_df['Total Value'].apply(format_large_number)
table_df.index = table_df.index.map(lambda addr: f"[{addr}](https://intel.arkm.com/explorer/address/{addr})")
table_md = table_df.to_markdown()

# Print as markdown table
print(table_md)
