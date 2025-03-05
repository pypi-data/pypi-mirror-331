from itertools import combinations
from typing import Sequence

import numpy as np

from qcshared.io.observables import PauliProductTerm, PauliSumObservable


def pauli_observables_equal(po1: PauliProductTerm, po2: PauliProductTerm) -> bool:
    if po1.coeff != po2.coeff:
        return False
    if po1.paulis.keys() != po2.paulis.keys():
        return False
    for k in po1.paulis.keys():
        if po1.paulis[k] != po2.paulis[k]:
            return False
    return True


def random_pauli_term(
    qubit_labels: Sequence[str], pauli_density: float | int = 0.75
) -> PauliProductTerm:
    """Creates a random PauliProductTerm with n_qubits qubits.

    Creates a PauliProductTerm, where each qubit has the probability ``pauli_density`` to
    to be assigned a pauli. There will always be at least one qubit with a pauli, even if
    ``pauli_density = 0.``

    Parameters
    ----------
    qubit_labels
        Labels of qubits to (potentially) include in the PauliProductTerm.
    pauli_density
        Parameter controlling how many factors are in the PauliProductTerm on average,
        as a fraction of the number of qubits.

    Returns
    -------
    pauli_observable
        The random PauliProductTerm.
    """

    assert 0 <= pauli_density <= 1

    paulis = {}
    for q in qubit_labels:
        if np.random.random() < pauli_density:
            paulis[q] = str(np.random.choice(["X", "Y", "Z"]))

    # Ensure at least one qubit has a Pauli operator
    if len(paulis) == 0:
        paulis[str(np.random.choice(qubit_labels))] = str(
            np.random.choice(["X", "Y", "Z"])
        )

    coeff = np.random.random() + 1j * np.random.random()
    return PauliProductTerm(paulis=paulis, coeff=coeff)


def random_pauli_sum_observable(
    qubit_labels,
    max_n_terms: int,
    pauli_density=0.75,
    name: str = "random_pauli_sum_observable",
):
    """Creates a list of random PauliSumObservable objects with n_qubits qubits.

    Parameters
    ----------
    qubit_labels
        Labels of qubits to possibly include in the PauliSumObservable.
    max_n_terms
        Maximum number of PauliProductTerm objects to include in the
        PauliSumObservable.
    pauli_density
        Determines how many paulis on average will be included in each
        PauliProductTerm.
    name
        Name to assign to the PauliSumObservable.

    Returns
    -------
    random_observables
        A list of 10 random PauliSumObservables.
    """
    # Create a list of random Pauli observables
    pauli_product_terms = [
        random_pauli_term(qubit_labels, pauli_density)
        for _ in range(np.random.randint(1, max_n_terms + 1))
    ]
    return PauliSumObservable(terms=pauli_product_terms, name=name)
