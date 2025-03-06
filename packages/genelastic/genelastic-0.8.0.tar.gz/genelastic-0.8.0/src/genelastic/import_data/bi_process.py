import copy

from genelastic.common import BioInfoProcessData


class BioInfoProcess:
    """Class representing a bio process."""

    def __init__(
        self,
        proc_id: str,
        bundle_file: str | None = None,
        **data: str | list[str],
    ) -> None:
        self._proc_id = proc_id
        self._bundle_file = bundle_file
        self._data: BioInfoProcessData = data

    @property
    def id(self) -> str:
        """Get the bio process ID."""
        return self._proc_id

    @property
    def data(self) -> BioInfoProcessData:
        """Get data associated to the bio process."""
        return copy.deepcopy(self._data)
