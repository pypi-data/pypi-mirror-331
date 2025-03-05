import json
import math

import numpy as np

from .. import noise_models
from ..config.config_utils import ConfigWarning
from ..config.emulator_config import EmulatorConfig
from ..messaging import message
from ..serializers.circuit import SerializedCircuit


class CustomDecoder(json.JSONDecoder):  # numpydoc ignore=PR01
    """Custom JSON decoder for classes and data types that we use."""

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "__ClientMessage__" in dct:
            class_name = dct["__ClientMessage__"]["name"]
            class_contents = dct["__ClientMessage__"]["content"]
            return getattr(message, class_name).from_dict(class_contents)
        # Complex numbers (not serializable by default)
        elif "__complex__" in dct:
            for k in ["real", "imag"]:
                if dct[k] is None:
                    dct[k] = math.nan
            return complex(dct["real"], dct["imag"])
        # Numpy arrays
        elif "__ndarray__" in dct:
            return np.array(dct["data"], dtype=dct["dtype"])
        # Config warnings
        elif "__ConfigWarning__" in dct:
            return ConfigWarning(dct["loc"], dct["type"], dct["msg"])
        # BaseNoiseComponent and its subclasses (e.g. NoiseChannel, QubitNoise, GateNoise, NoiseModel)
        elif "__BaseNoiseComponent__" in dct:
            class_name = dct["type"]
            return getattr(noise_models, class_name).from_dict(dct)
        # Serialized circuits
        elif "__SerializedCircuit__" in dct:
            return SerializedCircuit.from_dict(dct)
        elif "__EmulatorConfig__" in dct:
            return EmulatorConfig(**dct["values"])
        else:
            return dct


def dejsonify(data):
    """Shorthand to convert json encodable data to its original format with the custom decoder.

    Parameters
    ----------
    data
        The data to be decoded from json with the custom decoder.
    """
    json_string = json.dumps(data)
    return json.loads(json_string, cls=CustomDecoder)
