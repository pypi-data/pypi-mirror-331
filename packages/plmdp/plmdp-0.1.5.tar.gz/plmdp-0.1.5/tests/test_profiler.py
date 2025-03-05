import datetime

from freezegun import freeze_time
from polars import String, Date, Float32, read_csv
import pytest

from plmdp.models import DateOrDateTimeProfile, NumericProfile
from plmdp.models.output import ProfilerOutput, ColumnData
from plmdp.profiler import Profiler
from tests.constants import TESTS_RESOURCES


@pytest.fixture
@freeze_time("2000-01-01")
def profiler_output() -> ProfilerOutput:
    return ProfilerOutput(
        rows_count=20,
        column_count=3,
        ignored_columns=["comment"],
        dataframe_size=545,
        columns=[
            ColumnData(
                name="dob",
                type="Date",
                metrics=DateOrDateTimeProfile(
                    nulls_count=0,
                    min=datetime.date(1973, 9, 19),
                    max=datetime.date(1999, 8, 29),
                ),
            ),
            ColumnData(
                name="sales",
                type="Float32",
                metrics=NumericProfile(
                    nulls_count=0,
                    mean=181.5,
                    median=185.0,
                    std=78.42,
                    min=50.0,
                    max=320.0,
                    percentile25=120.0,
                    percentile50=190.0,
                    percentile75=230.0,
                ),
            ),
        ],
    )


@freeze_time("2000-01-01")
def test_profiler(profiler_output: ProfilerOutput) -> None:
    df = read_csv(
        (TESTS_RESOURCES / "data.csv"),
        schema={"comment": String, "dob": Date, "sales": Float32},
    )

    result = Profiler().run_profiling(
        df,
        columns_to_ignore=[
            "comment",
        ],
    )

    assert result == profiler_output
