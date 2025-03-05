import logging
from typing import Optional

from qcshared.messaging.message import ProgressMessage

debug_logger = logging.getLogger("debug_logger")
emulator_logger = logging.getLogger("emulator_logger")


class ProgressReporter:
    """Use to report progress to client with optional min_step.

    Parameters
    ----------
    label
        Label to be printed next to the progress bar (client).
    color
        Color of the label.
    min_step
        Mininum step size (don't report updates if the progress change is
        smaller than this value).
    enabled
        Bool specifying whether to show output on next update.
    """

    def __init__(
        self,
        label: str,
        color: str = "red",
        min_step: Optional[float] = None,
        enabled: bool = True,
    ) -> None:
        self.label = label
        self.color = color
        self.min_step = min_step
        self._last_prog = 0.0
        self.enabled = enabled

    def __call__(self, progress: float, finished: bool = False) -> None:
        """Report progress to the client (progress bars).

        Parameters
        ----------
        progress
            Current progress (0.0-1.0) of the circuit builder.
        finished
            Indication of whether the circuit is done (will be passed to the
            `finished` field of the `ProgressMessage`.
        """
        if not finished and self.min_step is not None:
            if (progress - self._last_prog) < self.min_step:
                # Step too small - don't report update
                return
            else:
                # Store the current progress for the next call
                self._last_prog = progress

        if self.enabled:
            try:
                emulator_logger.info(
                    ProgressMessage(
                        progress,
                        label=self.label,
                        finished=finished,
                        color=self.color,
                    )
                )
            except Exception as e:
                debug_logger.info(f"Could not send progress: {e}")
