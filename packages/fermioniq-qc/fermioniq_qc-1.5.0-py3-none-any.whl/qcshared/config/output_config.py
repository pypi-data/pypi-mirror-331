import warnings
from typing import Any, Optional

from pydantic import StrictInt, StrictStr, field_validator, model_validator

from qcshared.config.config_utils import BaseConfig, ConfigWarning
from qcshared.config.constants import (
    MAX_BITSTRINGS,
    MAX_QUBITS_FOR_FULL_OUTPUT,
    MAX_SHOTS,
)
from qcshared.io.observables import PauliSumObservable


class ExpectationValuesOutputConfig(BaseConfig):
    enabled: bool = False
    observables: list[PauliSumObservable] = []


class AmplitudesOutputConfig(BaseConfig):
    enabled: bool = False

    # Note the strict types to prevent coercion
    bitstrings: list[StrictStr] | list[StrictInt] | str = [0]

    @field_validator("bitstrings", mode="before")
    @classmethod
    def validate_bitstrings_maxlen(cls, bitstrings):
        """Pre-check for too long list of bitstrings"""
        if len(set(bitstrings)) > MAX_BITSTRINGS:
            raise ValueError(
                f"The number of amplitudes requested is {len(bitstrings)}, which is "
                "beyond the supported limit of {MAX_BITSTRINGS}."
            )
        return bitstrings

    @field_validator("bitstrings", mode="after")
    @classmethod
    def validate_bitstrings(cls, bitstrings, info):
        """Validates bitstrings

        Raises
        ------
        ValueError

            - If bitstrings are *not* given as a list of ints or a list of str (this should already be checked by type-checking)
            - If given as strings, but contain other values than 0 and 1
            - If given as ints, but with negative ints is positive
            - If no bitstrings are provided, but ``enabled`` is True
        ConfigWarning

            - If any of the errors listed above is encountered, but ``enabled`` is False
            - If bitstrings are not unique
        """
        err_location = ["emulator_config", "output", "amplitudes", "bitstrings"]

        # Check that some bitstrings were provided
        if len(bitstrings) == 0:
            if info.data.get("enabled"):
                raise ValueError(
                    "You must provide at least one bitstring, or set bitstrings = 'all' "
                    "if computing amplitudes as output. "
                    f"Warning: Only do this for up to {MAX_QUBITS_FOR_FULL_OUTPUT} qubits."
                )
            else:
                err_msg = (
                    "You should provide at least one bitstring, or set bitstrings = 'all' "
                    "if computing amplitudes as output. "
                    "This will cause an error if computing amplitudes is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )

        # If bitstrings are given as strings, then check that there are no non-binary values in there
        if isinstance(bitstrings, list) and all(
            isinstance(bs, str) for bs in bitstrings
        ):
            if any(b not in ("0", "1") for bs in bitstrings for b in bs):
                if info.data.get("enabled"):
                    raise ValueError(
                        "Encountered non-binary value in bitstrings provided."
                    )
                else:
                    err_msg = (
                        "Encountered non-binary value in bitstrings provided."
                        "This will cause an error if computing amplitudes is enabled."
                    )
                    warnings.warn(
                        ConfigWarning(
                            err_location,
                            "Potential source of error",
                            err_msg,
                        )
                    )

        # If bitstrings is a list of ints, check that there are no negative values
        elif isinstance(bitstrings, list) and all(
            isinstance(bs, int) for bs in bitstrings
        ):
            if any(bs < 0 for bs in bitstrings):
                if info.data.get("enabled"):
                    raise ValueError("Encountered negative value in bitstrings.")
                else:
                    err_msg = (
                        "Encountered negative value in bitstrings."
                        "This will cause an error if computing amplitudes is enabled."
                    )
                    warnings.warn(
                        ConfigWarning(
                            err_location,
                            "Potential source of error",
                            err_msg,
                        )
                    )

        # If bitstrings is a string, check that it is "all" (the only valid setting in this case)
        elif isinstance(bitstrings, str) and bitstrings != "all":
            if info.data.get("enabled"):
                raise ValueError(
                    "Bitstrings must be one of: 'all', a list of integers, or a list of strings."
                )
            else:
                err_msg = (
                    "Bitstrings must be one of: 'all', a list of integers, or a list of strings."
                    "This will cause an error if computing amplitudes is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )

        # Check that bitstrings are unique, raising a warning if not (this won't cause errors).
        if isinstance(bitstrings, list) and len(set(bitstrings)) != len(bitstrings):
            bitstrings = [b for b in set(bitstrings)]
            err_msg = (
                "Bitstrings provided are not unique. Removed all duplicate bitstrings."
            )
            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Redundant input",
                    err_msg,
                )
            )
        return bitstrings


class SampleOutputConfig(BaseConfig):
    enabled: bool = True
    n_shots: Optional[int] = 1000
    return_probabilities: bool = False

    @field_validator("n_shots", mode="before")
    @classmethod
    def validate_n_shots(cls, n_shots, info):
        """Validates n_shots

        Raises
        ------
        ValueError

            - If n_shots is negative
            - If n_shots is larger than the maximum number of shots allowed
            - If n_shots is not provided, but ``enabled`` is True
        ConfigWarning
            - If any of the two first errors listed above is encountered, but ``enabled`` is False
        """

        err_location = ["emulator_config", "output", "sampling", "n_shots"]
        if info.data.get("enabled") and n_shots is None:
            raise ValueError(
                "You must provide a number of shots if using sampling as output."
            )
        if n_shots is not None and n_shots < 0:
            if info.data.get("enabled"):
                raise ValueError(f"Invalid number of shots {n_shots} (negative value).")
            else:
                err_msg = (
                    f"Invalid number of shots {n_shots} (negative value). "
                    "This will cause an error if sampling output is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )
        elif n_shots is not None and n_shots > MAX_SHOTS:
            if info.data.get("enabled"):
                raise ValueError(
                    f"Invalid number of shots {n_shots} (Surpasses limit of {MAX_SHOTS})."
                )
            else:
                err_msg = (
                    f"Invalid number of shots {n_shots} (Surpasses limit of {MAX_SHOTS}). "
                    "This will cause an error if sampling output is enabled."
                )
                warnings.warn(
                    ConfigWarning(
                        err_location,
                        "Potential source of error",
                        err_msg,
                    )
                )
        return n_shots


class MpsOutputConfig(BaseConfig):
    enabled: bool = False


class OutputConfig(BaseConfig):
    amplitudes: AmplitudesOutputConfig = AmplitudesOutputConfig()
    sampling: SampleOutputConfig = SampleOutputConfig()
    mps: MpsOutputConfig = MpsOutputConfig()
    expectation_values: ExpectationValuesOutputConfig = ExpectationValuesOutputConfig()

    @model_validator(mode="after")
    def validate_all(self):
        """Validates the output config as a whole

        Raises
        ------
        ValueError

            - If no output modes are enabled
        """

        if not any(
            [
                self.amplitudes.enabled,
                self.sampling.enabled,
                self.mps.enabled,
                self.expectation_values.enabled,
            ]
        ):
            raise ValueError("There are no output modes enabled.")
        return self
