def recursive_dict_update(d: dict, u: dict) -> dict:
    """Recursively update a dictionary with another dictionary.

    Parameters
    ----------
    d
        Dictionary to update.

    u
        Dictionary to update with.

    Returns
    -------
    d
        The same dictionary d as in the input, but updated.
    """
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = recursive_dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def dicts_equal(d1: dict, d2: dict) -> bool:
    """Test if two dictionaries are equal.

    This assumes that the dictionaries only contain primitive types
    and other dictionaries (i.e. are serializable).

    Parameters
    ----------
    d1
        First dictionary.
    d2
        Second dictionary.

    Returns
    -------
    equal
        True if the dictionaries are equal, False otherwise.
    """
    equal = True
    for k in d1:
        if k in d2:
            if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                equal = equal and dicts_equal(d1[k], d2[k])
            elif d1[k] != d2[k]:
                equal = False
        else:
            return False
    return equal
