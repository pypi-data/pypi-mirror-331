import polars

from plmdp.models.type_agnostic import BaseProfile


def get_type_agnostic_metrics(
    dataframe: polars.DataFrame,
    column_name: str,
) -> BaseProfile:
    column = dataframe[column_name]
    null_count = column.null_count()

    return BaseProfile(
        nulls_count=null_count,
    )
