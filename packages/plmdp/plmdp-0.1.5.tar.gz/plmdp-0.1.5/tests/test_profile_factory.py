from typing import Callable

import pytest
from polars import DataType

from plmdp.enums import SupportedDataTypes
from plmdp.exceptions import UnsupportedDataTypeException
from plmdp.models import BaseProfile
from plmdp.metrics_handler_factory import MetricsHandlerFactory
from plmdp.service import (
    get_numeric_metrics,
    get_string_metrics,
    get_type_agnostic_metrics,
    get_date_or_datetime_metrics,
)
import polars
from polars.datatypes import (
    Decimal,
    Float32,
    Int8,
    String,
    Date,
    Datetime,
    Boolean,
)


@pytest.fixture
def metrics_handler() -> MetricsHandlerFactory:
    return MetricsHandlerFactory()


@pytest.mark.parametrize(
    "data_type, expected_profile_type",
    [
        (Float32, SupportedDataTypes.NUMERIC),
        (Int8, SupportedDataTypes.NUMERIC),
        (Decimal, SupportedDataTypes.NUMERIC),
        (String, SupportedDataTypes.STRING),
        (Date, SupportedDataTypes.DATE_OR_DATETIME),
        (Datetime, SupportedDataTypes.DATE_OR_DATETIME),
    ],
)
def test_get_profile_type(
    metrics_handler: MetricsHandlerFactory,
    data_type: DataType,
    expected_profile_type: SupportedDataTypes,
) -> None:
    assert metrics_handler.get_profile_type(data_type) == expected_profile_type


def test_get_profile_type_unsupported(metrics_handler: MetricsHandlerFactory) -> None:
    with pytest.raises(UnsupportedDataTypeException):
        metrics_handler.get_profile_type(str())


@pytest.mark.parametrize(
    "data_type, expected_handler",
    [
        (Float32, get_numeric_metrics),
        (Int8, get_numeric_metrics),
        (String, get_string_metrics),
        (Date, get_date_or_datetime_metrics),
        (Datetime, get_date_or_datetime_metrics),
    ],
)
def test_create(
    metrics_handler: MetricsHandlerFactory,
    data_type: DataType,
    expected_handler: Callable[[polars.DataFrame, str], BaseProfile],
) -> None:
    handler = metrics_handler.create(data_type)
    assert handler == expected_handler


def test_create_fallback(metrics_handler: MetricsHandlerFactory) -> None:
    handler = metrics_handler.create(Boolean())
    assert handler == get_type_agnostic_metrics
