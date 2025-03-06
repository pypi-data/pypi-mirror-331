"""This module defines the DataFile class, which handles the representation,
management, and extraction of metadata for a data file within a data bundle.

It includes functionality to construct DataFile instances from paths and
optional filename patterns, retrieve file paths and metadata, and support
for extracting metadata from filenames using specified patterns.
"""

import logging
import pathlib
from pathlib import Path

from genelastic.common import AnalysisMetaData

from .filename_pattern import FilenamePattern

logger = logging.getLogger("genelastic")


class DataFile:
    """Class for handling a data file and its metadata."""

    # Initializer
    def __init__(
        self,
        path: Path,
        bundle_path: Path | None = None,
        metadata: AnalysisMetaData | None = None,
    ) -> None:
        self._path = path
        self._bundle_path = bundle_path  # The bundle YAML file in which this
        # file was listed.
        self._metadata = {} if metadata is None else metadata

    def __repr__(self) -> str:
        return f"File {self._path}, from bundle {self._bundle_path}, with metadata {self._metadata}"

    # Get path
    @property
    def path(self) -> Path:
        """Retrieve the data file path."""
        return self._path

    def exists(self) -> bool:
        """Tests if the associated file exists on disk."""
        return self._path.is_file()

    # Get bundle path
    @property
    def bundle_path(self) -> Path | None:
        """Retrieve the path to the associated data bundle file."""
        return self._bundle_path

    # Get metadata
    @property
    def metadata(self) -> AnalysisMetaData:
        """Retrieve a copy of the metadata associated with the data file."""
        return self._metadata.copy()

    # Factory
    @classmethod
    def make_from_bundle(
        cls,
        path: Path,
        bundle_path: Path | None,
        pattern: FilenamePattern | None = None,
    ) -> "DataFile":
        """Construct a DataFile instance from a bundle path, file path,
        and optional filename pattern.
        """
        # Make absolute path
        if not path.is_absolute() and bundle_path is not None:
            path = bundle_path.parent / path

        # Extract filename metadata
        metadata = None
        if pattern is not None:
            metadata = pattern.extract_metadata(path.name)

        if metadata:
            if "ext" not in metadata:
                metadata["ext"] = pathlib.Path(path).suffixes[0][1:]

            if "cov_depth" in metadata:
                metadata["cov_depth"] = int(metadata["cov_depth"])

        return cls(path, bundle_path, metadata)
