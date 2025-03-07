from dataclasses import dataclass
from dataclasses import field
from typing import Protocol
from typing import Self


class BasicNumber(Protocol):
    def __add__(self, other: Self, /) -> Self: ...

    def __radd__(self, other: Self, /) -> Self: ...

    def __sub__(self, other: Self, /) -> Self: ...


@dataclass(slots=True)
class Feature:
    carbon_chain_length: int
    double_bond_count: int
    labeled_carbons: int = field(default=0)

    def __add__(self, other: Self) -> Self:
        return self.__class__(
            carbon_chain_length=self.carbon_chain_length + other.carbon_chain_length,
            double_bond_count=self.double_bond_count + other.double_bond_count,
            labeled_carbons=self.labeled_carbons + other.labeled_carbons,
        )

    def __radd__(self, other: Self) -> Self:
        if other == 0:
            # for use with sum(...)
            return self
        return self + other

    def __neg__(self) -> Self:
        return self.__class__(
            carbon_chain_length=-self.carbon_chain_length,
            double_bond_count=-self.double_bond_count,
            labeled_carbons=-self.labeled_carbons,
        )

    def __sub__(self, other: Self) -> Self:
        return self.__class__(
            carbon_chain_length=self.carbon_chain_length - other.carbon_chain_length,
            double_bond_count=self.double_bond_count - other.double_bond_count,
            labeled_carbons=self.labeled_carbons - other.labeled_carbons,
        )


if __name__ == '__main__':
    number: BasicNumber = 1 + 2j
    number2: BasicNumber = Feature(1, 2, 1)
    del number
    del number2
