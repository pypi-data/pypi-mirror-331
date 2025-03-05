from pydantic import Field

from .config_utils import BaseConfig, BondDimType


class TEBDConfig(BaseConfig):
    max_D: BondDimType | list[BondDimType] = 2

    svd_cutoff: float = Field(
        default=1e-8,
        description="Threshold below which singular values are truncated",
        gt=0.0,
        lt=1.0,
    )
