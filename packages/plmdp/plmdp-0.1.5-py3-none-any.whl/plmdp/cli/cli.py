import argparse
from pathlib import Path

from plmdp.cli.formatter import FormatterFactory
from plmdp.cli.data_loader import DataReaderFactory
from plmdp.cli.input_utils import load_schema_from_cli, load_kwargs
from plmdp.models.output import ProfilerOutput
from plmdp.profiler import Profiler


def main() -> str:
    parser = argparse.ArgumentParser(description="Profiler cli")

    parser.add_argument("-p", "--path", required=True, help="Path to datafile")

    parser.add_argument(
        "-s", "--schema", required=False, help="Dataframe schema as json"
    )

    parser.add_argument(
        "-k", "--kwargs", required=False, help="Polars dataframe loader kwargs"
    )

    parser.add_argument(
        "-c", "--columns-to-ignore", required=False, help="Column names to ignore"
    )

    parser.add_argument(
        "-f",
        "--formatter",
        required=False,
        default="json",
        choices=["yaml", "json"],
        help="Stdout format: json or yaml",
    )
    args = parser.parse_args()
    str_schema = args.schema
    path = Path(args.path)
    dataloader_kwargs = args.kwargs
    columns_to_ignore = (
        args.columns_to_ignore.split(",") if args.columns_to_ignore else []
    )

    schema = load_schema_from_cli(str_schema)
    kwargs = load_kwargs(dataloader_kwargs)
    stdout_format = args.formatter

    read_data = DataReaderFactory.create(path)
    data = read_data(source=path, schema=schema, **kwargs)
    results: ProfilerOutput = Profiler().run_profiling(
        data, columns_to_ignore=columns_to_ignore
    )
    formatter = FormatterFactory.get_formatter(stdout_format)
    return formatter(results)


if __name__ == "__main__":
    print(main())
