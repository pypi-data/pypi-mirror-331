from typing import Any, NamedTuple, Optional

# Output can be:
#   - an amplitude dict, from bitstrings to complex amplitudes
#   - a samples dict, from basis states to counts (int)
#   - an expectation values dict, from observable names to expectation values (complex)
#   - an MPS list, of which each element contains a list of qubit labels and an array

AmplitudeDict = dict[str | int, complex]
ProbabilityDict = dict[str, float]
SampleDict = dict[str, int]
ExpectationValuesDict = list[dict[str, str | complex | float]]
MpsList = list[list[list]]
QubitOrder = list[str]
MetaData = dict[str, Any]
OptimizerDict = dict[str, Any]
OutputData = (
    AmplitudeDict
    | ProbabilityDict
    | SampleDict
    | ExpectationValuesDict
    | MpsList
    | QubitOrder
    | OptimizerDict
    | int
)


class Result(NamedTuple):
    """A result class for storing emulation results.

    :param output:  emulation output.
    :param metadata: emulation metadata.
    :param circuit_number: (optional) number specifying the circuit emulated (in case of a batch job)
    :param run_number: (optional) number specyfing the run in case of multiple runs (with different
        bond dimensions) for a given circuit.
    """

    output: dict[str, OutputData]
    metadata: MetaData
    circuit_number: Optional[int] = None
    run_number: Optional[int] = None
