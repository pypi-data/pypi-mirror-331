from typing import Literal

from .config_utils import BaseConfig


class TrajectoryConfig(BaseConfig):
    n_shots: int = 1
    target_probability_tol: float = 1e-3
    search_method: Literal["dfs", "random"] = "dfs"
