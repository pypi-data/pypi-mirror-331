import dataclasses

from plmdp.models.type_agnostic import BaseProfile
from plmdp.primitives import OptionalNumeric


@dataclasses.dataclass
class NumericProfile(BaseProfile):
    mean: OptionalNumeric
    median: OptionalNumeric
    std: OptionalNumeric
    min: OptionalNumeric
    max: OptionalNumeric

    percentile25: OptionalNumeric
    percentile50: OptionalNumeric
    percentile75: OptionalNumeric
