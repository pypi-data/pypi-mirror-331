import functools as fn
import math
from collections import Counter
from collections.abc import Iterable


def calculate_number_of_permutations(collection: Iterable) -> int:
    count = Counter(collection)
    n_permutations = factorial(sum(count.values())) / math.prod(
        factorial(rep) for rep in count.values()
    )
    if n_permutations.is_integer():
        return int(n_permutations)
    raise ValueError(f'{n_permutations} is not an integer')


factorial = fn.lru_cache(math.factorial)
