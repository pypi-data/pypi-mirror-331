# Polars minimal data profiler

## Overview

The `pldmp` package provides an easy way to perform data profiling using the Polars library. It
analyzes datasets to generate various statistical summaries and insights, helping users understand the structure and
quality of their data.

## Features

- Supports a variety of data types, including numeric, string, and datetime.
- Computes key statistical metrics such as mean, median, standard deviation, and percentiles.
- Detects missing values, empty fields, and string token distributions.
- Provides both a Python and a command-line interface (CLI) for easy usage.

## Installation

```bash
pip install plmdp
```

## Usage

### Python Example

```python
from pathlib import Path
from pprint import pprint
import polars as pl
from plmdp import Profiler

if __name__ == "__main__":
    datafile_path = Path(__file__).resolve().parent / "data.csv"
    data: pl.DataFrame = pl.read_csv(datafile_path, separator=";")
    results = Profiler().run_profiling(data)
    pprint(results)
```
#### Example output
```python
ProfilerOutput(rows_count=20,
               column_count=3,
               ignored_columns=[],
               dataframe_size=745,
               columns=[ColumnData(name='comment',
                                   type='String',
                                   metrics=StringProfile(nulls_count=0,
                                                         min_length=14,
                                                         max_length=27,
                                                         avg_length=19.25,
                                                         median_length=19.0,
                                                         min_token_count=2,
                                                         max_token_count=4,
                                                         avg_token_count=2.35,
                                                         median_token_count=2.0,
                                                         empty_or_whitespace_count=0)),
                        ColumnData(name='dob',
                                   type='String',
                                   metrics=StringProfile(nulls_count=0,
                                                         min_length=10,
                                                         max_length=10,
                                                         avg_length=10.0,
                                                         median_length=10.0,
                                                         min_token_count=1,
                                                         max_token_count=1,
                                                         avg_token_count=1.0,
                                                         median_token_count=1.0,
                                                         empty_or_whitespace_count=0)),
                        ColumnData(name='sales',
                                   type='Int64',
                                   metrics=NumericProfile(nulls_count=0,
                                                          mean=181.5,
                                                          median=185.0,
                                                          std=78.42,
                                                          min=50,
                                                          max=320,
                                                          percentile25=120.0,
                                                          percentile50=190.0,
                                                          percentile75=230.0))],
               created_at=datetime.datetime(2025, 2, 18, 14, 6, 29, 574191, tzinfo=datetime.timezone.utc))
```

### CLI Example

```bash
#!/bin/bash

DATA_PATH="$(pwd)/data.csv"
SCHEMA='{"comment": "String", "dob": "Date", "sales": "Float32"}'
LOADER_KWARGS='{"separator":";"}'
FORMATTER='json'

plmdp --path "$DATA_PATH" --schema="$SCHEMA" --kwargs="$LOADER_KWARGS" --formatter="$FORMATTER"
```

#### Example output

```json
{
  "rows_count": 20,
  "column_count": 3,
  "ignored_columns": [],
  "dataframe_size": 545,
  "columns": [
    {
      "name": "comment",
      "type": "String",
      "metrics": {
        "nulls_count": 0,
        "min_length": 14,
        "max_length": 27,
        "avg_length": 19.25,
        "median_length": 19.0,
        "min_token_count": 2,
        "max_token_count": 4,
        "avg_token_count": 2.35,
        "median_token_count": 2.0,
        "empty_or_whitespace_count": 0
      }
    },
    {
      "name": "dob",
      "type": "Date",
      "metrics": {
        "nulls_count": 0,
        "min": "1973-09-19",
        "max": "1999-08-29"
      }
    },
    {
      "name": "sales",
      "type": "Float32",
      "metrics": {
        "nulls_count": 0,
        "mean": 181.5,
        "median": 185.0,
        "std": 78.42,
        "min": 50.0,
        "max": 320.0,
        "percentile25": 120.0,
        "percentile50": 190.0,
        "percentile75": 230.0
      }
    }
  ],
  "created_at": "2025-02-18 14:07:23.736730+00:00"
}

```

## Supported Data Types

The package supports the following Polars data types:

- Numeric: `Float32`, `Float64`, `Int8`, `Int16`, `Int32`, `Int64`, `Int128`, `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Decimal`
- String: `String`, `Categorical`
- Date/Time: `Date`, `Datetime`
- Others: `Boolean`

## Metrics Computed

- **String Profile**: Minimum/maximum/average string length, token counts, empty or whitespace count.
- **Numeric Profile**: Mean, median, standard deviation, min/max values, and percentiles.
- **Date/Datetime Profile**: Minimum and maximum values.
- **Base Profile**: Null values count.
