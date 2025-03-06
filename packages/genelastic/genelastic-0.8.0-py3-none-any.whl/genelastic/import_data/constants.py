"""Module: constants

This module contains genelastic constants.
"""

import typing

ALLOWED_CATEGORIES: typing.Final[list[str]] = ["vcf", "cov"]

BUNDLE_CURRENT_VERSION = 3

DEFAULT_TAG_REGEX = "[^_-]+"
DEFAULT_TAG_PREFIX = "%"
DEFAULT_TAG_SUFFIX = ""

DEFAULT_TAG2FIELD: typing.Final[dict[str, dict[str, str]]] = {
    "%S": {"field": "sample_name", "regex": DEFAULT_TAG_REGEX},
    "%F": {"field": "source", "regex": DEFAULT_TAG_REGEX},
    "%W": {"field": "wet_process", "regex": DEFAULT_TAG_REGEX},
    "%B": {"field": "bi_process", "regex": DEFAULT_TAG_REGEX},
    "%D": {"field": "cov_depth", "regex": DEFAULT_TAG_REGEX},
    "%A": {"field": "barcode", "regex": DEFAULT_TAG_REGEX},
    "%R": {"field": "reference_genome", "regex": DEFAULT_TAG_REGEX},
}
