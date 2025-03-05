from numbers import Number
from typing import Any, Literal

from pydantic import StrictStr, field_validator

from qcshared.config.config_utils import BaseConfig


class PauliProductTerm(BaseConfig):
    """Class for storing a product of single-qubit Pauli observables.

    Contain the different observables together with their
    respective coefficients (relevant when combining several
    PauliProductTerms into one PauliSumObservable).

    Attributes
    ----------
    paulis
        dictionary with qubit labels (str) as keys, and a Pauli operator
        ('X', 'Y', or 'Z') as values
    coeff
        a complex-valued coefficient.
    """

    paulis: dict[str, Literal["X", "Y", "Z"]]
    coeff: Any  # (int | float | complex)

    @field_validator("coeff")
    @classmethod
    def validate_coeff(cls, coeff):
        if not isinstance(coeff, Number):
            raise ValueError("Pauli operator coefficient should be a number")
        return coeff


class PauliSumObservable(BaseConfig):
    """Class for observables composed of a linear combination of local Pauli operators.

    Each PauliObservable contains a 'coeff' attribute that stores the coefficient of the
    operator in question.

    Attributes
    ----------
    terms
        A list of PauliProductTerm objects.
    name
        Name of the PauliSumObservable.
    """

    terms: list[PauliProductTerm]
    name: StrictStr

    def __len__(self):
        return len(self.observables)
