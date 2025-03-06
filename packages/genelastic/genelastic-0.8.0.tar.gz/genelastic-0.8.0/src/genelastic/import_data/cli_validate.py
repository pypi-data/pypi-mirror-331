import argparse
import logging
from pathlib import Path

from schema import SchemaError

from genelastic.common import add_verbose_control_args

from .import_bundle_factory import make_import_bundle_from_files
from .logger import configure_logging

logger = logging.getLogger("genelastic")


def read_args() -> argparse.Namespace:
    """Read arguments from command line."""
    parser = argparse.ArgumentParser(
        description="Ensure that YAML files "
        "follow the genelastic YAML bundle schema.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    add_verbose_control_args(parser)
    parser.add_argument(
        "files",
        type=Path,
        nargs="+",
        default=None,
        help="YAML files to validate.",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="In addition to validating the schema, "
        "check for undefined referenced processes.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point of the validate script."""
    args = read_args()
    configure_logging(args.verbose)

    try:
        make_import_bundle_from_files(args.files, check=args.check)
    except (ValueError, RuntimeError, TypeError, SchemaError) as e:
        # Catch any exception that can be raised by 'make_import_bundle_from_files'.
        logger.error(e)
        return 1

    logger.info("All YAML files respect the genelastic YAML bundle format.")
    return 0
