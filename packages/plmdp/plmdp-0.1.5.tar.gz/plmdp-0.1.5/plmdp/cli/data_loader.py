from pathlib import Path
from typing import Callable

import polars.datatypes
from polars.datatypes import (
    Decimal,
    Float32,
    Float64,
    Int8,
    Int16,
    Int32,
    Int64,
    Int128,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    String,
    Categorical,
    Date,
    Datetime,
)

from plmdp.exceptions import UnsupportedDataTypeException, UnsupportedDataFileExtension

STR_TO_POLARS_TYPE = {
    "Decimal": Decimal,
    "Float32": Float32,
    "Float64": Float64,
    "Int8": Int8,
    "Int16": Int16,
    "Int32": Int32,
    "Int64": Int64,
    "Int128": Int128,
    "UInt8": UInt8,
    "UInt16": UInt16,
    "UInt32": UInt32,
    "UInt64": UInt64,
    "String": String,
    "Categorical": Categorical,
    "Date": Date,
    "Datetime": Datetime,
}


def str_type_to_polars(str_type: str) -> polars.datatypes.DataTypeClass:
    try:
        return STR_TO_POLARS_TYPE[str_type]
    except KeyError as e:
        raise UnsupportedDataTypeException(f"Unsupported datatype {str_type}") from e


class DataReaderFactory:
    @staticmethod
    def create(path: Path) -> Callable[..., polars.DataFrame]:
        file_extension = path.suffix

        readers: dict[str, Callable[..., polars.DataFrame]] = {
            ".csv": polars.read_csv,
            ".parquet": polars.read_parquet,
        }

        try:
            reader = readers[file_extension]
        except KeyError as e:
            raise UnsupportedDataFileExtension(
                "Supported file extensions are: '.csv' and '.parquet'"
            ) from e

        return reader
