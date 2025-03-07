from copy import copy
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import NamedTuple
from typing import Protocol

import numpy as np
import numpy.typing as npt
import scipy.optimize
from fatty_acylizer.util.feature import BasicNumber
from fatty_acylizer.util.model import Model
from fatty_acylizer.util.model import Profile
from fatty_acylizer.util.model import Result
from sklearn.feature_extraction import DictVectorizer


@dataclass
class Callback:
    x: npt.NDArray
    fun: float
    nfev: int | None = field(default=None)
    message: str | None = field(default=None)
    jac: npt.NDArray | None = field(default=None)
    njev: int | None = field(default=None)
    hess: npt.NDArray | None = field(default=None)
    nhev: int | None = field(default=None)
    nit: int | None = field(default=None)
    success: bool | None = field(default=None)
    status: int | None = field(default=None)

    @classmethod
    def from_optimize_result(cls, result):
        kwargs = {
            k: copy(v) for k, v in result.items() if k in cls.__dataclass_fields__
        }
        return cls(**kwargs)

    def report(self) -> dict[str, str]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class Serializer(Protocol):
    def __call__(
        self,
        callback: Callback,
    ): ...


class ArrayResult(NamedTuple):
    profile: npt.NDArray
    gradient: list[npt.NDArray] | None


class Optimization:
    def __init__(
        self,
        model: Model,
        ftol: float = 5e-3,
        gtol: float = 1e-4,
        verbose: bool = False,
        max_iter: int = 100,
    ):
        self.raw_model = model
        self.ftol = ftol
        self.verbose = verbose
        self.max_iter = max_iter
        self.gtol = gtol

        self.method: str = 'l-bfgs-b'
        # require setup!
        self._lipid_vectorizer: DictVectorizer | None = None
        self._fa_vectorizer: DictVectorizer | None = None
        self._target_array: npt.NDArray | None = None
        self._x0: npt.NDArray | None = None

        self._history: list[Callback] = []
        self._callback_handlers: list = []

    @property
    def lipid_vectorizer(self) -> DictVectorizer:
        if self._lipid_vectorizer is None:
            raise NotImplementedError
        return self._lipid_vectorizer

    @property
    def fa_vectorizer(self) -> DictVectorizer:
        if self._fa_vectorizer is None:
            raise NotImplementedError
        return self._fa_vectorizer

    @property
    def target_array(self) -> npt.NDArray:
        if self._target_array is None:
            raise NotImplementedError
        return self._target_array

    @property
    def x0(self) -> npt.NDArray:
        if self._x0 is None:
            raise NotImplementedError
        return self._x0

    @property
    def history(self) -> list[Callback]:
        return self._history

    def model(self, fa_array: npt.NDArray) -> ArrayResult:
        """Wrapper around the model

        Utilizes the initialized DictVectorizers to translate profiles to array
        representation.
        """
        fa_profile: Profile = self.fa_vectorizer.inverse_transform(
            fa_array.reshape(1, -1)
        )[0]
        result: Result = self.raw_model(
            fa_profile=fa_profile,
        )
        lipid_array: npt.NDArray = self.lipid_vectorizer.transform(
            result.profile
        ).reshape(-1)
        if not result.gradient:
            return ArrayResult(profile=lipid_array, gradient=None)

        gradient = [
            self.lipid_vectorizer.transform(g).reshape(-1) for g in result.gradient
        ]
        return ArrayResult(profile=lipid_array, gradient=gradient)

    def objective_function(
        self,
        fa_array: npt.NDArray,
    ) -> float | tuple[float, npt.NDArray]:
        result = self.model(fa_array=fa_array)
        lipid_array = result.profile
        distance_squared = np.sum(np.square(lipid_array - self.target_array))
        constraint = (1 - np.sum(fa_array)) ** 2
        function_value: float = float(distance_squared + constraint)
        if not result.gradient:
            return function_value
        gradient = result.gradient
        g_distance_sq = 2 * np.sum((lipid_array - self.target_array) * gradient, axis=1)
        g_constraint = 2 * np.sum(fa_array) - 2
        gradient_value: npt.NDArray = g_distance_sq + g_constraint
        return (function_value, gradient_value)

    def fit(
        self,
        fa_profile: dict[BasicNumber, float],
        target_profile: dict[BasicNumber, float],
        requires_setup: bool = True,
    ):
        """Fit a fatty acid profile to a target lipid profile.

        args:
            fa_profile:
                start guess for the optimizer
            target_profile:
                lipid profile the fatty acid profile is fitted to

        This function has important side effects and initializes the start guess x0,
        the target lipid profile, and the vectorizers for mapping profiles to arrays and
        back.
        """
        if requires_setup:
            self.setup(fa_profile=fa_profile, target_profile=target_profile)

        match self.objective_function(self.x0):
            case (float() as value, _):
                distance = value
            case float() as value:
                distance = value
            case _:
                raise ValueError

        start = scipy.optimize.OptimizeResult(
            x=self.x0,
            fun=distance,
        )
        self.callback(start)
        # fit
        result = scipy.optimize.minimize(
            x0=self.x0,
            fun=self.objective_function,
            jac=self.raw_model.jac,
            bounds=[(0, 1)] * len(self.x0),
            method=self.method,
            options=self.opt_settings,
            callback=self.callback,
        )
        self.history.pop()
        self.history.append(Callback.from_optimize_result(result))
        return result

    def setup(
        self,
        fa_profile: dict[BasicNumber, float],
        target_profile: dict[BasicNumber, float],
    ):
        # setup
        self._fa_vectorizer = DictVectorizer(sparse=False, sort=False)
        self._x0 = self.fa_vectorizer.fit_transform([fa_profile]).reshape(-1)

        # This always constructs all possible lipids, even if their probability is 0
        # This way, the lipid vectorizer is always properly defined
        result = self.raw_model(fa_profile=fa_profile)
        lipid_profile = result.profile
        self._lipid_vectorizer = DictVectorizer(sparse=False, sort=False)
        self.lipid_vectorizer.fit([lipid_profile])
        self._target_array = self.lipid_vectorizer.transform(target_profile).reshape(-1)

    def callback(self, intermediate_result: scipy.optimize.OptimizeResult):
        callback = Callback.from_optimize_result(intermediate_result)
        self.history.append(callback)
        for handler in self._callback_handlers:
            handler(callback)

    @property
    def opt_settings(self):
        return {
            'disp': self.verbose,
            'iprint': 101,
            'ftol': self.ftol,
            'gtol': self.gtol,
            'maxiter': self.max_iter,
        }

    @property
    def settings(self):
        settings: dict[str, Any] = self.opt_settings | self.raw_model.settings
        return settings

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        params = ', '.join(
            [f'{key}={value}' for key, value in self.opt_settings.items()]
        )
        return f'{cls_name}({params})'

    def add_callback_handler(self, handler) -> None:
        self._callback_handlers.append(handler)

    def save_results(self, *serializers: Serializer) -> None:
        """Save the results of the optimization run.

        Either the provided serializers or all serializers added through
        `add_callback_handler` will be used for serializing the callbacks
        stored in `history`.
        """

        for serializer in serializers or self._callback_handlers:
            for callback in self.history:
                serializer(callback)
