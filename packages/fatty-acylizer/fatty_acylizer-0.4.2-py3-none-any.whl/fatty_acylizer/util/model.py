from typing import Any
from typing import NamedTuple
from typing import Protocol

from fatty_acylizer.util.feature import BasicNumber


Profile = dict[BasicNumber, float]


class Result(NamedTuple):
    profile: Profile
    gradient: list[Profile] | None


class Model(Protocol):
    jac: bool
    n_fa_per_lipid: int
    fatty_acids: list[BasicNumber]
    settings: dict[str, Any]

    def __call__(self, fa_profile: Profile) -> Result: ...
