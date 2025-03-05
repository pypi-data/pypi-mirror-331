import re
import warnings
from collections import Counter
from typing import Literal, Optional

import numpy as np
from pydantic import Field, field_validator

from .config_utils import BaseConfig, ConfigWarning
from .constants import MAX_BITSTRINGS, MAX_QUBITS_FOR_FULL_OUTPUT
from .dmrg_config import DMRGConfig
from .noise_config import NoiseConfig
from .optimizer_config import OptimizerConfig
from .output_config import OutputConfig
from .statevector_config import StateVectorConfig
from .tebd_config import TEBDConfig
from .trajectory_config import TrajectoryConfig


class EmulatorConfig(BaseConfig):
    """This is a class for the emulator config.

    It does not know about the circuit or noise model.
    """

    qubits: list[str] = Field(description="Qubit objects")
    grouping: Optional[list[list[str]]] = Field(
        default=None,
        description="Grouping of qubits as a list of lists. If None, groups will be generated"
        "automatically, with a group size given by group_size.",
        validate_default=True,
    )
    group_size: Optional[int] = Field(
        default=None, description="Size of groups", ge=1, le=20, validate_default=True
    )
    physical_dimensions: tuple[int, ...] = Field(default=(), validate_default=True)
    initial_state: int | list[int] = 0
    mode: Literal["dmrg", "tebd", "statevector"] = Field(
        default="dmrg",
        description="Emulation mode. Supported: 'dmrg', 'tebd', 'statevector'",
    )
    ignore_swaps: bool = False
    noise: NoiseConfig = NoiseConfig()
    tebd: TEBDConfig = TEBDConfig()
    dmrg: DMRGConfig = Field(default=DMRGConfig(), validate_default=True)
    statevector: StateVectorConfig = StateVectorConfig()
    output: OutputConfig = Field(default=OutputConfig(), validate_default=True)
    optimizer: OptimizerConfig = Field(default=OptimizerConfig(), validate_default=True)
    trajectory: TrajectoryConfig = TrajectoryConfig()

    # TODO doesn't support physical dimensions beyond 2 yet

    @field_validator("qubits")
    @classmethod
    def check_unique_qubits(cls, qubits):
        if len(qubits) != len(set(qubits)):
            raise ValueError("qubits must be unique")
        return qubits

    @field_validator("initial_state", mode="before")
    @classmethod
    def string_to_int_list(cls, initial_state):
        """If initial state is a string convert it to a list of integers.

        Also checks that the string only contains '0' and '1'.

        Parameters
        ----------
        initial_state
            Initial state of the qubits.

        Returns
        -------
        initial_state
            Initial state of the qubits as a list of integers.
        """

        if isinstance(initial_state, str):
            if not bool(re.match(r"^[01]+$", initial_state)):
                raise ValueError(
                    "initial_state is a string containing other characters than '0' and '1', this is currently not supported."
                )
            return [int(bit) for bit in initial_state]

        return initial_state

    @field_validator("physical_dimensions", mode="before")
    @classmethod
    def list_to_tuple(cls, physical_dimensions):
        """
        Converts physical_dimensions to a tuple if it is a list.

        Parameters
        ----------
        physical_dimensions
            Physical dimensions of the qubits.

        Returns
        -------
        physical_dimensions
            Physical dimensions of the qubits as a tuple.
        """

        if isinstance(physical_dimensions, list):
            return tuple(physical_dimensions)
        return physical_dimensions

    @field_validator("grouping")
    @classmethod
    def validate_grouping(cls, grouping, info):
        """Validates grouping of qubits.

        Validation criteria:
        - Checks if qubit grouping includes all qubits in 'qubits' section of config.
        - Checks if there are no duplicate qubits in the grouping.

        Parameters
        ----------
        grouping
            The qubit grouping to validate.
        values
            The values.

        Returns
        -------
        grouping
            Validated values.
        """

        if "qubits" not in info.data:
            # Avoid validation type error in 'qubits'
            return grouping

        if grouping is None:
            return grouping

        flat_grouping = [g for group in grouping for g in group]
        if any(g not in info.data.get("qubits") for group in grouping for g in group):
            raise ValueError("Qubit found in grouping that wasn't found in 'qubits'.")
        elif set(flat_grouping) != set(info.data.get("qubits")):
            raise ValueError("Qubit found in 'qubits' that wasn't found in grouping.")
        if len(set(flat_grouping)) != len(flat_grouping):
            duplicates = [
                item for item, count in Counter(flat_grouping).items() if count > 1
            ]
            raise ValueError(
                f"The following qubits appear more than once in the grouping: {duplicates}"
            )

        return grouping

    @field_validator("group_size")
    @classmethod
    def validate_group_size(cls, group_size, info):
        """Validates the group size.

        Validation criteria:
            - If `group_size` is None, it checks if 'grouping' is present in config.
            - If 'qubits' is not in the config, it returns the provided `group_size`.
            - If 'grouping' is provided in the config, it returns the maximum length of groups in 'grouping'.
              It also issues a warning if 'grouping' aand 'group_size' are both provided.
            - If `group_size` is greater than the number of qubits in 'qubits', it sets group_size to
              the number of qubits and issues a warning indicating that the requested `group_size` is
              more than the number of qubits.

        Parameters
        ----------
        group_size
            The group size parameter to validate.
        values : dict
            The values.

        Returns
        -------
        group_size
            The validated group size.
        """

        if group_size is None:
            if not info.data.get("grouping"):
                raise ValueError("One of group_size or grouping must be given.")
            return None

        if "qubits" not in info.data:
            # Avoid validation type error in 'qubits'
            return group_size

        if info.data.get("grouping"):
            err_location = ["emulator_config", "group_size"]
            err_msg = (
                "Only one of grouping or group_size should be set at any one time. "
                "group_size will be overriden by grouping."
            )
            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Set to default value",
                    err_msg,
                )
            )
            return max(len(group) for group in info.data["grouping"])

        # If the group size was too big, make it small enough and raise a warning
        if group_size > len(info.data["qubits"]):
            err_location = ["emulator_config", "group_size"]
            err_msg = "Group_size requested is more than the number of qubits."
            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Set to valid value.",
                    err_msg,
                )
            )
            return len(info.data["qubits"])

        return group_size

    # Always is True so that this validator is applied, even if no 'dmrg' dict and default DMRGConfig is generated
    @field_validator("dmrg")
    @classmethod
    def validate_dmrg(cls, dmrg, info):
        """
        Validates config for dmrg.

        Validation criteria:
            - If 'mode' is not present in values or its value is not 'dmrg', the config is returned unchanged.
            - If 'convergence_window_size' is None, it is inferred based on the values of 'grouping' and 'group_size'.
              If neither 'grouping' nor 'group_size' is provided, no inference is made.
              The inferred window size is set to twice the number of qubits divided by the group size or the number of
              groups in the grouping, whichever is available.

        Parameters
        ----------
        dmrg
            The DMRG config to validate.
        values
            The values.

        Returns
        -------
        dmrg
            The validated DMRG configuration.
        """

        if "mode" not in info.data or info.data["mode"] != "dmrg":
            return dmrg

        if dmrg.convergence_window_size is None:
            # If the grouping wasn't set, use the group_size to infer a window size
            if "grouping" not in info.data or info.data["grouping"] is None:
                # Quick exit if neither group_size or grouping is set (this will be caught earlier up)
                if info.data["group_size"] is None:
                    return dmrg
                window_size = 2 * len(info.data["qubits"]) // info.data["group_size"]
            else:
                window_size = 2 * len(info.data["grouping"])

            dmrg.convergence_window_size = window_size

            err_location = ["emulator_config", "dmrg", "convergence_window_size"]
            err_msg = (
                "convergence_window_size is None': set window_size to the number of qubit groups"
                f"\nResulting window size: {dmrg.convergence_window_size}."
            )

            warnings.warn(
                ConfigWarning(
                    err_location,
                    "Set to default value",
                    err_msg,
                )
            )
        return dmrg

    # TODO doesn't support physical dimensions beyond 2 yet
    @field_validator("physical_dimensions")
    @classmethod
    def validate_physical_dimensions(cls, physical_dims, info):
        """Validates the physical dimensions.

        Checks that the physical dimensions are empty or filled with dimension 2.

        Parameters
        ----------
        physical_dims
            The physical dimensions to validate.
        values
            The values.

        Returns
        -------
        unknown
            If 'qubits' is present in the config, returns a tuple filled with dimension 2
            with the same length as the number of qubits. If 'qubits' is not present or
            physical_dims is not empty and contains dimensions other than 2, returns an empty tuple.
        """

        if physical_dims and not all(dim == 2 for dim in physical_dims):
            raise ValueError("Custom physical dimensions are currently not supported")

        if "qubits" not in info.data:
            return ()

        return tuple(2 for _ in range(len(info.data["qubits"])))

    @field_validator("initial_state")
    @classmethod
    def validate_initial_state(cls, initial_state, info):
        """Validates the initial state.

        Validation criteria:
        - Checks if the initial state is achievable (positive).
        - Verifies if the initial state matches the specified physical dimensions.

        Parameters
        ----------
        initial_state
            The initial state to validate.
        values
            The values.

        Returns
        -------
        initial_state
            The validated initial state.
        """

        if (
            "physical_dimensions" not in info.data
            or not info.data["physical_dimensions"]
        ):
            return None

        physical_dims = info.data["physical_dimensions"]
        n_qubits = len(physical_dims)

        if isinstance(initial_state, int):
            # calculate maximal_state with pure python instead of np.prod to avoid overflow errors
            prod = 1
            for i in physical_dims:
                prod *= i
            maximal_state = prod - 1

            if initial_state < 0:
                raise ValueError(
                    f"Invalid initial state: {initial_state} (negative value)."
                )
            elif initial_state > 0 and initial_state > maximal_state:
                raise ValueError(
                    f"Invalid initial state: {initial_state} "
                    f"(not possible with {n_qubits} qubits) of dimensions {physical_dims})"
                )
        elif isinstance(initial_state, list):
            if len(initial_state) != n_qubits:
                raise ValueError(
                    f"Invalid initial state: {initial_state} "
                    f"(not possible with {n_qubits} qubits)."
                )
            elif any(
                s < 0 or s >= physical_dims[i] for i, s in enumerate(initial_state)
            ):
                raise ValueError(
                    f"Invalid physical value found in initial state: {initial_state} (for physical dimensions {physical_dims})"
                )
        else:
            return None

        return initial_state

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, mode, info):
        """Validates the emulation mode.

        Validation criteria:
        - Checks if the provided mode is supported.
        - Ensures that for mode 'dmrg', emulation is performed on more than 1 group.
        - Requires a grouping to be given for mode 'tebd'.

        Parameters
        ----------
        mode
            The emulation mode to validate.
        values
            The values.

        Returns
        -------
        mode
            The validated emulation mode.
        """

        if "qubits" not in info.data:
            return mode

        if mode == "dmrg":
            if (
                "grouping" in info.data
                and info.data["grouping"] is not None
                and len(info.data["grouping"]) == 1
            ):
                raise ValueError(
                    "DMRG is not supported for a single group (MPS of length 1), use mode 'tebd' instead"
                )
            if (
                ("grouping" not in info.data or info.data["grouping"] is None)
                and "group_size" in info.data
                and info.data["group_size"] >= len(info.data["qubits"])
            ):
                raise ValueError(
                    "DMRG is not supported for a single group (MPS of length 1), but the maximum group size is larger or equal to the number of qubits"
                )

        if mode == "tebd" and "grouping" in info.data and info.data["grouping"] is None:
            raise ValueError(
                "Automatic grouping is not supported for emulation mode 'tebd'. Please set a grouping."
            )

        return mode

    @field_validator("output")
    @classmethod
    def validate_output(cls, v, info):
        """Validates the output amplitudes against 'qubits'.

        Validation criteria:
        - Checks if the number of qubits in each amplitude bitstring match the number
              defined in 'qubits'.
        - Checks if the number of bitstrings does not exceed the maximum allowed limit.
        - Checks if observables, if provided, act only on qubits existing in 'qubits'.
        - Ensures that the full MPS is only returned if the bond dimensions <= 100 and the number
            of qubits <= 10.

        Parameters
        ----------
        v
            The output configuration to validate.
        values
            The values.
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        v
            The validated output configuration.
        """

        # If amplitude output or observables output or mps output are not enabled, we don't do any checking
        if not (v.amplitudes.enabled or v.expectation_values.enabled or v.mps.enabled):
            return v

        # (try to) get 'qubits' and the number of qubits
        try:
            qubits = info.data["qubits"]
            n_qubits = len(set(qubits))
        except KeyError:
            return v

        # Validate amplitudes
        if v.amplitudes.enabled:
            bitstrings = v.amplitudes.bitstrings
            if isinstance(bitstrings, list):
                if all(isinstance(bs, str) for bs in bitstrings) and not all(
                    len(bs) == len(qubits) for bs in bitstrings
                ):
                    raise ValueError(
                        "The bitstrings for which amplitudes are to be computed do not "
                        f"match the number of qubits in 'qubits', given by: ({qubits})."
                    )
                elif all(isinstance(bs, int) for bs in bitstrings) and any(
                    bs > 0 and np.log2(bs) > len(qubits) for bs in bitstrings
                ):
                    raise ValueError(
                        "The basis state values for which amplitudes are to be computed are "
                        f"not compatible with the number of qubits in 'qubits', given by: ({qubits})."
                    )
            elif (
                isinstance(bitstrings, str)
                and bitstrings == "all"
                and n_qubits > MAX_QUBITS_FOR_FULL_OUTPUT
            ):
                raise ValueError(
                    f"Setting bitstrings to 'all' will generate {2**n_qubits} amplitudes, "
                    f"which is beyond the supported limit of {MAX_BITSTRINGS}. "
                    "The use of setting 'all' is only supported for up to "
                    f"{MAX_QUBITS_FOR_FULL_OUTPUT} qubits."
                )

        if v.expectation_values.enabled:
            # Check that each observable acts only on qubits in the qubit order
            for obs in v.expectation_values.observables:
                for term in obs.terms:
                    if not all(q in qubits for q in term.paulis.keys()):
                        missing_qubits = [
                            q for q in term.paulis.keys() if q not in qubits
                        ]
                        raise ValueError(
                            f"Observable {obs.name} acts on qubits ({missing_qubits}) not found in qubit order."
                        )

        if v.mps.enabled:
            if "mode" not in info.data:
                return v

            mode = info.data["mode"]

            if mode == "dmrg" or mode == "tebd":
                if mode == "dmrg":
                    bond_dims = info.data["dmrg"].D
                else:
                    bond_dims = info.data["tebd"].max_D

                if isinstance(bond_dims, int):
                    bond_dims = [bond_dims]

                if not (all(b <= 100 for b in bond_dims) and n_qubits <= 10):
                    raise ValueError(
                        "The full MPS can only be returned as output if bond dimension is less or equal than 100 and the number of qubits is less or equal than 10"
                    )

        return v

    @field_validator("optimizer")
    @classmethod
    def validate_optimizer(cls, optimizer, info):
        """Validates optimizer.

        Check:
            - If optimizer is enabled, an observable must be specified
            - initial_param_noise must be non-negative
            - initial_param_noise is zero, and no initial parameter values are given
        """
        if not optimizer.enabled:
            return optimizer

        qubits_in_observable = {
            key
            for single_term in optimizer.observable.terms
            for key in single_term.paulis.keys()
        }

        qubits_in_emulation = set(info.data["qubits"])

        if not qubits_in_observable <= qubits_in_emulation:
            raise ValueError(
                f"Observable acts on qubits not found in 'qubits': {qubits_in_observable - qubits_in_emulation}"
            )

        return optimizer
