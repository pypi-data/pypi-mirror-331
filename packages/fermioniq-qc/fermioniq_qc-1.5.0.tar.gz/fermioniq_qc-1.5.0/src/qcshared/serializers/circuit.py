from typing import Any, Literal, Optional

from pydantic import Field, field_validator

from qcshared.pydantic.models import BaseConfig


class SerializedCircuit(BaseConfig):
    type: Literal["dict_list", "qpy_binary_string", "cirq_json_string"]
    circuit: list[dict[str, Any]] | str
    qubits: Optional[tuple[str, ...]] = Field(default=None, validate_default=True)

    @field_validator("circuit")
    @classmethod
    def validate_circuit(cls, circuit, info):
        """Validation of the circuit.

        Parameters
        ----------
        circuit
            Circuit to be validated.
        values
            Values of the model.

        Raises
        ------
        ValueError
            If type = 'qpy_binary_string' or 'cirq_json_string' and circuit is not a string.
            If type = 'dict_list' and circuit is not a list of dictionaries.
            If type = 'dict_list' and a gate in the circuit is missing 'qubits' field.
            If type = 'dict_list' and a gate in the circuit is missing 'name' or 'label' field.

        TypeError
            If type = 'dict_list' and the type of 'qubits' is not list or tuple.
        """

        # Only checks that the circuit is a string
        if info.data["type"] != "dict_list":
            if not isinstance(circuit, str):
                raise ValueError(
                    f"If SerializedCircuit has type 'qpy_binary_string' or 'cirq_json_string', the circuit must be a string, but found: {type(circuit)}"
                )
            return circuit

        # Check that the circuit is a list of dicts
        if not (
            isinstance(circuit, list)
            and all(isinstance(gate_dict, dict) for gate_dict in circuit)
        ):
            raise ValueError(
                "If SerializedCircuit has type 'dict_list', circuit must be a list of dictionaries."
            )

        # Check that each gate has a 'qubits', and 'name' or 'label' field
        for gate_dict in circuit:
            try:
                qubits = gate_dict["qubits"]
                assert isinstance(qubits, list) or isinstance(qubits, tuple), TypeError(
                    "Type of qubits must be list or tuple"
                )
                gate_dict["qubits"] = tuple(qubits)
            except:
                raise ValueError(
                    "Not all items in the payload have a 'qubits' field containing a list or tuple of labels"
                )
            if "name" not in gate_dict or "label" not in gate_dict:
                raise ValueError(
                    "Not all items in the payload have a 'name' and 'label' field"
                )
        return circuit

    @field_validator("qubits")
    @classmethod
    def validate_qubits(cls, qubits, info):
        """Validation of the qubits.

        Parameters
        ----------
        qubits
            Qubits to be validated.
        values
            Values of the model.

        Raises
        ------
        ValueError
            If type = 'qpy_binary_string' or 'cirq_json_string', and qubits are not provided.
            If type = 'dict_list' and gates do not contain 'qubits'.
        """
        if info.data.get("type") == "dict_list":
            return get_qubits_from_circuit_dict_list(info.data.get("circuit"))

        if qubits is None:
            raise ValueError(
                "If circuit is given as qpy or cirq json, qubits must be provided"
            )

        return qubits


def get_qubits_from_circuit_dict_list(
    circuit_dict_list: list[dict[str, Any]]
) -> tuple[str, ...]:
    """Extract qubits from a serialized circuit.

    Parameters
    ----------
    circuit_dict_list :
        List of dictionaries representing the circuit.

    Returns
    -------
    qubits
        Sorted tuple of qubits that appear in the circuit.
    """
    qubits = set()
    try:
        for gate in circuit_dict_list:
            qubits.update(gate["qubits"])
    except KeyError:
        raise ValueError("Gate in serialized circuit missing 'qubits' field")
    except Exception:
        raise ValueError("Serialized circuit could not be parsed")
    return tuple(sorted(qubits))
