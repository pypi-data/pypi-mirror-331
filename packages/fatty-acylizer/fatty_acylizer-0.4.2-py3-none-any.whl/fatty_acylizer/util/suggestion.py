import itertools
from collections import defaultdict


def split(n: int, parts: int, force_even: bool = True) -> list[int]:
    """Splits up the number n into parts."""
    avg = n // parts
    rem = int(n % parts)
    if not force_even:
        return [avg] * (parts - rem) + [avg + 1] * rem

    if rem:
        sub = int(avg - avg % 2)
        return [
            sub,
            *split(
                n - sub,
                parts - 1,
                force_even=force_even,
            ),
        ]

    half = (parts - rem) // 2
    final_rem = int((parts - rem) % 2)
    return [avg - avg % 2] * half + [avg] * final_rem + [avg + avg % 2] * half


def suggest_start_conditions(
    lipid_profile: dict[complex, float],
    n_fa_per_lipid: int,
    fatty_acids: list[complex],
    prefer_even_chains: bool = True,
) -> dict[complex, float]:
    fa_profile: dict[complex, float] = defaultdict(float)
    for lipid, probability in lipid_profile.items():
        if not lipid.imag.is_integer() or not lipid.real.is_integer():
            raise ValueError(
                f'{lipid} may only contain integer values for real and imaginary parts'
            )
        cc = split(
            n=int(lipid.real), parts=n_fa_per_lipid, force_even=prefer_even_chains
        )
        db = split(n=int(lipid.imag), parts=n_fa_per_lipid, force_even=False)
        for real, imag in itertools.product(cc, db):
            fatty_acid = complex(real, imag)
            fa_profile[fatty_acid] += probability

    fa_set = set(fatty_acids)
    fa_profile = {lipid: prob for lipid, prob in fa_profile.items() if lipid in fa_set}

    total = sum(fa_profile.values())
    return {fatty_acid: prob / total for fatty_acid, prob in fa_profile.items()}
