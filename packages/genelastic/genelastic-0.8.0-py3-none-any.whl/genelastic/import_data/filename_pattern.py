"""This module defines the FilenamePattern class, used to define a filename pattern
and extract metadata from file names using this pattern.
"""

import re

from genelastic.common import AnalysisMetaData


class FilenamePattern:
    """Class for defining a filename pattern.
    The pattern is used to extract metadata from filenames
    and verify filename conformity.
    """

    # Initializer
    def __init__(self, pattern: str) -> None:
        """Initializes a FilenamePattern instance.

        Args:
            pattern (str): The pattern string used for defining
             the filename pattern.
        """
        self._re = re.compile(pattern)

    def extract_metadata(self, filename: str) -> AnalysisMetaData:
        """Extracts metadata from the given filename based
        on the defined pattern.

        Args:
            filename (str): The filename from which metadata
            needs to be extracted.

        Returns:
            dict: A dictionary containing the extracted metadata.

        Raises:
            RuntimeError: If parsing of filename fails
            with the defined pattern.
        """
        m = self._re.search(filename)
        if not m:
            msg = f'Failed parsing filename "{filename}" with pattern "{self._re.pattern}".'
            raise RuntimeError(msg)
        return m.groupdict()

    def matches_pattern(self, filename: str) -> bool:
        """Checks if the given filename matches the defined pattern.

        Args:
            filename (str): The filename to be checked.

        Returns:
            bool: True if the filename matches the pattern,
            False otherwise.
        """
        return bool(self._re.match(filename))
