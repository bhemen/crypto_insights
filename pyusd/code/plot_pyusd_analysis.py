#!/usr/bin/env python3
"""
pyUSD Admin Logs Analysis Script

This script analyzes pyUSD admin logs data and generates three plots:
1. Histogram of number of Mints (SupplyIncreased) per address
2. Histogram of amount Minted per address
3. Line chart showing total supply over time
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

def format_supply_readable(value):
    """Format supply value in millions to readable units (B=billion, T=trillion)."""
    if value >= 1e6:  # Trillions
        return f"{value/1e6:.2f}T"
    elif value >= 1e3:  # Billions
        return f"{value/1e3:.2f}B"
    else:  # Millions
        return f"{value:.2f}M"

def load_and_prepare_data(csv_path):
    """Load and prepare the pyUSD admin logs data."""
    print("Loading data...")
    df = pd.read_csv(csv_path)
    
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.value = df.value/1e6 #PyUSD has 6 decimals
    
    print(f"Loaded {len(df)} records")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"Event types: {df['event'].value_counts().to_dict()}")
    
    return df

def plot_total_supply_over_time(df, output_dir):
    """Create line chart showing total supply over time with broken axis for spikes."""
    print("Creating line chart of total supply over time...")
    
    # Sort by timestamp
    df_sorted = df.sort_values('timestamp')
    
    # Calculate cumulative supply changes
    df_sorted['supply_change'] = 0.0
    df_sorted.loc[df_sorted['event'] == 'SupplyIncreased', 'supply_change'] = df_sorted['value']
    df_sorted.loc[df_sorted['event'] == 'SupplyDecreased', 'supply_change'] = -df_sorted['value']
    
    # Calculate cumulative total supply
    df_sorted['cumulative_supply'] = df_sorted['supply_change'].cumsum()
    
    # Convert to more readable units
    df_sorted['cumulative_supply_readable'] = df_sorted['cumulative_supply'] / 1e6
    
    # Analyze the data to determine if we need a broken axis
    max_supply = df_sorted['cumulative_supply_readable'].max()
    
    # Calculate percentiles to identify outliers
    q95 = df_sorted['cumulative_supply_readable'].quantile(0.95)
    
    # Determine if we need a broken axis (if max is significantly larger than 95th percentile)
    use_broken_axis = max_supply > q95 * 1.5
    
    if use_broken_axis:
        # Create a broken axis plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Determine the break point (e.g., 95th percentile)
        break_point = q95 * 1.2
        y_lower_max = q95 * 1.5
        
        # Plot on upper axis (spike range) - convert to billions
        ax1.plot(df_sorted['datetime'], df_sorted['cumulative_supply_readable'] / 1e3, 
                 linewidth=2, color='darkblue', alpha=0.8)
        ax1.set_ylim((break_point * 0.8) / 1e3, (max_supply * 1.05) / 1e3)
        ax1.set_ylabel('Total Supply (pyUSD) (in Billions)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Plot on lower axis (main range) - convert to billions
        ax2.plot(df_sorted['datetime'], df_sorted['cumulative_supply_readable'] / 1e3, 
                 linewidth=2, color='darkblue', alpha=0.8)
        ax2.set_ylim(0, y_lower_max / 1e3)
        ax2.set_ylabel('Total Supply (pyUSD) (in Billions)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Add title
        ax1.set_title('pyUSD Total Supply', fontsize=14, fontweight='bold')
        
        # Format x-axis
        ax2.set_xlabel('Date', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        
        # Hide the spines between the axes
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.xaxis.tick_top()
        ax1.tick_params(labeltop=False)
        ax2.xaxis.tick_bottom()
        
        # Add diagonal lines to indicate break
        d = 0.015  # how big to make the diagonal lines in axes coordinates
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False, linewidth=1)
        ax1.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
        
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'total_supply_over_time.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
    else:
        # Regular plot without broken axis
        plt.figure(figsize=(14, 8))
        plt.plot(df_sorted['datetime'], df_sorted['cumulative_supply_readable'] / 1e3, 
                 linewidth=2, color='darkblue', alpha=0.8)
        
        plt.xlabel('Date')
        plt.ylabel('Total Supply (pyUSD) (in Billions)')
        plt.title('pyUSD Total Supply')
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'total_supply_over_time.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Saved total supply chart to {output_dir}/total_supply_over_time.png")
    
def main():
    """Main function to run the analysis."""
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'pyusd_admin_logs.csv')
    output_dir = os.path.join(script_dir, '..', 'figures')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print("pyUSD Admin Logs Analysis")
    print("=" * 50)
    
    # Load and prepare data
    df = load_and_prepare_data(data_path)
    
    # Generate plots
    plot_total_supply_over_time(df, output_dir)
    
    print("\nAnalysis complete! All plots saved to the figures directory.")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()
