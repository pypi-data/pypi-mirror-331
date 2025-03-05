from typing import cast

import polars

from plmdp.models.date_or_datetime import DateOrDateTimeProfile
from plmdp.primitives import OptionalDateOrDateTime


def get_date_or_datetime_metrics(
    dataframe: polars.DataFrame,
    column_name: str,
) -> DateOrDateTimeProfile:
    column = dataframe[column_name]
    null_count = column.null_count()
    min_value = cast(OptionalDateOrDateTime, column.min())
    max_value = cast(OptionalDateOrDateTime, column.max())

    return DateOrDateTimeProfile(nulls_count=null_count, min=min_value, max=max_value)
