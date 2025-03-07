from fatty_acylizer.models.gradient.model import DiffCounter


def test_counting():
    counter = DiffCounter(list('aaab'))
    assert counter['a'] == 3


def test_factor():
    counter = DiffCounter(list('aaab'))
    assert counter.factor == 1


def test_npermutations():
    counter = DiffCounter(list('aaab'))
    assert counter.n_permutations == 4


def test_differentiation_to_a():
    counter = DiffCounter(list('aaab'))
    expected = DiffCounter(list('aab'))
    expected.factor = 3
    assert counter.differentiate('a') == expected


def test_differentiation_to_b():
    counter = DiffCounter(list('aaab'))
    expected = DiffCounter(list('aaa'))
    assert counter.differentiate('b') == expected


def test_differentiation_to_c():
    counter = DiffCounter(list('aaab'))
    assert counter.differentiate('c') is None
