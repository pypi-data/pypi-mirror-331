from copy import deepcopy
from typing import Any, Sequence

from qcshared.io.observables import PauliSumObservable

from .circuit import SerializedCircuit, get_qubits_from_circuit_dict_list
from .cirq_serializer import (
    cirq_qubit_to_str,
    convert_cirq_pauli,
    default_qubits_cirq,
    serialize_cirq_circuit,
)
from .custom_types import (
    Circuit,
    CirqQubit,
    QiskitQubit,
    Qubit,
    is_cirq_circuit,
    is_cirq_pauli_string,
    is_cirq_pauli_sum,
    is_cirq_qubit,
    is_qiskit_circuit,
    is_qiskit_qubit,
    is_qiskit_sparse_pauli_op,
    is_sequence_of_cirq_qubit,
    is_sequence_of_qiskit_qubit,
    is_sequence_of_str_qubit,
)
from .qiskit_serializer import (
    convert_qiskit_sparse_pauli_op,
    default_qubits_qiskit,
    qiskit_qubit_to_str,
    serialize_qiskit_circuit,
)


def serialize_circuit(
    circuit: Circuit | list[dict], third_party_serialization: bool = False
) -> SerializedCircuit:
    """Converts a circuit from a 3rd-party quantum programming framework or as list of dicts to a SerializedCircuit object.

    Currently supported frameworks: Cirq, Qiskit.

    Parameters
    ----------
    circuit :
        The circuit to serialize.
    third_party_serialization :
        If False, the circuit is serialized as a list of dictionaries.
        If True, the circuit is serialized in qiskit's or cirq's native format, and then must be provided as cirq or qiskit circuit.

    Returns
    -------
    serialized_circuit :
        A SerializedCircuit.

    Raises
    ------
    ValueError
        If third_party_serialization is True and the circuit is not in a recognized third party format.
    TypeError
        If the circuit is not a recognized type.
    """

    if is_qiskit_circuit(circuit):
        return serialize_qiskit_circuit(
            circuit, qpy_serialization=third_party_serialization
        )
    elif is_cirq_circuit(circuit):
        return serialize_cirq_circuit(
            circuit, cirq_to_json_serialization=third_party_serialization
        )
    elif third_party_serialization:
        raise ValueError(
            "Third party (statevector) serialization is only supported for Qiskit and Cirq circuits."
        )
    elif isinstance(circuit, list) and all(isinstance(g, dict) for g in circuit):
        return SerializedCircuit(circuit=circuit, type="dict_list")
    else:
        raise TypeError(
            f"Circuit type '{type(circuit)}' not recognized for serialization, provide a cirq or qiskit circuit."
        )


def serialize_qubits(
    qubits: Sequence[Qubit],
) -> tuple[str, ...]:
    """Convert qubits objects to string representation.

    Given a sequence of qubit objects (e.g. Cirq Qid objects, Qiskit Qubit objects, etc.),
    convert to tuple of string labels representing the qubits.

    Parameters
    ----------
    qubits :
        Sequence of qubit objects.

    Returns
    -------
    qubit_labels :
        Tuple of qubit labels.

    Raises
    ------
    TypeError
        If the qubit objects are not recognized.
    """
    if is_sequence_of_qiskit_qubit(qubits):
        return tuple(qubit_to_str(q) for q in qubits)
    if is_sequence_of_cirq_qubit(qubits):
        return tuple(qubit_to_str(q) for q in qubits)
    if is_sequence_of_str_qubit(qubits):
        return tuple(qubits)
    raise ValueError(
        f"Qubit sequence not recognized, should be either tuple, list, or register containin cirq qubits or qiskit qubits"
    )


def get_default_qubit_objects(
    circuit: Circuit,
) -> list[QiskitQubit] | list[CirqQubit]:
    if is_cirq_circuit(circuit):
        return default_qubits_cirq(circuit)
    if is_qiskit_circuit(circuit):
        return default_qubits_qiskit(circuit)
    raise ValueError(f"Unrecognized circuit type {type(circuit)}.")


def qubit_to_str(qubit: Qubit) -> str:
    if is_cirq_qubit(qubit):
        return cirq_qubit_to_str(qubit)
    if is_qiskit_qubit(qubit):
        return qiskit_qubit_to_str(qubit)
    if isinstance(qubit, str):
        return qubit
    raise ValueError(f"Unrecognized qubit type {type(qubit)}.")


def serialize_observable(
    name: str, observable: Any, qubits: list[str]
) -> dict[str, Any]:
    """Serialize an observable to a dictionary.

    Parameters
    ----------
    name :
        Name of the observable.
    observable :
        The observable to serialize.
    qubits :
        The qubits (already serialized, i.e. as strings).

    Returns
    -------
    serialized_observable :
        A dictionary representation of the observable.

    Raises
    ------
    TypeError
        If the observable is not a recognized type.
    """

    if is_qiskit_sparse_pauli_op(observable):
        return convert_qiskit_sparse_pauli_op(observable, qubits, name).model_dump()
    elif is_cirq_pauli_string(observable) or is_cirq_pauli_sum(observable):
        return convert_cirq_pauli(observable, name).model_dump()
    elif isinstance(observable, PauliSumObservable):
        return PauliSumObservable(name=name, terms=observable.terms).model_dump()

    else:
        raise TypeError(
            f"Observable type {type(observable)} not recognized. Must be one of cirq.PauliString, cirq.PauliSum, or qiskit.SparsePauliOp."
        )


def serialize_config(config_dict: dict[str, Any]) -> dict[str, Any]:
    """Fully serialize a config dict to a dictionary representation that can be serialized to JSON.

    Currently this involves:

    - Serializing the qubit order
    - Serializing the grouping (if present)
    - Serializing the observables (if present)

    Parameters
    ----------
    config_dict :
        The config dict to serialize.

    Returns
    -------
    serialized_config :
        The serialized config dict.

    Raises
    ------
    ValueError
        If the grouping is not a list of lists of qubits.
    """

    # Make a deep copy of the config
    conf_dict = deepcopy(config_dict)

    # Serialize the qubits
    conf_dict["qubits"] = serialize_qubits(conf_dict["qubits"])

    # Serialize the grouping and the qubits
    grouping = conf_dict.get("grouping", None)
    if grouping is not None:
        if not all(isinstance(group, list) for group in conf_dict["grouping"]):
            raise ValueError("'grouping' should be a list of lists of qubits")

        conf_dict["grouping"] = [[qubit_to_str(q) for q in group] for group in grouping]

    if "expectation_values" in conf_dict["output"]:
        observables = conf_dict["output"]["expectation_values"].get("observables")
        if isinstance(observables, dict):
            conf_dict["output"]["expectation_values"]["observables"] = [
                serialize_observable(name, obs, conf_dict["qubits"])
                for name, obs in observables.items()
            ]
        else:
            raise ValueError(
                f"'observables' should be a dictionary where each key is the names of the observable and the value is a qiskit or cirq observable. "
            )

    if "optimizer" in conf_dict:
        observable = conf_dict["optimizer"].get(
            "observable", None
        )  # check if not multiple
        if isinstance(observable, dict) and len(observable) == 1:
            name, obs = next(iter(observable.items()))
            conf_dict["optimizer"]["observable"] = serialize_observable(
                name, obs, conf_dict["qubits"]
            )
        else:
            raise ValueError(
                f"'observable' should be a dict containing a single observable and its name. {len(observable)} given"
            )

    return conf_dict
