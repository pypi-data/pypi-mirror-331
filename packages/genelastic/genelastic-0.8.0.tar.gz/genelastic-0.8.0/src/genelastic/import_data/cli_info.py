import argparse
import logging

from genelastic.common import (
    Bucket,
    ElasticQueryConn,
    add_es_connection_args,
    add_verbose_control_args,
)

from .logger import configure_logging

logger = logging.getLogger("genelastic")
logging.getLogger("elastic_transport").setLevel(
    logging.WARNING
)  # Disable excessive logging


def read_args() -> argparse.Namespace:
    """Read arguments from command line."""
    parser = argparse.ArgumentParser(
        description="ElasticSearch database info.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    add_verbose_control_args(parser)
    add_es_connection_args(parser)
    parser.add_argument(
        "-y",
        "--list-bundles",
        action="store_true",
        help="List all imported YAML bundles.",
    )
    parser.add_argument(
        "-f",
        "--list-data-files",
        action="store_true",
        help="List all imported data files.",
    )
    parser.add_argument(
        "-w",
        "--list-wet-processes",
        action="store_true",
        help="List all imported wet processes.",
    )
    parser.add_argument(
        "-b",
        "--list-bi-processes",
        action="store_true",
        help="List all imported bio info processes.",
    )
    parser.add_argument(
        "-Y",
        "--list-data-files-per-bundle",
        action="store_true",
        help="For each imported YAML bundle, "
        "display some info and list its data files.",
    )
    return parser.parse_args()


def list_bundles(es_query_conn: ElasticQueryConn, index: str) -> None:
    """List all imported YAML bundles."""
    query = {
        "size": 0,
        "aggs": {
            "get_bundle_paths": {
                "composite": {
                    "sources": {
                        "bundle_path": {
                            "terms": {"field": "bundle_path.keyword"}
                        }
                    },
                    "size": 1000,
                }
            }
        },
    }

    buckets: list[Bucket] = es_query_conn.run_composite_aggregation(
        index, query
    )

    logger.info("Imported YAML files")
    logger.info("===================")

    if len(buckets) == 0:
        logger.info("Empty response.")
        return

    for bucket in buckets:
        bundle_path = bucket["key"]["bundle_path"]
        logger.info("- %s", bundle_path)


def list_data_files(es_query_conn: ElasticQueryConn, index: str) -> None:
    """List all imported data files."""
    query = {
        "size": 0,
        "aggs": {
            "get_paths": {
                "composite": {
                    "sources": {"path": {"terms": {"field": "path.keyword"}}},
                    "size": 1000,
                }
            }
        },
    }

    buckets: list[Bucket] = es_query_conn.run_composite_aggregation(
        index, query
    )

    logger.info("Imported data files")
    logger.info("===================")

    if len(buckets) == 0:
        logger.info("Empty response.")
        return

    for bucket in buckets:
        bundle_path = bucket["key"]["path"]
        logger.info("- %s", bundle_path)


def list_processes(es_query_conn: ElasticQueryConn, index: str) -> None:
    """List all processes."""
    process_ids = es_query_conn.get_field_values(index, "proc_id")

    if len(process_ids) == 0:
        logger.info("Empty response.")
        return

    for process_id in process_ids:
        logger.info("- %s", process_id)


def list_wet_processes(es_query_conn: ElasticQueryConn, index: str) -> None:
    """List all wet processes."""
    logger.info("Imported wet processes")
    logger.info("======================")
    list_processes(es_query_conn, index)


def list_bi_processes(es_query_conn: ElasticQueryConn, index: str) -> None:
    """List all bio info processes."""
    logger.info("Imported bi processes")
    logger.info("=====================")
    list_processes(es_query_conn, index)


def list_data_files_per_bundle(
    es_query_conn: ElasticQueryConn, index: str
) -> None:
    """For each imported YAML bundle, display some info and list its data files."""
    query = {
        "size": 0,
        "aggs": {
            "data_files": {
                "composite": {
                    "sources": [
                        {
                            "bundle_path": {
                                "terms": {"field": "bundle_path.keyword"}
                            }
                        }
                    ],
                    "size": 100,
                },
                "aggs": {"docs": {"top_hits": {"size": 100}}},
            }
        },
    }

    buckets: list[Bucket] = es_query_conn.run_composite_aggregation(
        index, query
    )

    logger.info("Data files per YAML bundle")
    logger.info("==========================")

    if len(buckets) == 0:
        logger.info("Empty response.")
        return

    for bucket in buckets:
        documents = bucket["docs"]["hits"]["hits"]
        if len(documents) == 0:
            continue

        logger.info("- Bundle Path: %s", bucket["key"]["bundle_path"])
        logger.info(
            "    -> Wet process: %s",
            documents[0]["_source"]["metadata"]["wet_process"],
        )
        logger.info(
            "    -> Bio info process: %s",
            documents[0]["_source"]["metadata"]["bi_process"],
        )
        logger.info("    -> Data files:")

        for doc in documents:
            logger.info("        - Index: %s", doc["_source"]["file_index"])
            logger.info("          Path: %s", doc["_source"]["path"])


def main() -> None:
    """Entry point of the info script."""
    args = read_args()

    configure_logging(args.verbose)
    logger.debug("Arguments: %s", args)

    addr = f"https://{args.es_host}:{args.es_port}"
    logger.info("Trying to connect to Elasticsearch at %s...", addr)
    es_query_conn = ElasticQueryConn(
        addr, args.es_cert_fp, basic_auth=(args.es_usr, args.es_pwd)
    )

    analysis_index = f"{args.es_index_prefix}-analyses"
    wet_processes_index = f"{args.es_index_prefix}-wet_processes"
    bi_processes_index = f"{args.es_index_prefix}-bi_processes"

    list_call_count = 0

    if args.list_bundles:
        list_bundles(es_query_conn, analysis_index)
        list_call_count += 1

    if args.list_data_files:
        list_data_files(es_query_conn, analysis_index)
        list_call_count += 1

    if args.list_wet_processes:
        list_wet_processes(es_query_conn, wet_processes_index)
        list_call_count += 1

    if args.list_bi_processes:
        list_bi_processes(es_query_conn, bi_processes_index)
        list_call_count += 1

    if args.list_data_files_per_bundle:
        list_data_files_per_bundle(es_query_conn, analysis_index)
        list_call_count += 1

    if list_call_count == 0:
        logger.debug("No list option specified, listing everything.")
        list_bundles(es_query_conn, analysis_index)
        list_data_files(es_query_conn, analysis_index)
        list_wet_processes(es_query_conn, wet_processes_index)
        list_bi_processes(es_query_conn, bi_processes_index)
        list_data_files_per_bundle(es_query_conn, analysis_index)


if __name__ == "__main__":
    main()
