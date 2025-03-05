import polars
from typing import Callable

from plmdp.exceptions import EmptyDataFrameException, NoColumnsToProfile
from plmdp.models.output import ProfilerOutput, ColumnData
from plmdp.metrics_handler_factory import MetricsHandlerFactory
from plmdp.models import BaseProfile

import logging

logger = logging.getLogger(__name__)


class Profiler:
    def __init__(
        self,
        profile_factory: MetricsHandlerFactory | None = None,
    ):
        self._profile_factory = (
            profile_factory if profile_factory else MetricsHandlerFactory()
        )

    def _get_handler(
        self,
        data_type: polars.datatypes.DataType,
    ) -> Callable[[polars.DataFrame, str], BaseProfile]:
        return self._profile_factory.create(data_type)

    @staticmethod
    def _validate_row_count_not_zero(
        dataframe: polars.DataFrame,
    ) -> None:
        if dataframe.shape[0] == 0:
            msg = "Passed dataframe is empty."
            logger.error(msg)
            raise EmptyDataFrameException(msg)

    @staticmethod
    def _validate_columns_to_profile(
        dataframe: polars.DataFrame,
        columns_to_ignore: list[str],
    ) -> None:
        dataframe_columns = set(dataframe.columns)
        ignored_columns = set(columns_to_ignore)

        if dataframe_columns.issubset(ignored_columns):
            msg = "All columns are ignored, no columns left to profile."
            logger.error(msg)
            raise NoColumnsToProfile(msg)

        extra_ignored_columns = ignored_columns - dataframe_columns
        if extra_ignored_columns:
            logger.warning(
                f"Warning: The following columns in 'columns_to_ignore' are not in the DataFrame: {extra_ignored_columns}"
            )

    def _gather_columns_metrics(
        self,
        dataframe: polars.DataFrame,
        columns_to_ignore: list[str],
    ) -> list[ColumnData]:
        column_name: str
        data_type: polars.datatypes.DataType

        column_metrics = []
        for column_name, data_type in dataframe.schema.items():
            if column_name in columns_to_ignore:
                continue

            handler: Callable[[polars.DataFrame, str], BaseProfile] = self._get_handler(
                data_type
            )

            column_metrics.append(
                ColumnData(
                    name=column_name,
                    type=str(data_type),
                    metrics=handler(dataframe, column_name),
                )
            )

        return column_metrics

    def run_profiling(
        self,
        dataframe: polars.DataFrame,
        columns_to_ignore: list[str] | None = None,
    ) -> ProfilerOutput:
        _columns_to_ignore: list[str] = columns_to_ignore if columns_to_ignore else []

        self._validate_row_count_not_zero(dataframe)
        self._validate_columns_to_profile(dataframe, _columns_to_ignore)

        columns_data = self._gather_columns_metrics(dataframe, _columns_to_ignore)
        rows_count, column_count = dataframe.shape
        results = ProfilerOutput(
            rows_count=rows_count,
            column_count=column_count,
            ignored_columns=_columns_to_ignore,
            dataframe_size=dataframe.estimated_size(),
            columns=columns_data,
        )
        return results
