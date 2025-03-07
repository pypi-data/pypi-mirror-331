import itertools as it
import math
from collections import defaultdict

from fatty_acylizer.util.combinatorics import calculate_number_of_permutations
from fatty_acylizer.util.model import Profile
from fatty_acylizer.util.model import Result


class Model:
    def __init__(self, n_fa_per_lipid):
        self.n_fa_per_lipid = n_fa_per_lipid
        self.jac = False
        self.fatty_acids = None

    @property
    def settings(self):
        return {
            'jac': self.jac,
            'n_fa_per_lipid': self.n_fa_per_lipid,
            'fatty_acids': self.fatty_acids,
        }

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        params = ', '.join([f'{key}={value}' for key, value in self.settings.items()])
        return f'{cls_name}({params})'

    def __call__(self, fa_profile: Profile) -> Result:
        self.fatty_acids = list(fa_profile.keys())
        space = defaultdict(float)
        for combination in it.combinations_with_replacement(
            fa_profile, r=self.n_fa_per_lipid
        ):
            sum_feature = sum(combination)
            k_possible_permutations = calculate_number_of_permutations(combination)
            probability = (
                math.prod(fa_profile[item] for item in combination)
                * k_possible_permutations
            )
            space[sum_feature] += probability
        return Result(profile=dict(space), gradient=None)
