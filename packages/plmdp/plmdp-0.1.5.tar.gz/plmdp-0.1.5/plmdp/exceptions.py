class UnsupportedDataTypeException(Exception):
    """Handles unsupported column data type."""


class EmptyDataFrameException(Exception):
    """Handles empty dataframe passed to profiling."""


class NoColumnsToProfile(Exception):
    """Handles situations when all dataframe's columns are ignored."""


class UnsupportedDataFileExtension(Exception):
    """Handles file extensions that differ from csv and parquet."""
