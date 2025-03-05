import polars
import pytest
from _pytest.logging import LogCaptureFixture

from plmdp.exceptions import EmptyDataFrameException, NoColumnsToProfile
from plmdp.profiler import Profiler


@pytest.fixture
def profiler() -> Profiler:
    return Profiler()


@pytest.fixture
def sample_dataframe() -> polars.DataFrame:
    return polars.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})


def test_validate_row_count_not_zero_passes_on_non_empty_dataframe(
    profiler: Profiler,
) -> None:
    non_empty_df = polars.DataFrame({"column": [1, 2, 3]})
    profiler._validate_row_count_not_zero(non_empty_df)


def test_validate_row_count_not_zero_raises_exception_on_empty_dataframe(
    caplog: LogCaptureFixture,
    profiler: Profiler,
) -> None:
    empty_df = polars.DataFrame()
    with pytest.raises(EmptyDataFrameException, match="Passed dataframe is empty."):
        profiler._validate_row_count_not_zero(empty_df)

    assert "Passed dataframe is empty." in caplog.text


def test_all_columns_ignored(
    sample_dataframe: polars.DataFrame,
    profiler: Profiler,
) -> None:
    columns_to_ignore = ["a", "b", "c"]

    with pytest.raises(NoColumnsToProfile, match="All columns are ignored"):
        profiler._validate_columns_to_profile(sample_dataframe, columns_to_ignore)


def test_some_columns_ignored(
    sample_dataframe: polars.DataFrame,
    profiler: Profiler,
) -> None:
    columns_to_ignore = ["a"]

    profiler._validate_columns_to_profile(sample_dataframe, columns_to_ignore)


def test_no_columns_ignored(
    sample_dataframe: polars.DataFrame,
    profiler: Profiler,
) -> None:
    columns_to_ignore: list[str] = []

    profiler._validate_columns_to_profile(sample_dataframe, columns_to_ignore)


def test_extra_ignored_columns(
    sample_dataframe: polars.DataFrame,
    caplog: LogCaptureFixture,
    profiler: Profiler,
) -> None:
    columns_to_ignore = ["a", "d"]

    profiler._validate_columns_to_profile(sample_dataframe, columns_to_ignore)

    assert (
        "Warning: The following columns in 'columns_to_ignore' are not in the DataFrame: {'d'}"
        in caplog.text
    )
