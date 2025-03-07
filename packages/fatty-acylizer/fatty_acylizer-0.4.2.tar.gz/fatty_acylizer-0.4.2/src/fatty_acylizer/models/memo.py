import typing
from collections import defaultdict

if typing.TYPE_CHECKING:
    from _typeshed import SupportsRichComparison  # noqa F401

from fatty_acylizer.util.feature import BasicNumber
from fatty_acylizer.util.model import Result


class Model:
    def __init__(self, fatty_acids: list[BasicNumber], n_fa_per_lipid: int):
        """fatty acids needs to be sorted."""
        self.jac = False
        self.n_fa_per_lipid = n_fa_per_lipid
        self.fatty_acids = fatty_acids
        self.table: list[dict] = []

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        params = ', '.join([f'{key}={value}' for key, value in self.settings.items()])
        return f'{cls_name}({params})'

    @property
    def settings(self):
        return {
            'jac': self.jac,
            'n_fa_per_lipid': self.n_fa_per_lipid,
            'fatty_acids': self.fatty_acids,
        }

    def __call__(self, fa_profile: dict[BasicNumber, float]) -> Result:
        if any(key not in self.fatty_acids for key in fa_profile):
            raise ValueError(fa_profile)
        self._initialize(fa_profile)
        for _ in range(self.n_fa_per_lipid - 1):
            self._propagate_to_next()
        return Result(profile=self.table[-1], gradient=None)

    def _initialize(self, fa_profile: dict[BasicNumber, float]) -> None:
        """Initialize self.table with zero containing arrays"""
        self.table = [fa_profile]

    def _propagate_to_next(self) -> None:
        n = len(self.table)
        new_row = defaultdict(lambda: 0)
        for def_val, def_prob in self.table[0].items():
            for pre_val, pre_prob in self.table[n - 1].items():
                new_row[pre_val + def_val] += pre_prob * def_prob
        self.table.append(dict(new_row))


if __name__ == '__main__':
    import pathlib

    with open(
        pathlib.Path('/home/janik/Documents/projects/predictor/data/fatty_acids.csv')
    ) as f:
        lines = (line.strip().split(',') for line in f)
        fatty_acids = [complex(real=int(real), imag=int(imag)) for real, imag in lines]

    model = Model(fatty_acids=fatty_acids, n_fa_per_lipid=3)
