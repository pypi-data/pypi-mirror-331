import dataclasses
from datetime import datetime, timezone

from plmdp.models import BaseProfile


@dataclasses.dataclass
class ColumnData:
    name: str
    type: str
    metrics: BaseProfile


@dataclasses.dataclass
class ProfilerOutput:
    rows_count: int
    column_count: int
    ignored_columns: list[str]
    dataframe_size: int | float
    columns: list[ColumnData]
    created_at: datetime = dataclasses.field(
        default_factory=lambda: datetime.now(timezone.utc), init=False
    )
