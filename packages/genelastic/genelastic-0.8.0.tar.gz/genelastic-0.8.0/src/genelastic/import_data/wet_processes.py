import logging
import typing

from genelastic.common import BundleDict

from .wet_process import WetProcess

logger = logging.getLogger("genelastic")


class WetProcesses:
    """Class WetProcesses is a container of WetProces objects."""

    def __init__(self) -> None:
        """Create an empty container."""
        self._dict: dict[str, WetProcess] = {}

    def __len__(self) -> int:
        """Return the number of WetProcess objects inside the container."""
        return len(self._dict)

    def __getitem__(self, key: str) -> WetProcess:
        """Return a WetProcess present in the container by its key."""
        return self._dict[key]

    def add(self, process: WetProcess) -> None:
        """Add one WetProces object.
        If a WetProces object with the same ID already exists in the container, the program exits.
        """
        if process.id in self._dict:
            msg = (
                f"A wet process with the id '{process.id}' is already present."
            )
            raise ValueError(msg)

        # Add one WetProcess object.
        self._dict[process.id] = process

    def get_process_ids(self) -> set[str]:
        """Get a list of the wet processes IDs."""
        return set(self._dict.keys())

    @classmethod
    def from_array_of_dicts(
        cls, arr: typing.Sequence[BundleDict]
    ) -> typing.Self:
        """Build a WetProcesses instance."""
        wet_processes = cls()

        for d in arr:
            wet_processes.add(WetProcess(**d))

        return wet_processes
