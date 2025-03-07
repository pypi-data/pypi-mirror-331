from typing import Any

from fatty_acylizer.util.optimization import Callback
from scipy.optimize import OptimizeResult
from sklearn.feature_extraction import DictVectorizer


def debug_serializer(
    result: OptimizeResult,
    history: list[Callback],
    settings: dict[str, Any],
    fa_vectorizer: DictVectorizer,
):
    print(result)
    print(history)
    print(settings)
    print(fa_vectorizer)
