import math
from typing import Any, Sequence

import numpy as np

from ..serializers.circuit import SerializedCircuit
from ..serializers.custom_types import (
    Circuit,
    CirqQubit,
    QiskitQubit,
    is_qiskit_cirq_circuit,
)
from ..serializers.serializer import (
    get_default_qubit_objects,
    get_qubits_from_circuit_dict_list,
)
from .constants import (
    MAX_EASY_BOND_DIM,
    MAX_ELEMENTS,
    MPO_BOND_DIM_NO_NOISE,
    MPO_BOND_DIM_WITH_NOISE,
    NUM_ROWS,
)
from .resources import _num_elements_without_bond_dim_dmrg


def qubits_from_any_circuit(
    circuit: Circuit | list[dict[str, Any]] | SerializedCircuit
) -> tuple[QiskitQubit, ...] | tuple[CirqQubit, ...] | tuple[str, ...]:
    """Given a circuit in as SerializedCircuit, qiskit or cirq circuit, or list of dicts, return the qubits.

    Parameters
    ----------
    circuit
        Circuit in qiskit, cirq or serialized format.

    Returns
    -------
    qubits
        The qubits in the circuit.
    """
    if is_qiskit_cirq_circuit(circuit):
        return tuple(get_default_qubit_objects(circuit))  # type: ignore
    elif isinstance(circuit, SerializedCircuit):
        return circuit.qubits  # type: ignore
    elif isinstance(circuit, list):
        return get_qubits_from_circuit_dict_list(circuit)
    else:
        raise ValueError(f"Unrecognized circuit type {type(circuit)}.")


def standard_config_impl(
    circuit: Circuit | list[dict[str, Any]] | SerializedCircuit,
    effort: float = 0.1,
    noise: bool = False,
) -> dict[str, Any]:
    """Given a circuit in any known format, return a default config setup.

    Parameters
    ----------
    circuit
        Circuit in qiskit, cirq, dict_list or serialized format.
    effort
        A float between 0 and 1 that specifies the 'effort' that should be put
        into emulation. A number closer to 1 will aim to maximize fidelity of the emulation
        (up to memory limitations).
    noise
        Indicate whether this is a noisy simulation or not.

    Returns
    -------
    config
        Standard config based on the circuit.
    """
    qubits: Sequence[QiskitQubit | CirqQubit | str]
    if not (isinstance(effort, (float, int)) and 0 <= effort <= 1):
        raise ValueError(f"Effort should be a float between 0 and 1 (got {effort}).")

    qubits = qubits_from_any_circuit(circuit)
    n_qubits = len(qubits)

    # Group size is small for optimal memory usage
    if noise or n_qubits == 2:
        group_size = 1
    else:
        group_size = 2

    # Compute the maximum bond dimension that saturates available memory
    bond_dim = bond_dim_from_group_sizes(
        group_sizes=[group_size] * math.ceil(n_qubits / group_size),
        noise=noise,
        effort=effort,
    )

    # DMRG specific options (dmrg is the default emulation option)
    dmrg_config_settings = {
        "D": bond_dim,
        "convergence_window_size": math.ceil(n_qubits / group_size)
        * 2,  # Twice length of grouping
        "max_subcircuit_rows": NUM_ROWS,
        "mpo_bond_dim": None,
        "regular_grid": True,
        "truncate_rows": True,
    }

    # By default take 1000 samples
    output_settings = {
        "expectation_values": {"enabled": False, "observables": {}},
        "sampling": {"enabled": True, "n_shots": 1000},
        "mps": {"enabled": False},
        "amplitudes": {"enabled": False, "bitstrings": "all" if n_qubits < 6 else [0]},
    }

    config = {
        "mode": "dmrg",
        "qubits": list(qubits),
        "grouping": None,
        "group_size": group_size,
        "dmrg": dmrg_config_settings,
        "noise": {"validate_model": True},
        "output": output_settings,
    }
    return config


def bond_dim_from_group_sizes(
    group_sizes: Sequence[int],
    noise: bool,
    effort: float = 0.1,
) -> int:
    """Return the maximal bond dimension (up to a limit) for a particular grouping.

    Given a particular grouping, determines the maximal bond dimension
    that does not exceed a maximum space requirement (given by MAX_ELEMENTS).
    This function never returns a bond dimension larger than that needed for
    exact emulation. The group sizes are provided as inputs, not the grouping itself.

    Parameters
    ----------
    group_sizes
        The sizes of the groups in the grouping.
    noise :
        Whether noise is on or off. If on, then the 'qubits' are taken to be dim-4 qudits.
    effort :
        Optional float between 0 and 1 that determines the effort put into obtaining
        a high-fidelity.

    Returns
    -------
    bond_dim
        The computed bond dimension.
    """

    # If there is only one group, we don't need a bond dimension
    if len(group_sizes) == 1:
        return 1

    phys_dim = 4 if noise else 2

    # Compute the maximum number of elements created without including the bond dimension
    group_dim = phys_dim ** max(size for size in group_sizes)
    mpo_bond_dim = MPO_BOND_DIM_WITH_NOISE if noise else MPO_BOND_DIM_NO_NOISE
    mps_length = len(group_sizes)

    num_elements = _num_elements_without_bond_dim_dmrg(
        group_dim, mpo_bond_dim, mps_length, noise
    )

    max_bond_dim = int(np.floor(np.sqrt(MAX_ELEMENTS / num_elements)))

    # Compute the log of the minimum bond dim required for an exact emulation
    log_max_ltr = np.cumsum([size for size in group_sizes[:-1]])
    log_max_rtl = np.cumsum([size for size in group_sizes[::-1][:-1]])[::-1]
    log_exact_fidelity_bond_dim = np.max(list(map(min, zip(log_max_ltr, log_max_rtl))))

    # If the bond dimension for a fidelity one emulation is achievable below the 'easy' maximum,
    #  we always do that
    log_max_easy_bond_dim = np.log2(MAX_EASY_BOND_DIM) / np.log2(phys_dim)
    if log_exact_fidelity_bond_dim < log_max_easy_bond_dim:
        return phys_dim**log_exact_fidelity_bond_dim

    # Otherwise, if the exact is smaller than min(effort * max_bond_dim, MAX_EASY_BOND_DIM), we return that,
    #   else we return the maximum of the effort * max_bond_dim and the max_easy_bond_dim
    return min(
        phys_dim**log_exact_fidelity_bond_dim,
        max(effort * max_bond_dim, MAX_EASY_BOND_DIM),
    )
