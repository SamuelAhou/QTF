#!/usr/bin/env python3
"""
Main script to download BTCUSDT data from Binance for the last 2 years.
Demonstrates the new asset-based data management system.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent / "src"))

from src.DataProvider import (
    get_data_manager, 
    check_asset_data_needs,
    smart_fetch_data
)

def download_btcusdt_data():
    """Download BTCUSDT data from Binance for the last 2 years."""
    
    print("=== BTCUSDT Data Download from Binance ===\n")
    
    # Initialize data manager
    dm = get_data_manager("data")
    
    # Parameters
    provider = "binance"
    symbol = "BTCUSDT"
    interval = "1d"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)  # 2 years
    
    print(f"Downloading {symbol} data:")
    print(f"  Provider: {provider}")
    print(f"  Interval: {interval}")
    print(f"  Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"  Total days: {(end_date - start_date).days}")
    print()
    
    # Check what data is needed
    print("1. Analyzing data needs...")
    needs = check_asset_data_needs(symbol, start_date, end_date, provider, interval)
    
    print(f"  Needs download: {needs['needs_download']}")
    print(f"  Reason: {needs['download_reason']}")
    print(f"  Missing days: {needs['missing_days']}")
    
    if needs['missing_range']:
        print(f"  Missing ranges:")
        for start, end in needs['missing_range']:
            print(f"    {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    
    if needs['existing_data'] and needs['existing_data']['has_data']:
        existing = needs['existing_data']['data_range']
        print(f"  Existing data: {existing['start']} to {existing['end']} ({existing['days']} days)")
    
    print()
    
    # Download the data
    print("2. Downloading data...")
    try:
        data = dm.get_data(provider, [symbol], start_date, end_date, interval)
        
        if symbol in data:
            df = data[symbol]
            print(f"  Successfully downloaded data for {symbol}")
            print(f"  Data points: {len(df)}")
            print(f"  Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
            print(f"  Columns: {list(df.columns)}")
            
            # Show some sample data
            print(f"\n  Sample data (first 5 rows):")
            print(f"    {df.head().to_string()}")
            
            # Show some statistics
            if 'Close' in df.columns:
                print(f"\n  Price statistics:")
                print(f"    Min Close: ${df['Close'].min():.2f}")
                print(f"    Max Close: ${df['Close'].max():.2f}")
                print(f"    Last Close: ${df['Close'].iloc[-1]:.2f}")
                
                # Calculate returns
                returns = df['Close'].pct_change().dropna()
                print(f"    Mean daily return: {returns.mean():.4f}")
                print(f"    Volatility: {returns.std():.4f}")
            
            # Show file information
            print(f"\n3. File information:")
            raw_file, clean_file = dm._get_data_file_paths(provider, symbol, start_date, end_date, interval)
            print(f"  Raw file: {raw_file}")
            print(f"  Clean file: {clean_file}")
            print(f"  Raw exists: {raw_file.exists()}")
            print(f"  Clean exists: {clean_file.exists()}")
            
            if raw_file.exists():
                print(f"  Raw file size: {raw_file.stat().st_size} bytes")
            if clean_file.exists():
                print(f"  Clean file size: {clean_file.stat().st_size} bytes")
            
        else:
            print(f"  Error: No data returned for {symbol}")
            
    except Exception as e:
        print(f"  Error downloading data: {e}")
        return False
    
    print(f"\n=== Download Complete ===")
    print(f"\nData for {symbol} has been successfully downloaded and stored.")
    print(f"The data is now available for backtesting and analysis.")
    
    return True

def main():
    """Main function."""
    print("Starting BTCUSDT data download...\n")
    
    success = download_btcusdt_data()
    
    if success:
        print("\n✅ Script completed successfully!")
    else:
        print("\n❌ Script encountered errors.")
    
    print("\nYou can now use this data in your backtesting strategies.")

if __name__ == "__main__":
    main()
