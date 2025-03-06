# vi: se tw=80

# Elasticsearch Python API:
# https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/overview.html
# https://elasticsearch-py.readthedocs.io/en/latest/api.html

import argparse
import csv
import datetime
import hashlib
import logging
import sys
import time
from pathlib import Path

import vcf

from genelastic.common import (
    AnalysisDocument,
    BulkItems,
    ElasticImportConn,
    MetadataDocument,
    ProcessDocument,
    add_es_connection_args,
    add_verbose_control_args,
)

from .bi_processes import BioInfoProcesses
from .data_file import DataFile
from .import_bundle_factory import make_import_bundle_from_files
from .logger import configure_logging
from .wet_processes import WetProcesses

logger = logging.getLogger("genelastic")
logging.getLogger("elastic_transport").setLevel(
    logging.WARNING
)  # Disable excessive logging
logging.getLogger("urllib3").setLevel(
    logging.WARNING
)  # Disable excessive logging


def read_args() -> argparse.Namespace:
    """Read arguments from command line."""
    parser = argparse.ArgumentParser(
        description="Genetics data importer.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    add_verbose_control_args(parser)
    add_es_connection_args(parser)
    parser.add_argument(
        "-D",
        "--dry-run",
        dest="dryrun",
        action="count",
        default=0,
        help=(
            "Dry-run level. -D for data files loading (VCF, coverage, etc) "
            "without connecting or importing to database. "
            "-DD for metadata YAML files loading only (no loading of data files)."
        ),
    )
    parser.add_argument(
        "--log-file", dest="log_file", help="Path to a log file."
    )
    parser.add_argument(
        "--no-list",
        dest="no_list",
        action="store_true",
        help="Do not print list of files to be imported.",
    )
    parser.add_argument(
        "--no-confirm",
        dest="no_confirm",
        action="store_true",
        help="Do not ask confirmation before importing.",
    )
    parser.add_argument(
        "files",
        type=Path,
        nargs="+",
        default=None,
        help="Data files that describe what to import.",
    )
    return parser.parse_args()


def import_cov_file(
    es_import_conn: ElasticImportConn | None,
    file_index: str,
    file: Path,
    dryrun: int = 0,
) -> None:
    """Import a coverage file to the Elasticsearch database."""
    # Set field types
    if dryrun == 0 and es_import_conn:
        es_import_conn.client.indices.put_mapping(
            index=file_index,
            body={
                "properties": {
                    "pos": {"type": "integer"},
                    "depth": {"type": "byte"},
                }
            },
        )

    # Open file
    if dryrun > 1:
        logger.info(
            "Would load and import Coverage file %s " "into index %s.",
            file,
            file_index,
        )
    else:
        logger.info("Load Coverage file %s.", file)
        if dryrun == 1:
            logger.info(
                "Would import Coverage file %s into index %s.", file, file_index
            )
        else:
            logger.info(
                "Import Coverage file %s into index %s.", file, file_index
            )
        with file.open(newline="", encoding="utf-8") as f:
            # Read file as CSV
            reader = csv.reader(f, delimiter="\t", quotechar='"')

            # Loop on al lines
            for row in reader:
                # Build document
                # Position starts at 0 inside coverage file
                doc: MetadataDocument = {
                    "type": "coverage",
                    "chr": row[0],
                    "pos": int(row[1]) + 1,
                    "depth": int(row[2]),
                }

                # Insert document
                if dryrun == 0 and es_import_conn:
                    es_import_conn.client.index(index=file_index, document=doc)


def import_analysis_metadata(  # noqa: PLR0913
    es_import_conn: ElasticImportConn | None,
    index_prefix: str,
    file_index: str,
    file: DataFile,
    analysis_type: str,
    dryrun: int = 0,
) -> None:
    """Import analysis metadata into a dedicated index."""
    doc: AnalysisDocument = {
        "path": str(file.path.resolve()),
        "bundle_path": str(file.bundle_path.resolve())
        if file.bundle_path
        else None,
        "metadata": file.metadata,
        "file_index": file_index,
        "type": analysis_type,
    }

    bulk_items: BulkItems = [
        {"_index": f"{index_prefix}-analyses", "_source": doc}
    ]

    if dryrun == 0 and es_import_conn:
        es_import_conn.import_items(
            bulk_items,
            start_time=time.perf_counter(),
            total_items=len(bulk_items),
        )


def import_vcf_file(
    es_import_conn: ElasticImportConn | None,
    file_index: str,
    file: DataFile,
    dryrun: int = 0,
) -> None:
    """Import a VCF file to the Elasticsearch database."""
    logger.info('Import VCF file "%s".', file)

    if dryrun > 1:
        logger.info(
            "Would load and import VCF file %s " "into index %s.",
            file.path,
            file_index,
        )
    else:
        logger.info("Load VCF file %s.", file.path)
        if dryrun == 1:
            logger.info(
                "Would import VCF file %s into index %s.", file.path, file_index
            )
        else:
            logger.info(
                "Importing VCF file %s into index %s...", file.path, file_index
            )

        try:
            vcf_reader = vcf.Reader(filename=str(file.path))
            n = 0
            start = time.perf_counter()
            bulk_sz = 256  # Bulk size
            bulk_items: BulkItems = []
            for record in vcf_reader:
                # Correct values
                if not record.CHROM.startswith("chr"):
                    if record.CHROM.lower().startswith("chr"):
                        record.CHROM = "chr" + record.CHROM[3:]
                    else:
                        record.CHROM = "chr" + record.CHROM

                # Build document
                alt = [x if x is None else x.type for x in record.ALT]
                doc: MetadataDocument = {
                    "type": "vcf",
                    "chr": record.CHROM,
                    "pos": record.POS,
                    "alt": alt,
                    "info": record.INFO,
                }

                if dryrun == 0:
                    # Append item to bulk
                    bulk_items.append({"_index": file_index, "_source": doc})
                    n += 1

                    # Insert bulk of items
                    if len(bulk_items) >= bulk_sz and es_import_conn:
                        es_import_conn.import_items(
                            bulk_items, start_time=start, total_items=n
                        )
                        bulk_items = []

            # Insert remaining items
            if dryrun == 0 and es_import_conn:
                es_import_conn.import_items(
                    bulk_items, start_time=start, total_items=n
                )

        except StopIteration:
            logger.error("Skipping empty file : %s.", file.path)


def import_processes(
    es_import_conn: ElasticImportConn | None,
    index: str,
    processes: WetProcesses | BioInfoProcesses,
    dryrun: int = 0,
) -> None:
    """Import processes into their own index."""
    bulk_items: BulkItems = []

    for proc_id in processes.get_process_ids():
        process = processes[proc_id]
        process_type = process.__class__.__name__
        doc: ProcessDocument = process.data | {
            "proc_id": proc_id,
            "type": process_type,
        }
        bulk_items.append({"_index": index, "_source": doc})

    if dryrun == 0 and es_import_conn:
        es_import_conn.import_items(
            bulk_items,
            start_time=time.perf_counter(),
            total_items=len(bulk_items),
        )


def generate_unique_index(index_prefix: str, filepath: Path) -> str:
    """Generate a unique index with the following format:
    <index_prefix>_<current_date>_<md5_hashed_filepath>
    """
    current_date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d")
    hashed_filepath = hashlib.md5(
        str(filepath).encode("utf-8"), usedforsecurity=False
    ).hexdigest()
    return f"{index_prefix}-file-{current_date}-{hashed_filepath}"


def main() -> None:  # noqa: C901
    """Entry point of the import script."""
    # Read command line arguments
    args = read_args()

    # Configure logging
    configure_logging(args.verbose, log_file=args.log_file)
    logger.debug("Arguments: %s", args)
    logger.debug("LOGGERS: %s", logging.root.manager.loggerDict)

    # Open connection to ES
    if args.dryrun == 0:
        addr = f"https://{args.es_host}:{args.es_port}"
        logger.info("Trying to connect to Elasticsearch at %s...", addr)
        es_import_conn = ElasticImportConn(
            addr, args.es_cert_fp, basic_auth=(args.es_usr, args.es_pwd)
        )
    else:
        es_import_conn = None

    # Load YAML import bundle
    import_bundle = make_import_bundle_from_files(args.files, check=True)
    all_bundled_files = import_bundle.get_files()

    # CHECK
    for f in all_bundled_files:
        if not f.exists():
            msg = f"Path {f.path} does not point to a valid file."
            raise RuntimeError(msg)

    # LIST
    if not args.no_list:
        for f in all_bundled_files:
            logger.info("Will import %s.", f.path)

    # Ask confirmation for importing
    if not args.no_confirm:
        answer: str = "maybe"
        while answer not in ["", "n", "y"]:
            answer = input("Import (y/N)? ").lower()
        if answer != "y":
            logger.info("Import canceled.")
            sys.exit(0)

    # IMPORT
    # Loop on file categories
    for cat in import_bundle.analyses.get_all_categories():
        # Import all files in this category.
        for f in import_bundle.get_files(cat):
            logger.info("Import %s files from %s.", cat, f.path)
            # First, generate a unique index name for each file.
            file_index = generate_unique_index(args.es_index_prefix, f.path)
            # Then, import the analysis metadata into a dedicated index.
            import_analysis_metadata(
                es_import_conn,
                args.es_index_prefix,
                file_index,
                f,
                cat,
                args.dryrun,
            )
            # Finally, import the file in its own index.
            globals()[f"import_{cat}_file"](
                es_import_conn=es_import_conn,
                file_index=file_index,
                file=f,
                dryrun=args.dryrun,
            )

    # Import processes
    logger.info("Importing wet processes.")
    logger.info(
        "Wet processes IDs = %s",
        str(import_bundle.wet_processes.get_process_ids()),
    )
    import_processes(
        es_import_conn,
        f"{args.es_index_prefix}-wet_processes",
        import_bundle.wet_processes,
    )

    logger.info("Importing bio info processes.")
    logger.info(
        "Bio info processes IDs = %s",
        str(import_bundle.bi_processes.get_process_ids()),
    )
    import_processes(
        es_import_conn,
        f"{args.es_index_prefix}-bi_processes",
        import_bundle.bi_processes,
    )


if __name__ == "__main__":
    main()
