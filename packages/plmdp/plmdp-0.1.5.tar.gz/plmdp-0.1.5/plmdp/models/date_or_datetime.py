import dataclasses

from plmdp.models.type_agnostic import BaseProfile
from plmdp.primitives import OptionalDateOrDateTime


@dataclasses.dataclass
class DateOrDateTimeProfile(BaseProfile):
    min: OptionalDateOrDateTime
    max: OptionalDateOrDateTime
