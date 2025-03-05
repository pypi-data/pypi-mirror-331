import dataclasses


from plmdp.models.type_agnostic import BaseProfile
from plmdp.primitives import OptionalInt, OptionalNumeric


@dataclasses.dataclass
class StringProfile(BaseProfile):
    min_length: OptionalInt
    max_length: OptionalInt
    avg_length: OptionalNumeric
    median_length: OptionalNumeric

    min_token_count: OptionalNumeric
    max_token_count: OptionalNumeric
    avg_token_count: OptionalNumeric
    median_token_count: OptionalNumeric

    empty_or_whitespace_count: OptionalInt
