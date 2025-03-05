from enum import Enum


class SupportedDataTypes(Enum):
    NUMERIC = "NUMERIC"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    DATE_OR_DATETIME = "DATE_OR_DATETIME"
    BASE = "BASE"
