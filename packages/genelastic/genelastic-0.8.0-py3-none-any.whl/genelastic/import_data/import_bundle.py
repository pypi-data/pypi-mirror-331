"""Module: import_bundle

This module provides functionality for importing data bundles.
"""

import logging
import sys
import typing

from genelastic.common import BundleDict

from .analyses import Analyses
from .bi_processes import BioInfoProcesses
from .constants import BUNDLE_CURRENT_VERSION
from .data_file import DataFile
from .tags import Tags
from .wet_processes import WetProcesses

logger = logging.getLogger("genelastic")


class ImportBundle:
    """Class for handling an import bundle description."""

    def __init__(  # noqa: C901
        self, x: typing.Sequence[BundleDict], *, check: bool = False
    ) -> None:
        analyses: list[BundleDict] = []
        wet_processes: list[BundleDict] = []
        bi_processes: list[BundleDict] = []
        tags = Tags(x)

        # Loop on dicts
        for d in x:
            # Check version
            if "version" not in d:
                msg = "No version inside YAML document."
                raise RuntimeError(msg)
            if int(d["version"]) != BUNDLE_CURRENT_VERSION:
                raise RuntimeError

            # Gather all analyses
            if "analyses" in d and d["analyses"] is not None:
                # Copy some bundle properties into each analysis
                for analysis in d["analyses"]:
                    for key in ["bundle_file", "root_dir"]:
                        if key in d:
                            analysis[key] = d[key]

                    # Add the tags to use.
                    analysis["tags"] = tags

                analyses.extend(d["analyses"])

            # If some wet processes are defined, copy the bundle file path into each of them.
            if "wet_processes" in d and d["wet_processes"] is not None:
                for wet_process in d["wet_processes"]:
                    wet_process["bundle_file"] = d["bundle_file"]
                wet_processes.extend(d["wet_processes"])

            # If some bio processes are defined, copy the bundle file path into each of them.
            if "bi_processes" in d and d["bi_processes"] is not None:
                for bi_process in d["bi_processes"]:
                    bi_process["bundle_file"] = d["bundle_file"]
                bi_processes.extend(d["bi_processes"])

        # Instantiate all objects
        self._wet_processes: WetProcesses = WetProcesses.from_array_of_dicts(
            wet_processes
        )
        self._bi_processes: BioInfoProcesses = (
            BioInfoProcesses.from_array_of_dicts(bi_processes)
        )
        self._analyses: Analyses = Analyses.from_array_of_dicts(analyses)

        if check:
            self.check_referenced_processes()

    def check_referenced_processes(self) -> None:
        """Check if wet and bi processes referenced inside each analysis are defined.
        If one of the processes is not defined, the program exits.
        """
        for index, analysis in enumerate(self._analyses):
            analysis_wet_process = analysis.metadata.get("wet_process")

            if (
                analysis_wet_process
                and analysis_wet_process
                not in self._wet_processes.get_process_ids()
            ):
                sys.exit(
                    f"Analysis at index {index} in file {analysis.bundle_file} "
                    f"is referencing an undefined wet process: {analysis_wet_process}"
                )

            analysis_bi_process = analysis.metadata.get("bi_process")

            if (
                analysis_bi_process
                and analysis_bi_process
                not in self._bi_processes.get_process_ids()
            ):
                sys.exit(
                    f"Analysis at index {index} in file {analysis.bundle_file} "
                    f"is referencing an undefined bi process: {analysis_bi_process}"
                )

    @property
    def analyses(self) -> Analyses:
        """The analyses."""
        return self._analyses

    @property
    def wet_processes(self) -> WetProcesses:
        """The wet processes."""
        return self._wet_processes

    @property
    def bi_processes(self) -> BioInfoProcesses:
        """The bi processes."""
        return self._bi_processes

    def get_nb_files(self, cat: str | None = None) -> int:
        """Get the number of files in a category."""
        files = self.get_files(cat)
        return len(files)

    def get_files(self, cat: str | None = None) -> list[DataFile]:
        """Returns all files of a category."""
        files: list[DataFile] = []

        # Loop on all analyses
        for analysis in self.analyses:
            files += analysis.get_data_files(cat)

        return files

    def get_nb_matched_files(self) -> int:
        """Get the number of files that match the pattern."""
        return sum(a.get_nb_files() for a in self.analyses)

    def get_nb_unmatched_files(self) -> int:
        """Get the number of files that do not match."""
        return sum(len(a.get_unmatched_file_paths()) for a in self.analyses)
