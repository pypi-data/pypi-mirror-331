"""Utility functions for CLI scripts."""

import argparse

BASE_LOG_LEVEL = ["critical", "error", "warning", "info", "debug"]


def add_verbose_control_args(parser: argparse.ArgumentParser) -> None:
    """Add verbose control arguments to the parser.
    Arguments are added to the parser by using its reference.
    """
    parser.add_argument(
        "-q",
        "--quiet",
        dest="verbose",
        action="store_const",
        const=0,
        default=1,
        help="Set verbosity to 0 (quiet mode).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="count",
        default=1,
        help=(
            "Verbose level. -v for information, -vv for debug, -vvv for trace."
        ),
    )


def add_es_connection_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the parser needed to gather ElasticSearch server connection parameters.
    Arguments are added to the parser by using its reference.
    """
    parser.add_argument(
        "--es-host",
        dest="es_host",
        default="localhost",
        help="Address of Elasticsearch host.",
    )
    parser.add_argument(
        "--es-port",
        type=int,
        default=9200,
        dest="es_port",
        help="Elasticsearch port.",
    )
    parser.add_argument(
        "--es-usr", dest="es_usr", default="elastic", help="Elasticsearch user."
    )
    parser.add_argument(
        "--es-pwd", dest="es_pwd", required=True, help="Elasticsearch password."
    )
    parser.add_argument(
        "--es-cert-fp",
        dest="es_cert_fp",
        help="Elasticsearch sha256 certificate fingerprint.",
    )
    parser.add_argument(
        "--es-index-prefix",
        dest="es_index_prefix",
        help="Add the given prefix to each index created during import.",
    )


def parse_server_launch_args(
    parser_desc: str, default_port: int
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=parser_desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
    )

    env_subparsers = parser.add_subparsers(dest="env", required=True)
    dev_parser = env_subparsers.add_parser(
        "dev",
        help="Use development environment.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    dev_parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=[*BASE_LOG_LEVEL, "trace"],
    )

    prod_parser = env_subparsers.add_parser(
        "prod",
        help="Use production environment.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    prod_parser.add_argument(
        "--log-level", type=str, default="info", choices=BASE_LOG_LEVEL
    )
    prod_parser.add_argument(
        "-w", "--workers", type=int, default=1, help="Number of workers."
    )

    prod_parser.add_argument("--access-logfile", type=str, default=None)
    prod_parser.add_argument("--log-file", type=str, default=None)

    return parser.parse_args()
