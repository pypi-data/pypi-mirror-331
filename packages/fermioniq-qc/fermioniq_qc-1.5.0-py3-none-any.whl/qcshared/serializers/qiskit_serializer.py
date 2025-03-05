import base64
import os
import tempfile
import warnings
from typing import Any, Sequence, Union

from packaging.version import Version

from ..io.observables import PauliProductTerm, PauliSumObservable
from ..utils.constants import MAX_QUBITS_PER_GATE_OR_CHANNEL
from ..utils.gate_maps import qiskit_gate_map
from .circuit import SerializedCircuit
from .custom_types import (
    QiskitCircuit,
    QiskitCircuitOperation,
    QiskitQubit,
    QiskitSparsePauliOp,
)
from .utils import numpy_array_to_matrix_gate_dict, reorder_gate_matrix


def serialize_qiskit_circuit(
    circuit: QiskitCircuit,
    qpy_serialization: bool = False,
) -> SerializedCircuit:
    """Convert a Qiskit circuit to a a SerializedCircuit with a list of dictionaries or a qpy binary string.

    In the former case, Each dictionary represents a gate in the circuit.

    Parameters
    ----------
    circuit :
        The Qiskit circuit to convert.
    qpy_serialization :
        If False, the serialized circuit contains a list of dictionaries.
        If True, the serialized circuit contains a qpy binary string.

    Returns
    -------
    serialized_circuit :
        A list of dictionaries representing the circuit.
    """
    # Assign to each qubit a unique string identifier
    qubit_to_str_dict = {
        q: qiskit_qubit_to_str(q) for gate in circuit.data for q in gate.qubits
    }
    if qpy_serialization:

        (
            qpy_binary_string,
            has_intermediate_measurements,
        ) = qiskit_circuit_to_qpy_binary_string(circuit)
        if has_intermediate_measurements:
            raise ValueError(
                "The received qiskit circuit contains intermediate measurements. This is not supported for mode = 'statevector'"
            )
        s_c = SerializedCircuit(
            circuit=qpy_binary_string,
            type="qpy_binary_string",
            qubits=tuple(qubit_to_str_dict.values()),
        )

    else:
        filtered_gates = filter_barriers_and_measurements(circuit.data)
        dict_list = [
            get_qiskit_gate_dict(gate, qubit_to_str_dict) for gate in filtered_gates
        ]
        s_c = SerializedCircuit(circuit=dict_list, type="dict_list")

    return s_c


def filter_barriers_and_measurements(
    instructions: Sequence[QiskitCircuitOperation],
) -> list[QiskitCircuitOperation]:
    """Filter out all barriers and measurements from a list of qiskit circuit instructions.

    Raise an error if the circuit contains intermediate measurements, and warns the user if
    the circuit contains measurements at the end of the circuit.

    Parameters
    ----------
    instructions :
        The Qiskit circuit instructions to filter.

    Returns
    -------
    filtered_instructions :
        A list with the instructions, from which barriers and measruements have been filtered.

    Raises
    ------
    ValueError
        If the circuit contains intermediate measurements.
    warnings.warn
        If the circuit contains measurements at the end of the circuit.
    """
    indices_to_filter = []
    measurement_indices_qubits = []

    for instruction_index, instruction in enumerate(instructions):
        if instruction.operation.name == "barrier":
            indices_to_filter.append(instruction_index)

        elif instruction.operation.name == "measure":
            measurement_indices_qubits.append((instruction_index, instruction.qubits))

    if measurement_indices_qubits:
        measurement_indices, _ = zip(*measurement_indices_qubits)
    else:
        measurement_indices = ()
    for i in reversed(range(len(instructions))):
        if i in measurement_indices:
            warnings.warn(
                "Encountered measurements at the end of the qiskit circuit. These are currently ignored. Please specify bitstring sampling in the config dictionary instead",
                stacklevel=2,
            )
            indices_to_filter.append(i)
        else:
            break

    return [ins for i, ins in enumerate(instructions) if i not in indices_to_filter]


def parse_param_gate_expr(params: Any) -> dict[str, str | dict[str, float]]:
    """Attempts to convert any linear expressions of a variable parameter to dict.

    The output will contain the global name of the parameter as well as a dict
    of linear coefficients that specify the expression.
    E.g. if the expression was -2 * p1 + 3, we get
    linear_coeffs = {"0": 3.0, "1": -2.0}, where the keys correspond to the order
    of each term in the linear expression.

    Parameters
    ----------
    params
        Variable parameter property of qiskit gate.

    Returns
    -------
    parsed_params
        Dict containing the global name of the variable parameter and linear
        coefficients.
    """
    coeffs = params.sympify().as_coefficients_dict()
    if len(params.parameters) > 1:
        raise ValueError(
            f"Gate contained {len(params.parameters)} variable parameters. Only 1 allowed"
        )
    (param,) = params.parameters
    linear_coeffs = {
        "0": float(coeffs[1]),
        "1": float(coeffs[param.sympify()]),
    }
    if linear_coeffs["1"] == 0:
        raise ValueError("Gate with variable parameter does not depend on parameter.")
    if len(coeffs) > 2:
        raise ValueError(
            "Gates can only contain linear expressions for variable parameters. "
            f"Got: {params}"
        )
    return {"name": param.name, "linear_coeffs": linear_coeffs}


def get_qiskit_gate_dict(
    gate: QiskitCircuitOperation,
    qubit_to_str_dict: dict[QiskitQubit, str],
) -> dict[str, Union[str, dict, tuple]]:
    """Get a dictionary representation of a qiskit gate, which is compatible with JSON serialization.

    Parameters
    ----------
    gate :
        The Qiskit gate to convert.
    qubit_to_str_dict :
        Dictionary mapping qiskit qubits to strings (as returned by qiskit_qubit_to_str).

    Returns
    -------
    gate_dict :
        A dictionary representation of the gate.

    Raises
    ------
    NotImplementedError

        - If the gate is not supported yet
        - If the gate acts on more than MAX_QUBITS_PER_GATE_OR_CHANNEL qubits
    """
    gate_dict: dict[str, str | dict[str, float] | dict[str, str] | tuple] = {}
    qiskit_gate_name = gate.operation.name

    try:
        gate_dict["name"] = qiskit_gate_map[qiskit_gate_name]
        gate_dict["label"] = qiskit_gate_name
    except KeyError:
        raise NotImplementedError(
            f"Qiskit gate {qiskit_gate_name} not supported yet, please use a unitary gate with the corresponding numpy array instead"
        )

    gate_dict["qubits"] = tuple(qubit_to_str_dict[qubit] for qubit in gate.qubits)

    n_gate_qubits = len(gate_dict["qubits"])
    if n_gate_qubits > MAX_QUBITS_PER_GATE_OR_CHANNEL:
        raise NotImplementedError(
            f"Gates on more than {MAX_QUBITS_PER_GATE_OR_CHANNEL} qubits are currently not supported; gate {qiskit_gate_name} acts on {n_gate_qubits} qubits"
        )

    param_dict: dict[str, float] = {}
    variable_param_dict: dict[str, str] = {}

    def _update_param_dicts(_name, _value):  # numpydoc ignore=SS03,PR01
        """Update one or both dicts depending on whether the gate contains variable params"""
        if hasattr(_value, "parameters"):
            # Try to extract the global variable parameter name and linear coefficients.
            # This function will raise a ValueError if the expression is not linear,
            # contains multiple independent parameters or does not actually depend
            # on any parameter (e.g. expression is 'p1 - p1')
            _parsed_param = parse_param_gate_expr(_value)
            param_dict[_name] = 0.0
            variable_param_dict[_name] = _parsed_param  # type: ignore
        else:
            param_dict[_name] = float(_value)

    if gate_dict["name"] in (
        "P",
        "RX",
        "RY",
        "RZ",
        "CRZ",
        "CRX",
        "CRY",
        "RXX",
        "RYY",
        "RZZ",
    ):
        _update_param_dicts("rads", gate.operation.params[0])

    elif gate_dict["name"] == "R":
        _update_param_dicts("theta", gate.operation.params[0])
        _update_param_dicts("phi", gate.operation.params[1])

    elif gate_dict["name"] in ("U", "CU"):
        _update_param_dicts("theta", gate.operation.params[0])
        _update_param_dicts("phi", gate.operation.params[1])
        _update_param_dicts("lam", gate.operation.params[2])

        if gate_dict["name"] == "CU":
            _update_param_dicts("gamma", gate.operation.params[3])

    elif gate_dict["name"] == "Gate":
        matrix = gate.operation.to_matrix()
        re_ordered_matrix = reorder_gate_matrix(matrix)
        param_dict = numpy_array_to_matrix_gate_dict(re_ordered_matrix)

        # Use the label of the gate (if given) as the label of the serialized gate
        if gate.operation.label is not None:
            gate_dict["label"] = gate.operation.label

    elif gate_dict["name"] in ["QubitMeasurement"]:
        try:
            (clbit,) = gate.clbits
        except ValueError:
            raise ValueError(
                "Gates that write to more than one classical bit are not supported."
            )
        param_dict["register_name"] = clbit.register.name
        param_dict["register_index"] = clbit.index
        param_dict["register_size"] = clbit.register.size

    if (condition := gate.operation.condition) is not None:
        gate_dict["condition"] = {
            "register_name": condition[0].name,
            "register_value": condition[1],
        }

    gate_dict["params"] = param_dict
    if variable_param_dict:
        gate_dict["variable_params"] = variable_param_dict

    return gate_dict


def default_qubits_qiskit(circuit: QiskitCircuit) -> list[QiskitQubit]:
    return circuit.qubits


def qiskit_qubit_to_str(qubit: QiskitQubit) -> str:
    # Compatible with qiskit v1
    if hasattr(qubit, "_register"):
        return f"{qubit._register.name}_{qubit._register.index(qubit)}"
    # Compatible with qiskit v0
    else:
        return f"{qubit.register.name}_{qubit._register.index(qubit)}"


def convert_qiskit_sparse_pauli_op(
    qiskit_obs: QiskitSparsePauliOp, qubits: list[str], name: str
) -> PauliSumObservable:
    """Constructs an instance of the PauliObservable class from a qiskit SparsePauliOp.

    Since the qiskit SparsePauliOp does not contain information about the qubits that
    it acts on, we assume that it acts on all qubits given in ``qubits``.

    Parameters
    ----------
    qiskit_obs :
        Qiskit SparsePauliOp.
    qubits :
        List of qubit labels (as strings, i.e. already serialized).
    name :
        String specifying the name of the operator.

    Returns
    -------
    pauli_observable :
        An instance of the PauliSumObservable class representing the input SparsePauliOp.

    Raises
    ------
    ValueError

        - If the number of qubits in the qiskit operator does not match the number of qubits in ``qubits``
        - If the qiskit operator contains multiple Pauli's acting on the same qubit
    """

    if qiskit_obs.num_qubits != len(qubits):
        raise ValueError(
            f"""Number of qubits ({qiskit_obs.num_qubits}) in qiskit operator does not
            match number of qubits ({len(qubits)}) in 'qubits'."""
        )

    # Store operator term-by-term
    terms = []
    for coeff, pauli_string in zip(qiskit_obs.coeffs, qiskit_obs.paulis):
        # Dictionary from qubit labels to Pauli operators (as strings)
        qubit_to_pauli: dict[str, str] = {}

        # read string from right to left
        for idx, pauli in enumerate(pauli_string):
            qubit_label = qubits[idx]

            # Only store non-identity Pauli's
            if str(pauli) != "I":
                if qubit_label not in qubit_to_pauli:
                    qubit_to_pauli[qubit_label] = str(pauli)
                else:
                    raise ValueError(
                        f"Qubit {qubit_label} already has a Pauli {qubit_to_pauli[qubit_label]} acting on it."
                    )
        terms.append(PauliProductTerm(paulis=qubit_to_pauli, coeff=coeff))

    return PauliSumObservable(terms=terms, name=name)


def qiskit_circuit_to_qpy_binary_string(circuit: QiskitCircuit) -> tuple[str, bool]:
    """Convert a Qiskit circuit to a binary string.

    Currently only used for mode='statevector'.

    Parameters
    ----------
    circuit :
        The Qiskit circuit to convert.

    Returns
    -------
    binary_string :
        A binary string representation of the circuit.
    has_intermediate_measurements
        True if the circuit contains intermediate measurements, False otherwise.

    Raises
    ------
    ImportError
        If qiskit is not installed.
    RuntimeError
        If the qiskit version is 1.0 or higher.
    """
    import io

    try:
        import qiskit
        from qiskit import qpy
    except ImportError:
        raise ImportError(
            "Trying to serialize a Qiskit circuit, but Qiskit (qpy) is not installed."
        )

    byte_stream = io.BytesIO()

    # Encode the binary circuit as a base64 string
    if Version(qiskit.__version__) >= Version("1.0.0"):
        qpy.dump(circuit, byte_stream, version=11)
    else:
        qpy.dump(circuit, byte_stream)

    qpy.dump(circuit, byte_stream)

    qpy_binary_string = base64.b64encode(byte_stream.getvalue()).decode("utf-8")

    return qpy_binary_string, qiskit_has_intermediate_measurements(circuit)


def qiskit_has_intermediate_measurements(circuit: QiskitCircuit) -> bool:
    """Check if a Qiskit circuit contains intermediate measurements.

    Parameters
    ----------
    circuit :
        The Qiskit circuit to check.

    Returns
    -------
    has_intermediate_measurements :
        True if the circuit contains intermediate measurements, False otherwise.
    """
    qubits_with_measurement: set[QiskitQubit] = set()
    for instr, qubits, class_regs in circuit.data:
        if instr.name == "measure":
            qubits_with_measurement.add(*qubits)
        elif any(qubit in qubits_with_measurement for qubit in qubits):
            return True

    return False
