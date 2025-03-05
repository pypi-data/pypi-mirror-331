import logging
from typing import Any, Optional

from pydantic import ValidationError, field_validator, model_validator

from ..json.decode import dejsonify
from ..json.encode import jsonify
from ..messaging.message import ConfigMessage
from ..noise_models import ANY, NoiseModel, QubitInternal
from ..serializers import SerializedCircuit
from .config_utils import BaseConfigWithWarning
from .constants import (
    MAX_STATEVECTOR_QUBITS_NO_NOISE,
    MPO_BOND_DIM_NO_NOISE,
    MPO_BOND_DIM_WITH_NOISE,
)
from .emulator_config import EmulatorConfig


def validate_input(
    serialized_circuit: SerializedCircuit,
    config: EmulatorConfig,
    noise_model: Optional[NoiseModel],
    print_warnings: bool = False,
) -> "EmulatorInput":
    """Validates the emulator input against the emulator config, and returns the validated input.

    Parameters
    ----------
    circuit :
        The circuit.
    config :
        The emulator config.
    noise_model :
        The noise model.
    print_warnings :
        Whether to print warnings or not.

    Returns
    -------
    emulator_input :
        The validated emulator input.

    Raises
    ------
    ValidationError :
        If the input is invalid. See the error message for details.
    """
    try:
        emulator_input = EmulatorInput(
            emulator_config=config,
            serialized_circuit=serialized_circuit,
            noise_model=noise_model,
        )
        if emulator_input._warnings:
            warnings = list(set(emulator_input._warnings))
            if print_warnings:
                logging.warning(ConfigMessage(warnings, []))

        return emulator_input
    except ValidationError as e:
        logging.error(ConfigMessage([], e.errors(include_context=False)))
        print(e.errors())
        raise e


def validate_input_batch(
    emulator_inputs: list[
        tuple[SerializedCircuit, EmulatorConfig, Optional[NoiseModel]]
    ]
) -> list["EmulatorInput"]:
    """Validates a batch of emulator inputs against the emulator config, and returns the validated inputs.

    Note that to use this function with multiprocessing, it can only take a single argument, which is why
    it does that, and as a first step unpacks that single argument into three below.

    Parameters
    ----------
    emulator_inputs
        This is a list of tuples with 3 elements, where each tuple contains a circuit,
        a config, and optionally a noise model.

    Returns
    -------
    emulator_inputs
        This is a list of EmulatorInput objects, which are validated against the emulator config.
    """
    circuits = [emulator_input[0] for emulator_input in emulator_inputs]
    configs = [emulator_input[1] for emulator_input in emulator_inputs]
    noise_dicts = [emulator_input[2] for emulator_input in emulator_inputs]
    return list(map(validate_input, circuits, configs, noise_dicts))


class EmulatorInput(BaseConfigWithWarning):
    """This is a class for the emulator input.

    It knows about the emulator config, the serialized circuit, and the noise model, and can validate
    these against each other.
    """

    serialized_circuit: SerializedCircuit
    emulator_config: EmulatorConfig
    noise_model: Optional[NoiseModel] = None

    @model_validator(mode="after")
    def validate_config_circuit(self):
        """Post-validation on circuit + config"""

        s_c = self.serialized_circuit

        circuit_qubits = s_c.qubits
        config_qubits = self.emulator_config.qubits

        if any(q not in config_qubits for q in circuit_qubits):
            erronous_qubits = (q for q in circuit_qubits if q not in config_qubits)
            raise ValueError(
                "The circuit acts on one or more erronous qubits that are not contained in "
                f"'qubits'. Erronous qubits: {','.join(erronous_qubits)}"
            )

        if self.emulator_config.mode == "statevector":
            if len(config_qubits) > MAX_STATEVECTOR_QUBITS_NO_NOISE:
                raise ValueError(
                    f"Statevector mode is only supported for at most {MAX_STATEVECTOR_QUBITS_NO_NOISE} qubits, but the config contains {len(config_qubits)} qubits."
                )

            if s_c.type == "dict_list":
                raise ValueError(
                    "When using 'mode' = 'statevector', the circuit must be serialized as 'qpy_binary_string' or 'cirq_json_string'."
                )

            if self.emulator_config.optimizer.enabled:
                raise ValueError(
                    "When using 'mode' = 'statevector', 'optimizer' must be False. Please change either 'mode' or 'optimizer' in the config."
                )

        else:
            if s_c.type != "dict_list":
                raise ValueError(
                    "When using 'mode' = 'dmrg' or 'tebd', the circuit must be serialized as 'dict_list'."
                )

            if self.emulator_config.mode == "tebd" and long_range_gates(
                s_c.circuit, self.emulator_config.grouping
            ):
                raise ValueError(
                    "Emulation mode tebd cannot be used when there are long-range gates in "
                    "the circuit. Please adjust the grouping or use a different emulation "
                    "mode (e.g. dmrg)."
                )

            if (
                self.emulator_config.optimizer.enabled
                and self.emulator_config.optimizer.initial_param_values
            ):

                def _get_param_name(_param: str | dict) -> str:
                    if isinstance(_param, str):
                        return _param
                    elif isinstance(_param, dict):
                        if "name" not in _param:
                            raise ValueError(
                                "Parameter dict withoud name found in parameterized circuit."
                            )
                        return _param["name"]
                    else:
                        raise ValueError(
                            f"Variable param '{_param}' could not be parsed"
                        )

                # Gather variable params from circuit
                params_circuit = {
                    _get_param_name(param)
                    for gate in s_c.circuit
                    for param in gate.get("variable_params", {}).values()
                }
                params_config = set(self.emulator_config.optimizer.initial_param_values)
                if params_not_in_circuit := params_config - params_circuit:
                    raise ValueError(
                        "One or more variable parameters in initial_param_values "
                        f"do not appear in circuit: {params_not_in_circuit}."
                    )

                if params_not_in_config := params_circuit - params_config:
                    raise ValueError(
                        "One or more variable parameters in circuit "
                        f"are not specified in initial_param_values: {params_not_in_config} "
                        "Either specify all initial parameter values or none."
                    )
        return self

    @model_validator(mode="after")
    def validate_noise_model(self):
        """Validates the noise model against the config and circuit.

        Raises
        ------
        ValueError :

            - If no mpo_bond_dim has been specified for 'dmrg', this is filled with a default, depending on the existence
                of a noise model.
            - If a noise model is given, the noise 'enabled' flag is set to true, for later output processing.
            - If a noise model is given, the mpo_bond_dim must be >= 16. otherwise it should be >= 4.
            - If the noise config specifies to validate the noise model, then the noise model must be valid, which means:
                - Every gate in the circuit must trigger some noise channels
                - All qubits defined in the config (not necessarily the circuit) must have some readout error defined
        """

        # No noise model given
        if self.noise_model is None:
            if self.emulator_config.mode == "dmrg":
                if self.emulator_config.dmrg.mpo_bond_dim is None:
                    self.emulator_config.dmrg.mpo_bond_dim = MPO_BOND_DIM_NO_NOISE
                elif self.emulator_config.dmrg.mpo_bond_dim < 4:
                    raise ValueError(
                        "MPO bond dim. should be at least 4 for noiseless emulation."
                    )
        else:
            # Set private noise flag in config
            self.emulator_config.noise.enabled = True

            if self.emulator_config.mode == "statevector":
                raise ValueError(
                    "Noise model is not currently supported for mode='statevector'."
                )

            # Set MPO bond dim to noisy default, or check that the given value >=16
            if self.emulator_config.mode == "dmrg":
                if self.emulator_config.dmrg.mpo_bond_dim is None:
                    self.emulator_config.dmrg.mpo_bond_dim = MPO_BOND_DIM_WITH_NOISE

                elif self.emulator_config.dmrg.mpo_bond_dim < 16:
                    raise ValueError(
                        "MPO bond dim. should be at least 16 for noisy emulation."
                    )

            # If validation is turned on (default), validate the noise model
            if self.emulator_config.noise.validate_model:
                validate_noise_model_against_qubits(
                    noise_model=self.noise_model, qubits=self.emulator_config.qubits
                )
                validate_noise_model_against_serialized_circuit(
                    noise_model=self.noise_model,
                    serialized_circuit=self.serialized_circuit,
                )
        return self


def validate_noise_model_against_qubits(
    noise_model: NoiseModel, qubits: tuple[str, ...]
):
    """Check that all qubits exist in the noise model, and that there exists readout error for all qubits.

    Parameters
    ----------
    noise_model :
        The noise model to validate
    qubits :
        The qubits to validate against

    Raises
    ------
    ValueError :
        If a qubit is not contained in the noise model, or readout error is not defined for a qubit
    """

    noise_model_qubit_strings = noise_model.qubit_strings
    for q in qubits:
        if q not in noise_model_qubit_strings:
            raise ValueError(
                f"Qubit {q} is listed in the config, but is not contained in the noise model."
            )

    remaining_qubits = set(qubits)
    for q, _ in noise_model.readout_errors:
        if q in remaining_qubits:
            remaining_qubits.remove(q)
        if q == ANY:
            remaining_qubits.clear()

    if len(remaining_qubits) > 0:
        raise ValueError(
            f"Readout error for qubits {remaining_qubits} are not defined in the noise model, and there is no generic entry (with ANY)."
        )


def validate_noise_model_against_serialized_circuit(
    noise_model: NoiseModel, serialized_circuit: SerializedCircuit
):
    """Check that there exists a noise trigger for every gate in the circuit."""
    noise = noise_model.on_circuit(serialized_circuit)
    # If there was any missing noise, return an error
    if len(noise["missing_noise"]) > 0:
        raise ValueError(
            f"The following gates in the circuit do not trigger any noise channels: {noise['missing_noise']}"
        )


def long_range_gates(gatelist: list[dict], grouping: list[list[str]]) -> bool:
    """Checks if there are any long-range gates in a list.

    Given a gatelist (as a dict) and a qubit grouping, detect any long-range gates,
    where long-range means acting over any non-adjacent groups in the grouping.

    Parameters
    ----------
    gatelist :
        List of gates.
    grouping :
        Qubit grouping.

    Returns
    -------
    long_range_gates_exist
        True if there are long-range gates, False otherwise.
    """
    for gate in gatelist:
        gate_qubits = gate["qubits"]
        if len(gate_qubits) == 1:
            continue
        groups_involved = [
            i for i, g in enumerate(grouping) for q in gate_qubits if q in g
        ]
        long_range = any(
            (abs(i - j) > 1 for i in groups_involved for j in groups_involved)
        )
        if long_range:
            return True
    return False
