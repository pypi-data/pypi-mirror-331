import itertools as it
import math
import typing
from collections import defaultdict

from fatty_acylizer.util.combinatorics import calculate_number_of_permutations
from fatty_acylizer.util.feature import BasicNumber
from fatty_acylizer.util.model import Profile
from fatty_acylizer.util.model import Result


class Combination(typing.NamedTuple):
    combination: list[BasicNumber]
    n_permutations: int


Space = dict[BasicNumber, list[Combination]]


class Model:
    def __init__(self, fatty_acids: list[BasicNumber], n_fa_per_lipid: int):
        self.jac = False
        self.n_fa_per_lipid = n_fa_per_lipid
        self.fatty_acids = fatty_acids
        lipid_space = defaultdict(list)
        for combination in it.combinations_with_replacement(
            fatty_acids, r=n_fa_per_lipid
        ):
            sum_feature = sum(combination)
            k_possible_permutations = calculate_number_of_permutations(combination)
            lipid_space[sum_feature].append(
                Combination(
                    combination=combination, n_permutations=k_possible_permutations
                )
            )
        self.lipid_space: Space = dict(lipid_space)

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

    def compute_profile(self, fa_profile: Profile) -> Result:
        lipid_space = compute_space(self.lipid_space, fa_profile)
        return Result(lipid_space, None)

    def __call__(self, fa_profile: Profile) -> Result:
        return self.compute_profile(fa_profile=fa_profile)


def compute_space(
    lipid_space: Space,
    fa_profile: Profile,
) -> Profile:
    prob_space = {}
    for key, combinations in lipid_space.items():
        probability = 0
        for comb in combinations:
            try:
                prob = math.prod(fa_profile[key] for key in comb.combination)
            except KeyError:
                # prob = 0
                pass
            else:
                weighted_prob = prob * comb.n_permutations
                probability += weighted_prob
        prob_space[key] = probability
    return prob_space


if __name__ == '__main__':
    import pathlib

    with open(
        pathlib.Path(__file__).parent.parent.parent / 'data/fatty_acids.csv'
    ) as f:
        lines = (line.strip().split(',') for line in f)
        fatty_acids = [complex(real=int(real), imag=int(imag)) for real, imag in lines]

    model = Model(fatty_acids=fatty_acids, n_fa_per_lipid=3)
