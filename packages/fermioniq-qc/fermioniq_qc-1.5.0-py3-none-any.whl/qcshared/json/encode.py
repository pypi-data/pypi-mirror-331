import base64
import json
import zlib
from typing import Literal

import numpy as np
from pydantic import BaseModel

from qcshared.config.config_utils import ConfigWarning
from qcshared.noise_models import NoiseModel
from qcshared.noise_models.utils import BaseNoiseComponent
from qcshared.serializers.circuit import SerializedCircuit

from ..config.emulator_config import EmulatorConfig


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder for classes and data types that we use."""

    def default(self, obj):
        if isinstance(
            obj, (complex, np.csingle, np.cdouble, np.clongdouble)
        ):  # Complex numbers (not serializable by default)
            return {
                "__complex__": True,
                "real": float(obj.real),
                "imag": float(obj.imag),
            }
        elif isinstance(obj, np.ndarray):  # Numpy arrays
            return {
                "__ndarray__": True,
                "data": obj.tolist(),
                "dtype": str(obj.dtype),
            }
        elif isinstance(obj, ConfigWarning):  # Config warnings
            return {
                "__ConfigWarning__": True,
                "loc": obj.loc,
                "type": obj.type,
                "msg": obj.msg,
            }
        elif isinstance(
            obj, BaseNoiseComponent
        ):  # Any objects derived from the BaseNoiseComponent class
            d = obj.to_dict()
            d["__BaseNoiseComponent__"] = True
            return d
        elif isinstance(obj, SerializedCircuit):  # Serialized circuits
            d = obj.to_dict()
            d["__SerializedCircuit__"] = True
            return d
        elif isinstance(obj, EmulatorConfig):  # EmulatorConfig
            return {"__EmulatorConfig__": True, "values": obj.model_dump()}
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)

        try:
            return super().default(obj)
        except Exception as e:
            print("Error encoding:", obj)
            raise e


def jsonify(data):
    """Shorthand to convert data to a json encodable dict.

    Useful for encoding data that is not serializable by default.
    See CustomEncoder for more information.

    Parameters
    ----------
    data
        The data to json encode with the custom encoder.

    Returns
    -------
    json_compatible_data
        The data encoded in a json-compatible format.
    """
    json_string = json.dumps(data, cls=CustomEncoder)
    return json.loads(json_string)


class NoiseModelWrapper(BaseModel):
    provider: Literal["user", "fermioniq"]
    content: str


def wrap_noise_model(noise_model: dict | str | None) -> dict | None:
    """
    Wrap noise_model in a dict with 'provider' and 'content' keys.

    The 'provider' entry of the dict shows who authored the noise model ('user' or 'fermioniq')
    while the 'content' entry is the noise model.
    If noise_model is None then return None instead

    Parameters
    ----------
    noise_model
        Noise model to wrap (already jsonified).

    Returns
    -------
    wrapped_noise_model
        Wrapped noise model.
    """
    if isinstance(noise_model, dict):
        return NoiseModelWrapper(
            provider="user",
            content=json.dumps(noise_model),
        ).model_dump()
    elif isinstance(noise_model, str):
        return NoiseModelWrapper(
            provider="fermioniq",
            content=noise_model,
        ).model_dump()
    else:
        return None


def compress_json(json_data: list | dict) -> str:
    """
    Compresses serializable objects (a (nested) list or dict) into a string.

    Parameters
    ----------
    json_data
        The data to compress.

    Returns
    -------
    compressed_data
        The compressed data as a string.
    """
    return base64.b64encode(
        zlib.compress(json.dumps(json_data).encode("utf-8"))
    ).decode("utf-8")
