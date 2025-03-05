from decimal import Decimal
from typing import cast

import polars

from plmdp.constants import FLOATING_POINT
from plmdp.models.numeric import NumericProfile
from plmdp.primitives import OptionalNumeric


def safe_round(value: OptionalNumeric, precision: int) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        value = float(value)
    return round(value, precision)


def get_numeric_metrics(
    dataframe: polars.DataFrame,
    column_name: str,
) -> NumericProfile:
    column = dataframe[column_name]
    null_count = column.null_count()
    mean = cast(OptionalNumeric, column.mean())
    median = cast(OptionalNumeric, column.median())
    std = cast(OptionalNumeric, column.std())
    min_value = cast(OptionalNumeric, column.min())
    max_value = cast(OptionalNumeric, column.max())

    percentile25 = cast(OptionalNumeric, column.quantile(0.25))
    percentile50 = cast(OptionalNumeric, column.quantile(0.50))
    percentile75 = cast(OptionalNumeric, column.quantile(0.75))

    return NumericProfile(
        nulls_count=null_count,
        mean=safe_round(mean, FLOATING_POINT),
        median=safe_round(median, FLOATING_POINT),
        std=safe_round(std, FLOATING_POINT),
        min=safe_round(min_value, FLOATING_POINT),
        max=safe_round(max_value, FLOATING_POINT),
        percentile25=safe_round(percentile25, FLOATING_POINT),
        percentile50=safe_round(percentile50, FLOATING_POINT),
        percentile75=safe_round(percentile75, FLOATING_POINT),
    )
