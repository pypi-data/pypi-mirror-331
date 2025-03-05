from numbers import Number
from typing import Any, Literal, Optional

import numpy as np
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from qcshared.io.observables import PauliSumObservable

from .config_utils import BaseConfig

SUPPORTED_SCIPY_METHODS = [
    "cobyla"
]  # can add others from https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html


class SPSAConfig(BaseConfig):
    learning_rate: float = 5.0
    learning_rate_exponent: float = 0.6
    perturbation: float = 1e-2
    perturbation_exponent: float = 0.1
    eps: float = 1e-14
    max_iter: int = 100
    params_tol: float = 1e-8
    fun_tol: float = 1e-7
    model_config = ConfigDict(extra="forbid")


class COBYLAConfig(BaseModel):
    maxiter: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("max_iter", "maxiter")
    )
    rhobeg: Optional[float] = 1.0
    tol: Optional[float] = 1e-4
    catol: Optional[float] = 2e-4
    model_config = ConfigDict(extra="forbid")


class OptimizerConfig(BaseConfig):
    enabled: bool = False
    observable: Optional[PauliSumObservable] = Field(
        default=None, validate_default=True
    )
    optimizer_name: Literal["spsa", "cobyla"] = "spsa"
    evaluation_mode: Literal["contract"] = "contract"
    optimizer_settings: Any = {}
    initial_param_values: dict[str, float] = {}
    initial_param_noise: float = 0.1

    @field_validator("optimizer_settings", mode="before")
    @classmethod
    def validate_optimizer_settings(cls, optimizer_settings, info):
        if info.data["enabled"]:
            match info.data["optimizer_name"]:
                case "spsa":
                    optimizer_settings = SPSAConfig(**optimizer_settings)
                case "cobyla":
                    optimizer_settings = COBYLAConfig(**optimizer_settings)
        return optimizer_settings

    @field_validator("observable", mode="before")
    @classmethod
    def validate_observable(cls, observable, info):
        if info.data["enabled"] and observable is None:
            raise ValueError("If optimizer is enabled, an observable must be specified")

        if not info.data["enabled"]:
            return None
        return observable

    @field_validator("initial_param_noise")
    @classmethod
    def validate_initial_param_noise(cls, initial_param_noise, info):
        if initial_param_noise < 0:
            raise ValueError("initial_param_noise must be non-negative")

        if not info.data["initial_param_values"] and np.isclose(initial_param_noise, 0):
            raise ValueError(
                "The parameter initial_param_noise is zero, and no initial parameter values are given in "
                "initial_param_values. This means that all parameters will start at exactly zero, "
                "which can often create problems in the optimization. Please provide initial values"
                " or let initial_param_noise be non-zero."
            )

        return initial_param_noise
