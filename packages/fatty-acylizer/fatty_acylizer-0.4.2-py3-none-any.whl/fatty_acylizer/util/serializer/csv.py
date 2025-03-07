import csv
import pathlib
from typing import Any
from typing import TextIO

import numpy as np
from fatty_acylizer.util.model import Model
from fatty_acylizer.util.optimization import Callback
from sklearn.feature_extraction import DictVectorizer


class FaProfileSerializer:
    def __init__(self, filename: str, vectorizer: DictVectorizer):
        self.filename = pathlib.Path(filename)
        self._vectorizer = vectorizer
        self.setup()

    def get_writer(self, file):
        writer = csv.DictWriter(
            file,
            fieldnames=self._vectorizer.feature_names_,
        )
        return writer

    def setup(self):
        with open(self.filename, 'w') as f:
            self.get_writer(f).writeheader()

    def add_callback(self, callback: Callback):
        with open(self.filename, 'a') as f:
            (profile,) = self._vectorizer.inverse_transform(callback.x.reshape(1, -1))
            self.get_writer(f).writerow(profile)

    def __call__(self, callback: Callback):
        return self.add_callback(callback)


class LipidProfileSerializer:
    def __init__(self, filename: str, model: Model):
        self.filename = pathlib.Path(filename)
        self.model = model
        self._fieldnames = list(sorted(str(lipid) for lipid in model.table[-1]))
        self.setup()

    def get_writer(self, file: TextIO):
        writer = csv.DictWriter(file, fieldnames=self._fieldnames)
        return writer

    def setup(self):
        with open(self.filename, 'w') as f:
            self.get_writer(f).writeheader()

    def add_callback(self, callback: Callback):  # noqa ARG002
        # call back is not used, but rather the last entry in the raw model table
        # This does not require the model to be reevaluated again
        lipid_profile = {
            str(lipid): prob for lipid, prob in self.model.table[-1].items()
        }
        with open(self.filename, 'a') as f:
            self.get_writer(f).writerow(lipid_profile)

    def __call__(self, callback: Callback):
        return self.add_callback(callback)


class DistanceSerializer:
    def __init__(self, filename: str):
        self.filename = pathlib.Path(filename)
        self.setup()

    def get_writer(self, file: TextIO):
        writer = csv.DictWriter(
            file,
            fieldnames=['distance'],
        )
        return writer

    def setup(self):
        with open(self.filename, 'w') as f:
            self.get_writer(f).writeheader()

    def add_callback(self, callback: Callback):
        with open(self.filename, 'a') as f:
            self.get_writer(f).writerow({'distance': callback.fun})

    def __call__(self, callback: Callback):
        return self.add_callback(callback)


class LogSerializer:
    def __init__(self, filename: str, settings: dict[str, Any]):
        self.filename = pathlib.Path(filename)
        self.setup(settings)
        self._iter = 0

    def get_writer(self, file: TextIO):
        return csv.DictWriter(file, fieldnames=['setting', 'value'], delimiter='\t')

    def setup(self, settings: dict[str, Any]):
        with open(self.filename, 'w') as f:
            f.write('Settings\n')
            f.write('--------\n\n')
            writer = self.get_writer(f)
            for setting, value in settings.items():
                if isinstance(value, np.ndarray):
                    value = ', '.join(str(v) for v in value)
                writer.writerow({'setting': setting, 'value': value})
            # for callbacks
            f.write('\nHistory\n')
            f.write('-------\n\n')

    def add_callback(self, callback: Callback):
        with open(self.filename, 'a') as f:
            f.write(f'Step {self._iter}:\n')
            self._iter += 1
            writer = self.get_writer(f)
            for setting, value in callback.report().items():
                if isinstance(value, np.ndarray):
                    value = ', '.join(str(v) for v in value)
                writer.writerow({'setting': setting, 'value': value})
            f.write('\n')

    def __call__(self, callback: Callback):
        return self.add_callback(callback)
