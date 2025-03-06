import logging
import re
import typing

from genelastic.common import BundleDict

from .constants import DEFAULT_TAG2FIELD, DEFAULT_TAG_PREFIX, DEFAULT_TAG_SUFFIX

logger = logging.getLogger("genelastic")

TagsDefinition: typing.TypeAlias = dict[str, dict[str, str | dict[str, str]]]


class Tags:
    """This class handles the definition of default and custom tags.
    Tags are used to extract custom metadata from files belonging to an analysis.
    """

    def __init__(self, documents: typing.Sequence[BundleDict] | None) -> None:
        """Create a Tag instance."""
        self._tags: dict[str, dict[str, str]] = DEFAULT_TAG2FIELD
        self._tag_prefix: str = DEFAULT_TAG_PREFIX
        self._tag_suffix: str = DEFAULT_TAG_SUFFIX

        redefined_tags = None

        if documents:
            # Search for tags definition across loaded YAML documents.
            redefined_tags = self._search_redefined_tags(documents)

        if redefined_tags:
            self._build_tags(redefined_tags)
            logger.info(
                "The following tags will be used to extract metadata from filenames : %s",
                self._tags,
            )
        else:
            logger.info(
                "Using the default tags to extract metadata from filenames : %s",
                self._tags,
            )

    def _build_tags(self, redefined_tags: TagsDefinition) -> None:
        # Erase the tags defined by defaults.
        self._tags = {}

        if "format" in redefined_tags:
            tag_format = redefined_tags["format"]

            # extra type check for mypy
            if "prefix" in tag_format and isinstance(tag_format["prefix"], str):
                self._tag_prefix = tag_format["prefix"]

            # extra type check for mypy
            if "suffix" in tag_format and isinstance(tag_format["suffix"], str):
                self._tag_suffix = tag_format["suffix"]

        for tag_name, tag_attrs in redefined_tags["match"].items():
            if isinstance(tag_attrs, dict):  # extra type check for mypy
                self._tags[
                    f"{self._tag_prefix}{tag_name}{self._tag_suffix}"
                ] = tag_attrs

    @staticmethod
    def _search_redefined_tags(
        documents: typing.Sequence[BundleDict],
    ) -> TagsDefinition | None:
        documents_with_redefined_tags: list[BundleDict] = [
            d for d in documents if "tags" in d
        ]
        bundle_paths = [d["bundle_file"] for d in documents_with_redefined_tags]

        # If there are more than one 'tags' redefinition across the documents, raise an error.
        if len(documents_with_redefined_tags) > 1:
            msg = (
                f"Only one 'tags' key should be defined across all documents, "
                f"but multiple were found : {', '.join(bundle_paths)}"
            )
            raise RuntimeError(msg)

        if len(documents_with_redefined_tags) == 1:
            redefined_tags: TagsDefinition = documents_with_redefined_tags[0][
                "tags"
            ]
            return redefined_tags

        return None

    @property
    def tag_prefix(self) -> str:
        """Return the tag prefix. Default prefix is '%'."""
        return self._tag_prefix

    @property
    def tag_suffix(self) -> str:
        """Return the tag suffix. There is no suffix by default."""
        return self._tag_suffix

    @property
    def items(self) -> typing.ItemsView[str, dict[str, str]]:
        """Returns the tag items : the key is the tag name,
        and the value is the tag attributes (a dict containing the 'field' and 'regex' keys).
        """
        return self._tags.items()

    @property
    def search_regex(self) -> str:
        """Returns a regex to search for a tag inside a string."""
        return (
            r"("
            + re.escape(self._tag_prefix)
            + r"\w+"
            + re.escape(self._tag_suffix)
            + r")"
        )

    def __len__(self) -> int:
        """Return the number of registered tags."""
        return len(self._tags)

    def __getitem__(self, key: str) -> dict[str, str]:
        """Return a tag by its key."""
        return self._tags[key]
