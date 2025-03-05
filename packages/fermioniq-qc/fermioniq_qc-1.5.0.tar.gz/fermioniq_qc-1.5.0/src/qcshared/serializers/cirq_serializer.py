from typing import Union

import numpy as np

from ..io.observables import PauliProductTerm, PauliSumObservable
from ..utils.constants import MAX_QUBITS_PER_GATE_OR_CHANNEL
from ..utils.gate_maps import cirq_gate_map
from .circuit import SerializedCircuit
from .custom_types import (
    CirqCircuit,
    CirqGateOperation,
    CirqPauliString,
    CirqPauliSum,
    CirqQubit,
    is_cirq_gate_operation,
    is_cirq_grid_qubit,
    is_cirq_line_qubit,
    is_cirq_measurement,
    is_cirq_named_qubit,
    is_list_of_cirq_qubit,
)
from .utils import numpy_array_to_matrix_gate_dict


def serialize_cirq_circuit(
    circuit: CirqCircuit,
    cirq_to_json_serialization: bool = False,
    compress_rotations: bool = True,
) -> SerializedCircuit:
    """Convert a Cirq circuit to a SerializedCircuit with a list of dictionaries or cirq json string.

    In the former case, each dictionary represents a gate.

    Parameters
    ----------
    circuit
        A circuit from Cirq.
    cirq_to_json_serialization
        If False, the serialized circuit contains a list of dictionaries.
        If True, the serialized circuit contains a cirq JSON string.
    compress_rotations
        If True, certain rotations are reduced to other native gates. For example RZ(np.pi/2) ->  S.

    Returns
    -------
    serialized_circuit
        The serialized circuit.

    Raises
    ------
    ValueError
        If the circuit contains a gate that is not a known Cirq gate.
    """
    qubit_to_str_dict = {
        qubit: cirq_qubit_to_str(qubit) for qubit in circuit.all_qubits()
    }
    if cirq_to_json_serialization:
        cirq_json_string, has_intermediate_measurements = cirq_circuit_to_json_string(
            circuit
        )
        if has_intermediate_measurements:
            raise ValueError(
                "Cirq circuit contains intermediate measurements which are not supported for mode 'statevector'"
            )
        s_c = SerializedCircuit(
            circuit=cirq_json_string,
            type="cirq_json_string",
            qubits=tuple(qubit_to_str_dict.values()),
        )
    else:
        serialized_gates = [
            get_cirq_gate_dict(gate, qubit_to_str_dict, compress_rotations)
            for moment in circuit
            for gate in moment
            if not is_cirq_measurement(gate.gate)
        ]
        s_c = SerializedCircuit(circuit=serialized_gates, type="dict_list")

    return s_c


def get_cirq_gate_dict(
    gate: CirqGateOperation,
    qubit_to_str_dict: dict[CirqQubit, str],
    compress_rotations: bool,
) -> dict[str, Union[str, dict, tuple]]:
    """Get a dictionary representation of a single Cirq gate, which can be serialized to JSON.

    Parameters
    ----------
    gate
        The Cirq gate to convert.
    qubit_to_str_dict
        Dictionary mapping qubits to their string representation.
    compress_rotations
        If True, certain rotations are reduced to other native gates. For example RZ(np.pi/2) ->  S.

    Returns
    -------
    gate_dict
        Serialization of the gate.

    Raises
    ------
    NotImplementedError

        - If the gate is not supported.
        - If the gate acts on more than ``MAX_QUBITS_PER_GATE_OR_CHANNEL`` qubits.
    """
    if not is_cirq_gate_operation(gate):
        raise ValueError(
            f"Object that is not recognised as cirq GateOperation found in cirq circuit. Found type: {type(gate)}"
        )

    if hasattr(gate.gate, "_is_parameterized_"):
        assert (
            not gate.gate._is_parameterized_()
        ), "Parameterized circuits not supported yet for Cirq input. Please use Qiskit instead"

    gate_dict: dict[str, Union[str, dict, tuple]] = {}
    cirq_gate_name = gate.gate.__class__.__name__
    try:
        gate_dict["name"] = cirq_gate_map[cirq_gate_name]
        gate_dict["label"] = cirq_gate_name
    except KeyError:
        raise NotImplementedError(f"Cirq gate {cirq_gate_name} not supported")

    gate_dict["qubits"] = tuple(qubit_to_str_dict[qubit] for qubit in gate.qubits)

    n_gate_qubits = len(gate_dict["qubits"])
    if n_gate_qubits > MAX_QUBITS_PER_GATE_OR_CHANNEL:
        raise NotImplementedError(
            f"Gates on more than {MAX_QUBITS_PER_GATE_OR_CHANNEL} qubits are currently not supported; gate {cirq_gate_name} acts on {n_gate_qubits} qubits"
        )

    gate_dict["params"] = {}

    # Different variations of the RZ-gate
    if gate_dict["name"] == "RZ":
        e_mod_2 = gate.gate.exponent % 2
        if compress_rotations and np.any(
            np.isclose(e_mod_2, [1.75, 1.5, 1, 0.5, 0.25, 0])
        ):
            if np.isclose(e_mod_2, 0):
                gate_dict["name"] = "I"
            if np.isclose(e_mod_2, 0.5):
                gate_dict["name"] = "S"
            elif np.isclose(e_mod_2, 1.5):
                gate_dict["name"] = "SDG"
            elif np.isclose(e_mod_2, 0.25):
                gate_dict["name"] = "T"
            elif np.isclose(e_mod_2, 1.75):
                gate_dict["name"] = "TDG"
            elif np.isclose(e_mod_2, 1):
                gate_dict["name"] = "Z"

        else:
            gate_dict["params"] = {"rads": gate.gate.exponent * np.pi}

    # Rotation gates, defined with radians
    elif gate_dict["name"] in ("RX", "RY", "RH", "RXX", "RYY", "RZZ"):
        e_mod_2 = gate.gate.exponent % 2
        if compress_rotations and np.any(np.isclose(e_mod_2, [0, 1])):
            if np.isclose(e_mod_2, 0):
                gate_dict["name"] = "I"
            elif np.isclose(e_mod_2, 1):
                gate_dict["name"] = gate_dict["name"][1:]
        else:
            gate_dict["params"] = {"rads": float(gate.gate.exponent * np.pi)}

    # POW gates, defined with exponent
    elif gate_dict["name"] in ("CXPOW", "CZPOW", "SWAPPOW", "ISWAPPOW", "CCXPOW"):
        e_mod_2 = gate.gate.exponent % 2
        if compress_rotations and np.any(np.isclose(e_mod_2, [0, 1])):
            if np.isclose(e_mod_2, 0):
                gate_dict["name"] = "I"
            elif np.isclose(e_mod_2, 1):
                gate_dict["name"] = gate_dict["name"][:-3]
        else:
            gate_dict["params"] = {"exponent": float(gate.gate.exponent)}

    # Other gates, defined with some other parameters
    elif gate_dict["name"] in ("PhasedXPOW", "PhasedXZ", "FSIM", "PhasedFSIM"):
        params = {}
        for attr in (
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
        ):
            if hasattr(gate.gate, attr):
                params[attr] = float(getattr(gate.gate, attr))
        gate_dict["params"] = params
    # Matrix gates, defined with a matrix
    elif gate_dict["name"] == "Gate":
        matrix = gate.gate._matrix.copy()
        gate_dict["params"] = numpy_array_to_matrix_gate_dict(matrix)
        # Use the label of the unitary (if given) as the label of the gate
        if gate.gate._name is not None:
            gate_dict["label"] = gate.gate._name

    else:
        raise ValueError(f"Gate {cirq_gate_name} : {gate_dict['name']} not supported")

    return gate_dict


def default_qubits_cirq(circuit: CirqCircuit) -> list[CirqQubit]:
    """Returns a list of qubits in a Cirq circuit, ordered according to the default ordering of Cirq.

    Parameters
    ----------
    circuit
        A Cirq circuit.

    Returns
    -------
    qubits
        The qubits in the circuit.

    Raises
    ------
    ImportError
        If Cirq is not installed.
    """

    try:
        import cirq  # Safe to import here since this function can only be called if cirq is installed
    except ImportError:
        raise ImportError("A cirq qubit object was found, but Cirq is not installed.")

    all_qubits = circuit.all_qubits()
    explicit_qubit_objects = list(cirq.QubitOrder.DEFAULT.order_for(all_qubits))  # type: ignore
    if is_list_of_cirq_qubit(explicit_qubit_objects):
        explicit_qubit_objects_typed: list[CirqQubit] = list(explicit_qubit_objects)
        return explicit_qubit_objects_typed
    return []


def cirq_qubit_to_str(qubit: CirqQubit) -> str:
    """Converts a Cirq qubit to a string representation.

    Parameters
    ----------
    qubit
        A Cirq qubit.

    Returns
    -------
    q_label
        The string representation of the qubit.

    Raises
    ------
    TypeError
        If the qubit is not a Cirq qubit.
    """
    if is_cirq_line_qubit(qubit):
        q_label = f"{qubit.x}"
    elif is_cirq_grid_qubit(qubit):
        q_label = f"({qubit.row}, {qubit.col})"
    elif is_cirq_named_qubit(qubit):
        q_label = qubit.name
    else:
        raise TypeError(f"Unknown qubit type {type(qubit)}.")
    return q_label


def convert_cirq_pauli(
    cirq_obs: CirqPauliSum | CirqPauliString, name: str
) -> PauliSumObservable:
    """Constructs an instance of the PauliObservable class from a cirq PauliSum or PauliString.

    Each PauliString consists of a sequence of Pauli gates, every gate acting
    on a different qubit (as per cirq's PauliString description). If a Pauli
    is encountered that acts on a qubit that already has another Pauli acting
    on it, an error will be thrown.

    Parameters
    ----------
    cirq_obs
        A cirq PauliSum or PauliString object.
    name
        A string specifying the name of the operator.

    Returns
    -------
    pauli_observable
        An instance of the PauliObservable class representing the input PauliSum or PauliString.

    Raises
    ------
    ValueError
        If a qubit has more than one Pauli acting on it.
    """

    # Convert to list of PauliStrings if input is a single PauliString
    if isinstance(cirq_obs, CirqPauliString):
        cirq_obs = [cirq_obs]

    # Pauli_mask returns an integer, which corresponds to a Pauli according to:
    mask_to_string = ["I", "X", "Y", "Z"]

    terms = []
    for pauli_string in cirq_obs:
        # Dictionary from qubit labels to Pauli operators (as strings)
        qubit_to_pauli: dict[str, str] = {}
        coeff = pauli_string.coefficient

        for qubit, pauli_idx in zip(pauli_string.qubits, pauli_string.gate.pauli_mask):
            # Only store non-identity Pauli's
            if pauli_idx != 0:
                qubit_label = cirq_qubit_to_str(qubit)
                if qubit not in qubit_to_pauli:
                    qubit_to_pauli[qubit_label] = mask_to_string[pauli_idx]
                else:
                    raise ValueError(
                        f"Qubit {qubit_label} already has a Pauli {qubit_to_pauli[qubit_label]} acting on it."
                    )
        terms.append(PauliProductTerm(paulis=qubit_to_pauli, coeff=coeff))

    return PauliSumObservable(terms=terms, name=name)


def cirq_circuit_to_json_string(circuit: CirqCircuit) -> tuple[str, bool]:
    try:
        import cirq  # Safe to import here since this function can only be called if cirq is installed
    except ImportError:
        raise ImportError(
            "Trying to serialize a Cirq circuit to JSON, but Cirq is not installed."
        )

    has_intermediate_measurements = not circuit.are_all_measurements_terminal()

    return cirq.to_json(circuit), has_intermediate_measurements
