from datetime import date, datetime
from decimal import Decimal

OptionalNumeric = int | float | None | Decimal
OptionalInt = int | None
OptionalDateOrDateTime = date | datetime | None
ColumnName = str
