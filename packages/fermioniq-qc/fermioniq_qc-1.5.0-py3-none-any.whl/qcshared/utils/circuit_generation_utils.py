import inspect
import math
from typing import Sequence, Union

import cirq
import numpy as np
import qiskit
from cirq.ops import *
from cirq.ops.pauli_gates import _PauliX, _PauliY, _PauliZ

from .gate_maps import (
    cirq_single_qubit_gates,
    cirq_two_qubit_gates,
    qiskit_single_qubit_gates,
    qiskit_two_qubit_gates,
)

cirq_gate_keyword_args = [
    "exponent",
    "theta",
    "phi",
    "zeta",
    "chi",
    "gamma",
    "x_exponent",
    "z_exponent",
    "axis_phase_exponent",
    "phase_exponent",
    "global_shift",
    "rads",
]


def add_random_cirq_gate(
    circuit: cirq.Circuit,
    qubits: Sequence[Union[cirq.LineQubit, cirq.GridQubit, cirq.NamedQubit]],
):
    """
    Add a random Cirq gate to a cirq circuit. Only single qubit and two qubit gates are supported.

    Parameters
    ----------
    circuit :
        The circuit to add the gate to
    qubits :
        Sequence of cirq qubits, on which the gate will be applied.

    Returns
    -------
    circuit :
        The same circuit that was passed as input, but with the added gate.

    Raises
    ------
    ValueError
        If the number of qubits is not 1 or 2.
    """

    if len(qubits) == 1:
        gate_name = np.random.choice(list(cirq_single_qubit_gates.keys()))
    elif len(qubits) == 2:
        gate_name = np.random.choice(list(cirq_two_qubit_gates.keys()))
    else:
        raise ValueError(f"Trying to add a random cirq gate to {len(qubits)} qubits")

    gate_class = eval(gate_name)
    params = inspect.signature(gate_class.__init__).parameters

    # Set available keyword arguments to random values
    attrs = {}
    for p in params:
        if p in cirq_gate_keyword_args:
            attrs[p] = np.random.uniform(math.pi * 2)

    # Create gate
    try:
        # Some cirq gate require initialisation with attributes, and application on qubits.
        gate = gate_class(**attrs)
        circuit.append(gate(*qubits))
    except:
        # Some cirq gates require initialisation with both attributes and qubits.
        circuit.append(gate_class(*qubits, **attrs))

    return circuit


def add_random_qiskit_gate(
    circuit: qiskit.QuantumCircuit,
    qubits: Sequence[qiskit.circuit.quantumregister.Qubit],
):
    """
    Add a qiskit gate to a qiskit circuit.

    Parameters
    ----------
    circuit :
        The circuit to add the gate to
    qubits :
        Sequence of qiskit qubits, on which the gate will be applied.

    Returns
    -------
    circuit :
        The same circuit that was passed as input, but with the added gate.

    Raises
    ------
    ValueError
        If the number of qubits is not 1 or 2.
    """
    qubits = list(qubits)
    if len(qubits) == 1:
        gate_name = np.random.choice(list(qiskit_single_qubit_gates.keys()))
    elif len(qubits) == 2:
        gate_name = np.random.choice(list(qiskit_two_qubit_gates.keys()))
    else:
        raise ValueError(f"Trying to add a random qiskit gate to {len(qubits)} qubits")

    attrs = {}
    for p, info in inspect.signature(getattr(circuit, gate_name)).parameters.items():
        if info.annotation == "ParameterValueType":
            attrs[p] = np.random.uniform(math.pi * 2)
        if info.annotation == "QubitSpecifier":
            attrs[p] = qubits.pop(0)

    getattr(circuit, gate_name)(**attrs)
    return circuit
