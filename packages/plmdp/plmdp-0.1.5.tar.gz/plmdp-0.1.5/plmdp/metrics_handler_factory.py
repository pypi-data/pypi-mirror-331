from functools import lru_cache
from typing import Callable

import polars
from polars import DataType

from plmdp.enums import SupportedDataTypes
from plmdp.exceptions import UnsupportedDataTypeException

from plmdp.models.type_agnostic import BaseProfile
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

from plmdp.service import (
    get_numeric_metrics,
    get_string_metrics,
    get_type_agnostic_metrics,
    get_date_or_datetime_metrics,
)


class MetricsHandlerFactory:
    TYPE_MAPPING: dict[SupportedDataTypes, list[type[DataType]]] = {
        SupportedDataTypes.NUMERIC: [
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
        ],
        SupportedDataTypes.STRING: [String, Categorical],
        SupportedDataTypes.DATE_OR_DATETIME: [Date, Datetime],
    }
    HANDLER_MAPPING: dict[
        SupportedDataTypes, Callable[[polars.DataFrame, str], BaseProfile]
    ] = {
        SupportedDataTypes.NUMERIC: get_numeric_metrics,
        SupportedDataTypes.STRING: get_string_metrics,
        SupportedDataTypes.DATE_OR_DATETIME: get_date_or_datetime_metrics,
        SupportedDataTypes.BASE: get_type_agnostic_metrics,
    }
    FALLBACK_TYPE = SupportedDataTypes.BASE

    @lru_cache
    def get_profile_type(self, _type: DataType) -> SupportedDataTypes:
        for simplified_type, polar_types in self.TYPE_MAPPING.items():
            if _type in polar_types:
                return simplified_type
        if isinstance(_type, DataType):
            return self.FALLBACK_TYPE
        raise UnsupportedDataTypeException(f"Unsupported datatype {_type}")

    def create(
        self, data_type: DataType
    ) -> Callable[[polars.DataFrame, str], BaseProfile]:
        profile_type: SupportedDataTypes = self.get_profile_type(data_type)
        return self.HANDLER_MAPPING[profile_type]
