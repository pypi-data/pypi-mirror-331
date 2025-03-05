import json
from typing import Any, cast

import polars.datatypes

from plmdp.exceptions import UnsupportedDataTypeException
from plmdp.cli.data_loader import str_type_to_polars
from plmdp.primitives import ColumnName


def load_schema_from_cli(
    schema: str | None,
) -> dict[ColumnName, polars.datatypes.DataTypeClass] | None:
    if not schema:
        return None
    try:
        json_input = json.loads(schema)
        return {k: str_type_to_polars(v) for k, v in json_input.items()}

    except json.JSONDecodeError as e:
        raise ValueError("Schema is not valid json") from e

    except UnsupportedDataTypeException:
        raise


def load_kwargs(kwargs_str: str | None) -> dict[Any, Any]:
    if not kwargs_str:
        return {}
    try:
        return cast(dict[Any, Any], json.loads(kwargs_str))
    except json.JSONDecodeError as e:
        raise ValueError("Kwargs are invalid json") from e
