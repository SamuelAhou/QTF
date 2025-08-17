# Asset-Based Data Management Features

This document describes the enhanced asset-based data management capabilities added to the `DataProvider.py` module. The system now stores data by asset name only and intelligently manages date ranges for efficient data fetching.

## Overview

The enhanced asset-based data management system provides:

1. **Asset-Based Storage**: Data files stored by symbol and interval only (e.g., `AAPL_1d.parquet`)
2. **Intelligent Date Range Management**: Automatically detects what data you have vs. what you need
3. **Partial Data Downloading**: Only downloads missing date ranges, never re-downloads existing data
4. **Seamless Data Extension**: Easy to extend data to new dates without duplication
5. **Smart Data Merging**: Automatically combines existing and new data
6. **Comprehensive Asset Information**: Detailed insights into your stored data

## Key Features

### 1. Asset-Based File Storage

Data is now stored with a simplified naming convention:

```
{symbol}_{interval}.parquet
```

**Examples:**
- `AAPL_1d.parquet` - Apple daily data
- `BTCUSDT_1h.parquet` - Bitcoin hourly data
- `SPY_1d.parquet` - SPDR S&P 500 ETF daily data

**Benefits:**
- No more duplicate files for different date ranges
- Easy to find and manage data for specific assets
- Simple file organization by asset type

### 2. Smart Data Fetching

The system automatically detects what data you need and only downloads what's missing:

```python
from DataProvider import smart_fetch_data
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# This will only download missing data and merge with existing data
data = smart_fetch_data("yahoo", "AAPL", start_date, end_date, "1d")
```

**What happens automatically:**
1. Checks what data you already have for AAPL
2. Identifies missing date ranges
3. Downloads only the missing data
4. Merges new data with existing data
5. Saves the complete dataset

### 3. Data Needs Analysis

Check exactly what data is needed before fetching:

```python
from DataProvider import check_asset_data_needs

# Analyze what data is needed
needs = check_asset_data_needs("AAPL", start_date, end_date, "yahoo", "1d")

if needs['needs_download']:
    print(f"Missing {needs['missing_days']} days of data")
    for start, end in needs['missing_range']:
        print(f"  Missing: {start} to {end}")
else:
    print("Data already complete!")
```

### 4. Asset Data Range Information

Get detailed information about what data you have for each asset:

```python
from DataProvider import get_data_manager

dm = get_data_manager()
asset_info = dm.get_asset_data_range("yahoo", "AAPL", "1d")

if asset_info['has_data']:
    data_range = asset_info['data_range']
    print(f"AAPL data: {data_range['start']} to {data_range['end']}")
    print(f"Total days: {data_range['days']}")
    print(f"Data points: {asset_info['data_points']}")
```

### 5. Batch Asset Management

Get information about all your assets at once:

```python
from DataProvider import get_all_asset_ranges

# Get all equity assets with their data ranges
all_assets = get_all_asset_ranges(asset_type="Equities", provider="yahoo", interval="1d")

for asset_type, assets in all_assets.items():
    print(f"\n{asset_type}:")
    for asset in assets:
        if asset['has_data']:
            print(f"  {asset['symbol']}: {asset['data_range']['start']} to {asset['data_range']['end']}")
```

## Usage Examples

### Basic Data Fetching

```python
from DataProvider import smart_fetch_data
from datetime import datetime, timedelta

# Fetch 1 year of data for multiple symbols
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

data = smart_fetch_data("yahoo", ["AAPL", "GOOGL", "MSFT"], start_date, end_date, "1d")
```

### Extending Existing Data

```python
# Extend AAPL data to 2 years (only downloads the missing year)
extended_end = end_date + timedelta(days=365)
extended_data = dm.get_data("yahoo", ["AAPL"], start_date, extended_end, "1d")
```

### Checking Data Availability

```python
# Check what data you have for all assets
all_assets = get_all_asset_ranges(asset_type="Equities")

for asset_type, assets in all_assets.items():
    print(f"\n{asset_type} assets:")
    for asset in assets:
        if asset['has_data']:
            print(f"  {asset['symbol']}: {asset['data_range']['start']} to {asset['data_range']['end']}")
```

## File Structure

```
data/
├── raw/
│   ├── Crypto/
│   │   ├── BTCUSDT_1d.parquet
│   │   └── ETHUSDT_1h.parquet
│   ├── Equities/
│   │   ├── AAPL_1d.parquet
│   │   ├── GOOGL_1d.parquet
│   │   └── MSFT_1d.parquet
│   └── FX/
└── clean/
    ├── Crypto/
    ├── Equities/
    └── FX/
```

## How It Works

### 1. **Initial Data Request**
- You request data for AAPL from 2023-01-01 to 2024-01-01
- System checks if `AAPL_1d.parquet` exists
- If no file exists, downloads all data and saves

### 2. **Subsequent Requests**
- You request data for AAPL from 2023-01-01 to 2025-01-01
- System loads existing `AAPL_1d.parquet`
- Detects you need data from 2024-01-01 to 2025-01-01
- Downloads only the missing year
- Merges with existing data
- Updates the file

### 3. **Data Merging**
- Automatically handles overlapping dates
- Removes duplicates
- Maintains data continuity
- Preserves data quality

## Benefits

1. **Efficiency**: No re-downloading of existing data
2. **Storage**: Single file per asset per interval
3. **Flexibility**: Easy to extend data to new dates
4. **Transparency**: Clear visibility into what data you have
5. **Cost Savings**: Reduced API calls and bandwidth usage
6. **Time Savings**: Faster data preparation for backtesting

## Error Handling

The system gracefully handles:
- Network failures during partial downloads
- Data corruption in existing files
- API rate limits
- Invalid date ranges
- Missing data columns

## Performance Considerations

- **Parquet format**: Efficient storage and fast loading
- **Smart merging**: Prevents duplicate data
- **File existence checks**: Fast operations before expensive downloads
- **Batch operations**: Optimized for multiple symbols

## Migration from Old System

If you have existing data with date ranges in filenames:
1. The new system will work alongside old files
2. New requests will use the new naming convention
3. Consider consolidating old files to the new format

## Example Script

See `example_data_management.py` for a complete demonstration of all features.

## Future Enhancements

Potential improvements:
- Incremental daily updates
- Data compression options
- Multi-threaded downloads
- Cloud storage integration
- Data versioning and rollback
