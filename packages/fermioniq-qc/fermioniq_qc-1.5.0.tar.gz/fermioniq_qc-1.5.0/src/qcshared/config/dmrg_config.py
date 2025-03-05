from typing import Optional

from pydantic import Field, field_validator

from .config_utils import BaseConfig, BondDimType
from .constants import MAX_CUT_DIM, MAX_SWEEPS


class DMRGConfig(BaseConfig):
    D: BondDimType | list[BondDimType] = 2
    init_mode: str = "ket"
    convergence_window_size: Optional[int] = Field(
        default=None,
        description="Number of fidelities to inspect for convergence",
        ge=2,
        le=1000,
    )
    convergence_threshold: float = Field(
        default=1e-5, description="Threshold for convergence", ge=0.0, le=1.0
    )
    target_fidelity: float = Field(
        default=1.0, description="Target fidelity to reach", ge=0.0, le=1.0
    )
    max_sweeps: int = Field(
        default=int(1e4), description="Maximum number of sweeps", ge=1, le=MAX_SWEEPS
    )
    max_subcircuit_rows: int = Field(default=1, ge=1, le=10)
    mpo_bond_dim: Optional[int] = Field(
        default=None, ge=4, le=1024, validate_default=True
    )
    regular_grid: bool = True
    truncate_rows: bool = True

    @field_validator("init_mode")
    @classmethod
    def validate_init_mode(cls, init_mode):
        if init_mode not in ["ket", "random", "tebd", "lowerD"]:
            raise ValueError(
                f"Unsupported / unrecognized initialization mode for dmrg ({init_mode})."
            )
        return init_mode

    @field_validator("mpo_bond_dim")
    @classmethod
    def validate_mpo_bond_dim(cls, mpo_bond_dim, info):
        if "max_subcircuit_rows" not in info.data or mpo_bond_dim is None:
            return mpo_bond_dim

        # Check that this combination of mpo_bond_dim and max_subcircuit_rows doesn't go beyond
        #  the max_cut_dim that we allow
        max_cut = mpo_bond_dim ** info.data["max_subcircuit_rows"]

        if max_cut > MAX_CUT_DIM:
            raise ValueError(
                f"Product of mpo_bond_dim {mpo_bond_dim} and max_subcircuit_rows {info.data['max_subcircuit_rows']} exceeds the maximum of {MAX_CUT_DIM}."
            )
        return mpo_bond_dim
