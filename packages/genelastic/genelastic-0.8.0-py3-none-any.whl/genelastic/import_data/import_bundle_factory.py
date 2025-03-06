"""ImportBundle factory module."""

import logging
import re
import sys
from pathlib import Path

import schema
import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from genelastic.common import BundleDict

from .constants import BUNDLE_CURRENT_VERSION
from .import_bundle import ImportBundle

logger = logging.getLogger("genelastic")


def validate_tag_char(s: str) -> bool:
    """A tag should only contain one special character, excluding the following : (, ), ?, <, >."""
    if len(s) > 1:
        return False

    return re.match(r"^[^\w()<>?]$", s) is not None


def validate_field_chars(s: str) -> bool:
    """Fields should only contain word characters.
    A word character is a character a-z, A-Z, 0-9, including _ (underscore).
    """
    return re.match(r"^\w+$", s) is not None


_SCHEMA_V1 = schema.Schema(
    {"version": 1, schema.Optional("vcf_files"): schema.Or(None, [str])}
)

_SCHEMA_V2 = schema.Schema(
    {
        "version": 2,
        schema.Optional("vcf"): {
            schema.Optional("filename_pattern"): str,
            "files": [str],
        },
    }
)

_SCHEMA_V3 = schema.Schema(
    {
        "version": 3,
        schema.Optional("analyses"): schema.Or(
            None,
            [
                {
                    schema.Optional("file_prefix"): str,
                    schema.Optional("files"): [str],
                    schema.Optional("sample_name"): str,
                    schema.Optional("source"): str,
                    schema.Optional("barcode"): str,
                    schema.Optional("wet_process"): str,
                    schema.Optional("bi_process"): str,
                    schema.Optional("reference_genome"): str,
                    schema.Optional("flowcell"): str,
                    schema.Optional("lanes"): [int],
                    schema.Optional("seq_indices"): [str],
                    schema.Optional("cov_depth"): int,
                    schema.Optional("qc_comment"): str,
                    schema.Optional("data_path"): str,
                }
            ],
        ),
        schema.Optional("wet_processes"): schema.Or(
            None,
            [
                {
                    "proc_id": str,
                    "manufacturer": str,
                    "sequencer": str,
                    "generic_kit": str,
                    "fragmentation": int,
                    "reads_size": int,
                    "input_type": str,
                    "amplification": str,
                    "flowcell_type": str,
                    "sequencing_type": str,
                    schema.Optional("desc"): str,
                    schema.Optional("library_kit"): str,
                    schema.Optional("sequencing_kit"): str,
                    schema.Optional("error_rate_expected"): float,
                }
            ],
        ),
        schema.Optional("bi_processes"): schema.Or(
            None,
            [
                {
                    "proc_id": str,
                    "name": str,
                    "pipeline_version": str,
                    schema.Optional("steps"): [
                        {
                            "name": str,
                            "cmd": str,
                            schema.Optional("version"): str,
                            schema.Optional("output"): str,
                        }
                    ],
                    "sequencing_type": str,
                    schema.Optional("desc"): str,
                }
            ],
        ),
        schema.Optional("tags"): {
            schema.Optional("format"): {
                schema.Optional("prefix"): schema.And(
                    str,
                    validate_tag_char,
                    error="Key 'prefix' should only contain one special character, "
                    "excluding the following : (, ), ?, <, >.",
                ),
                schema.Optional("suffix"): schema.And(
                    str,
                    validate_tag_char,
                    error="Key 'suffix' should only contain one special character, "
                    "excluding the following : (, ), ?, <, >.",
                ),
            },
            "match": {
                schema.And(
                    str,
                    validate_field_chars,
                    error="Tags listed under the 'match' key should only contain "
                    "word characters. A word character is a character "
                    "a-z, A-Z, 0-9, including _ (underscore).",
                ): {"field": str, "regex": str}
            },
        },
    }
)


def make_import_bundle_from_files(
    files: list[Path], *, check: bool = False
) -> ImportBundle:
    """Create an ImportBundle instance from a list of YAML files."""
    all_documents = []
    for file in files:
        # Load documents stored in each file.
        new_documents = load_import_bundle_file(file)

        for i, new_document in enumerate(new_documents):
            # Upgrade each new document to the latest/current version.
            if new_document["version"] != BUNDLE_CURRENT_VERSION:
                new_documents[i] = upgrade_bundle_version(
                    new_document, BUNDLE_CURRENT_VERSION
                )
            # Set the root directory path in each new document.
            new_documents[i]["root_dir"] = str(file.parent)
            # Set the original bundle YAML file path in each new document.
            new_documents[i]["bundle_file"] = str(file)

        all_documents.extend(new_documents)

    # Create bundle instance.
    return ImportBundle(all_documents, check=check)


def set_version(x: BundleDict) -> None:
    """Set version number.

    Deduce the version number from the keys present inside the dictionary.
    """
    # Empty doc
    if len(x) == 0:
        x["version"] = BUNDLE_CURRENT_VERSION

    # Wrong content in version field
    elif "version" in x:
        if not isinstance(x["version"], int):
            msg = "Version must be an integer."
            raise ValueError(msg)

    # Version 1
    elif "vcf_files" in x or "cov_files" in x:
        x["version"] = 1

    # Version 2
    elif "vcf" in x and "filename_pattern" in x["vcf"]:
        x["version"] = 2

    # Latest version
    else:
        x["version"] = BUNDLE_CURRENT_VERSION


def validate_doc(x: BundleDict) -> None:
    """Validate the dictionary using its corresponding schema."""
    # Get schema
    bundle_schema = globals().get("_SCHEMA_V" + str(x["version"]))
    if bundle_schema is None:
        raise ValueError(
            f"Unknown version \"{x['version']}\" for import " + "bundle file."
        )

    # Validate
    bundle_schema.validate(x)


def load_import_bundle_file(file: Path) -> list[BundleDict]:
    """Loads a YAML import bundle file."""
    # Load YAML
    logger.info('Load YAML data import file "%s".', file)
    docs: list[BundleDict] = []

    try:
        with file.open(encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))
    except (IsADirectoryError, FileNotFoundError) as e:
        logger.error(e)
        sys.exit(1)
    except ScannerError as e:
        logger.error("YAML file lexical analysis failed : %s", e)
        sys.exit(1)
    except ParserError as e:
        logger.error("YAML file syntactic analysis failed : %s", e)
        sys.exit(1)

    # Guess/set version
    if docs is None:
        docs = [{"version": BUNDLE_CURRENT_VERSION}]
    else:
        for i, x in enumerate(docs):
            if x is None:
                docs[i] = {"version": BUNDLE_CURRENT_VERSION}
            else:
                set_version(x)

    # Find schema and validate document
    for x in docs:
        validate_doc(x)

    return docs


def upgrade_bundle_version(x: BundleDict, to_version: int) -> BundleDict:
    """Upgrade a loaded import bundle dictionary.

    :raises ValueError: Raised if the input bundle lacks a version key or if the target version is invalid.
    :raises TypeError: Raised if the version value in the input bundle is not an integer.
    """
    # Check version
    if "version" not in x:
        msg = "No version in input bundle dictionary."
        raise ValueError(msg)
    if not isinstance(x["version"], int):
        msg = "Version of input bundle is not an integer."
        raise TypeError(msg)
    if x["version"] >= to_version:
        msg = f"Original version ({x['version']}) is greater or equal to target version ({to_version})."
        raise ValueError(msg)

    # Loop on upgrades to run
    y = x.copy()
    for v in range(x["version"], to_version):
        upgrade_fct = globals().get(f"_upgrade_from_v{v}_to_v{v + 1}")
        y = upgrade_fct(y)  # type: ignore[misc]

    return y


def _upgrade_from_v1_to_v2(x: BundleDict) -> BundleDict:
    # Upgrade
    y = {"version": 2, "vcf": {"files": []}}
    if "vcf_files" in x and x["vcf_files"] is not None:
        y["vcf"]["files"] = x["vcf_files"]  # type: ignore[index]

    # Validate schema
    _SCHEMA_V2.validate(y)

    return y


def _upgrade_from_v2_to_v3(x: BundleDict) -> BundleDict:
    # Upgrade
    y: BundleDict = {"version": 3, "analyses": []}
    if "vcf" in x:
        analysis_entry = {}
        if "files" in x["vcf"]:
            analysis_entry["files"] = x["vcf"]["files"]
        if "filename_pattern" in x["vcf"]:
            analysis_entry["file_prefix"] = x["vcf"]["filename_pattern"]
        y["analyses"].append(analysis_entry)

    _SCHEMA_V3.validate(y)

    return y
