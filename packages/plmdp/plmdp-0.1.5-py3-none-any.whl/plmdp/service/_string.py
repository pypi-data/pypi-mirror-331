from typing import cast

import polars
from plmdp.models._string import StringProfile
from plmdp.primitives import OptionalInt, OptionalNumeric


def get_string_metrics(
    dataframe: polars.DataFrame,
    column_name: str,
) -> StringProfile:
    column = dataframe[column_name]
    if column.dtype == polars.Categorical:
        column = column.cast(polars.String)

    null_count = column.null_count()

    empty_or_whitespace_count: int = cast(int, (column.str.strip_chars() == "").sum())

    string_lengths = column.str.len_chars()

    token_counts = column.str.split(by=" ").list.len()

    min_length = cast(OptionalInt, string_lengths.min())
    max_length = cast(OptionalInt, string_lengths.max())
    avg_length = cast(
        OptionalNumeric,
        string_lengths.mean() if not string_lengths.is_empty() else None,
    )
    median_length = cast(
        OptionalNumeric,
        string_lengths.median() if not string_lengths.is_empty() else None,
    )

    min_token_count = cast(OptionalNumeric, token_counts.min())
    max_token_count = cast(OptionalNumeric, token_counts.max())
    avg_token_count = cast(
        OptionalNumeric, token_counts.mean() if not token_counts.is_empty() else None
    )
    median_token_count = cast(
        OptionalNumeric, token_counts.median() if not token_counts.is_empty() else None
    )

    return StringProfile(
        nulls_count=null_count,
        min_length=min_length,
        max_length=max_length,
        avg_length=avg_length,
        median_length=median_length,
        min_token_count=min_token_count,
        max_token_count=max_token_count,
        avg_token_count=avg_token_count,
        median_token_count=median_token_count,
        empty_or_whitespace_count=empty_or_whitespace_count,
    )
