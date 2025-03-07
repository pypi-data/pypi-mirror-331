import collections
import itertools as it
import math
import typing
from collections import defaultdict

from fatty_acylizer.util.combinatorics import calculate_number_of_permutations
from fatty_acylizer.util.feature import BasicNumber
from fatty_acylizer.util.model import Profile
from fatty_acylizer.util.model import Result


class DiffCounter(collections.Counter):
    def __init__(self, *args, factor: int = 1, n_permutations: int = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.factor = factor
        if not n_permutations:
            n_permutations = calculate_number_of_permutations(self)
        self.n_permutations = n_permutations

    def differentiate(self, with_respect_to: BasicNumber) -> typing.Self:
        copy = self.copy()
        factor = copy[with_respect_to]
        if factor == 0:
            return None
        elif factor == 1:
            copy.pop(with_respect_to)
        else:
            copy[with_respect_to] -= 1
        copy.factor *= factor
        return copy


Space = dict[BasicNumber, list[DiffCounter]]


class Model:
    def __init__(self, fatty_acids: list[BasicNumber], n_fa_per_lipid: int):
        self.jac = True
        self.n_fa_per_lipid = n_fa_per_lipid
        lipid_space = defaultdict(list)
        for combination in it.combinations_with_replacement(
            fatty_acids, r=n_fa_per_lipid
        ):
            sum_feature = sum(combination)
            lipid_space[sum_feature].append(DiffCounter(combination))
        self.lipid_space: Space = dict(lipid_space)

        self.gradient: list[Space] = []
        for fatty_acid in fatty_acids:
            diff_space = {}
            for lipid, combinations in lipid_space.items():
                diffs = (
                    comb.differentiate(with_respect_to=fatty_acid)
                    for comb in combinations
                )
                diff_space[lipid] = [comb for comb in diffs if comb is not None]
            self.gradient.append(diff_space)

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

    def compute_profile_gradient(self, fa_profile: Profile) -> Result:
        lipid_space = compute_space(self.lipid_space, fa_profile)
        gradient = [compute_space(g, fa_profile) for g in self.gradient]
        return Result(lipid_space, gradient)

    def __call__(self, fa_profile: Profile) -> Result:
        return self.compute_profile_gradient(fa_profile=fa_profile)


def compute_space(
    lipid_space: Space,
    fa_profile: Profile,
) -> Profile:
    prob_space = {}
    for key, combinations in lipid_space.items():
        probability = 0
        for comb in combinations:
            try:
                prob = math.prod(
                    fa_profile[key] ** times for key, times in comb.items()
                )
            except KeyError:
                # prob = 0
                pass
            else:
                weighted_prob = prob * comb.factor * comb.n_permutations
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
