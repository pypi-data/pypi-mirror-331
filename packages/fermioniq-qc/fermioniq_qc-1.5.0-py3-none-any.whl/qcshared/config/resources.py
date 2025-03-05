def _num_elements_without_bond_dim_dmrg(
    group_dim: int, mpo_bond_dim: int, mps_length: int, noise: bool
) -> int:
    """Compute the peak number of memory elements required for the DMRG emulator, without taking into account bond dimension.

    Parameters
    ----------
    group_dim:

    mpo_bond_dim:

    mps_length:

    noise:

    Returns
    -------
    peak_num_elements_dmrg:
        Number of memory elements required
    """
    contraction = (
        2 * group_dim * mpo_bond_dim**2 if noise else 2 * group_dim * mpo_bond_dim
    )
    boundaries = 2 * (mps_length - 1) * mpo_bond_dim
    mps = 2 * mps_length * group_dim
    return contraction + boundaries + mps


def peak_num_elements_dmrg(
    group_size: int, mpo_bond_dim: int, mps_length: int, noise: bool, bond_dim: int
) -> int:
    """Compute the peak memory usage (in terms of the number of tensor elements) for DMRG.

    Parameters
    ----------
    group_size :
        Size of the groups (or an upper bound thereof).
    mpo_bond_dim :
        Bond dimension of the gate MPOs (if there are multiple rows, this should be raised
        to the power of the number of rows).
    mps_length :
        Length of the MPS.
    noise :
        Whether noise is enabled or not.
    bond_dim :
        Bond dimension of the MPS.

    Returns
    -------
    peak_num_elements_dmrg :
        Maximum number of memory elements required
    """
    phys_dim = 4 if noise else 2
    group_dim = phys_dim**group_size

    num_elems_without_bond_dim = _num_elements_without_bond_dim_dmrg(
        group_dim, mpo_bond_dim, mps_length, noise
    )

    return bond_dim**2 * num_elems_without_bond_dim


def peak_num_elements_tebd(
    group_size: int, mps_length: int, noise: bool, bond_dim: int
):
    """Compute the peak memory usage (in terms of the number of tensor elements) for TEBD.

    Parameters
    ----------
    group_size :
        Size of the groups (or an upper bound thereof).
    mps_length :
        Length of the MPS.
    noise :
        Whether noise is enabled or not.
    bond_dim :
        Bond dimension of the MPS.

    Returns
    -------
    peak_num_elements_tebd :
        Maximum number of memory elements required
    """
    phys_dim = 4 if noise else 2

    if mps_length == 1:
        # Store the statevector two times plus a gate for contraction
        return 2 * phys_dim**group_size + phys_dim**4

    mps = (mps_length * phys_dim**group_size) * bond_dim**2

    if group_size == 1:
        # For singleton groups the biggest contraction is merging the gate into the joined site tensors
        contraction = 2 * (bond_dim**2 * phys_dim**2) + phys_dim**4
        # Approximate space complexity of svd as three times matrix size. SVD to split two site tensors
        svd = 3 * (bond_dim**2 * phys_dim**2)

    else:
        # Otherwise, the biggest contraction is a single leg back into its group:
        # Contracting a term of phys X bond X (bond * phys) with a term of bond X phys**(group size - 1) X (phys * bond)
        contraction = (phys_dim**2 + 2 * phys_dim**group_size) * bond_dim**2

        # SVD to split off a leg
        svd = 3 * phys_dim**group_size * bond_dim**2

    return mps + max(contraction, svd)
