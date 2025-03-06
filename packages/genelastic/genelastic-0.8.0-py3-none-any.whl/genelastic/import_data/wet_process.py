import copy

from genelastic.common import WetProcessesData


class WetProcess:
    """Class WetProcess that represents a wet process."""

    def __init__(
        self,
        proc_id: str,
        bundle_file: str | None = None,
        **data: str | float,
    ) -> None:
        """Create a WetProcess instance."""
        self._proc_id = proc_id
        self._bundle_file = bundle_file
        self._data: WetProcessesData = data

    @property
    def id(self) -> str:
        """Get the wet process ID."""
        return self._proc_id

    @property
    def data(self) -> WetProcessesData:
        """Get data associated to the wet process."""
        return copy.deepcopy(self._data)
