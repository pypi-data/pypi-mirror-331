from importlib.metadata import version
from pathlib import Path
from typing import Any

from flask import Response, current_app, jsonify


def ping() -> Response:
    """Test route to verify that the server is online."""
    return jsonify({"message": "pong"})


def list_indices() -> Response:
    """Route to list Elasticsearch indexes."""
    return current_app.elastic_query_conn.get_indices()  # type: ignore[attr-defined, no-any-return]


def retrieve_document(index_id: str, document_id: str) -> Response:
    """Route to retrieve a document by its ID."""
    document = current_app.elastic_query_conn.get_document_by_id(  # type: ignore[attr-defined]
        index_id, document_id
    )
    return jsonify(document)


def list_wet_processes() -> Response:
    """Route to list wet processes."""
    wet_processes_index = (
        f"{current_app.config['GENAPI_ES_INDEX_PREFIX']}-wet_processes"
    )
    result = current_app.elastic_query_conn.get_field_values(  # type: ignore[attr-defined]
        wet_processes_index, "proc_id"
    )
    return jsonify(list(result))


def list_bi_processes() -> Response:
    """Route to list bi processes."""
    bi_processes_index = (
        f"{current_app.config['GENAPI_ES_INDEX_PREFIX']}-bi_processes"
    )
    result = current_app.elastic_query_conn.get_field_values(  # type: ignore[attr-defined]
        bi_processes_index, "proc_id"
    )
    return jsonify(list(result))


def list_analyses() -> Response:
    """Route to list analyses."""
    analyses_index = f"{current_app.config['GENAPI_ES_INDEX_PREFIX']}-analyses"
    result = current_app.elastic_query_conn.get_field_values(  # type: ignore[attr-defined]
        analyses_index, "path"
    )
    filenames = [Path(path).name for path in result]
    return jsonify(filenames)


def list_analyses_wet_processes(proc_id: str) -> Response:
    """Route to list analyses one of specific wet process"""
    analyses_index = f"{current_app.config['GENAPI_ES_INDEX_PREFIX']}-analyses"

    search_query = {
        "query": {
            "term": {
                "metadata.wet_process.keyword": proc_id,
            }
        }
    }
    response = current_app.elastic_query_conn.client.search(  # type: ignore[attr-defined]
        index=analyses_index, body=search_query
    )
    result = [hit["_source"]["path"] for hit in response["hits"]["hits"]]

    return jsonify(result)


def list_analyses_bi_processes(proc_id: str) -> Response:
    """Route to list analyses one of specific bi process"""
    analyses_index = f"{current_app.config['GENAPI_ES_INDEX_PREFIX']}-analyses"

    search_query = {
        "query": {
            "term": {
                "metadata.bi_process.keyword": proc_id,
            }
        }
    }
    response = current_app.elastic_query_conn.client.search(  # type: ignore[attr-defined]
        index=analyses_index, body=search_query
    )
    result = [hit["_source"]["path"] for hit in response["hits"]["hits"]]

    return jsonify(result)


def list_snv_documents() -> Response:
    """Route to list all documents containing a mutation at a single position (SNV)."""
    index_pattern = "genelastic-file-*"
    target_value = "SNV"

    search_query = {
        "aggs": {
            "snv_docs": {
                "composite": {
                    "sources": [
                        {"alt_value": {"terms": {"field": "alt.keyword"}}}
                    ],
                    "size": 1000,
                }
            }
        },
        "query": {"term": {"alt.keyword": target_value}},
        "size": 0,
    }

    all_documents = []
    buckets = current_app.elastic_query_conn.run_composite_aggregation(  # type: ignore[attr-defined]
        index_pattern, search_query
    )

    for bucket in buckets:
        alt_value = bucket["key"]["alt_value"]

        search_query_docs = {
            "query": {"term": {"alt.keyword": alt_value}},
            "size": 1000,
        }

        response = current_app.elastic_query_conn.client.search(  # type: ignore[attr-defined]
            index=index_pattern, body=search_query_docs
        )

        all_documents.extend(response["hits"]["hits"])

    return jsonify(all_documents)


def build_snv_search_query(
    target_alt: str, target_svtype: str
) -> dict[str, Any]:
    """Helper function to build the search query for SNV documents with specified alt and SVTYPE."""
    return {
        "query": {
            "bool": {
                "must": [
                    {"term": {"alt.keyword": target_alt}},
                    {"term": {"info.SVTYPE.keyword": target_svtype}},
                ]
            }
        },
        "size": 1000,
    }


def build_snv_mutation_search_query(
    target_svtypes: list[str],
) -> dict[str, Any]:
    """Helper function to build the search query for SNV mutations with specified SVTYPE values."""
    return {
        "query": {
            "bool": {
                "must": [
                    {"term": {"alt.keyword": "SNV"}},
                    {"terms": {"info.SVTYPE.keyword": target_svtypes}},
                ]
            }
        },
        "size": 1000,
    }


def list_snv_insertion_documents() -> Response:
    """Route to list all documents containing an insertion (INS) at a single position (SNV)."""
    index_pattern = "genelastic-file-*"
    search_query = build_snv_search_query(target_alt="SNV", target_svtype="INS")

    response = current_app.elastic_query_conn.client.search(  # type: ignore[attr-defined]
        index=index_pattern, body=search_query
    )

    all_documents = [hit["_source"] for hit in response["hits"]["hits"]]

    return jsonify(all_documents)


def list_snv_deletion_documents() -> Response:
    """Route to list all documents containing a deletion (DEL) at a single position (SNV)."""
    index_pattern = "genelastic-file-*"
    search_query = build_snv_search_query(target_alt="SNV", target_svtype="DEL")

    response = current_app.elastic_query_conn.client.search(  # type: ignore[attr-defined]
        index=index_pattern, body=search_query
    )

    all_documents = [hit["_source"] for hit in response["hits"]["hits"]]

    return jsonify(all_documents)


def list_snv_mutation_documents() -> Response:
    """Route to list all documents containing a mutation at a single position (SNV)."""
    index_pattern = "genelastic-file-*"
    target_svtypes = ["INS", "DEL"]

    search_query = build_snv_mutation_search_query(
        target_svtypes=target_svtypes
    )

    response = current_app.elastic_query_conn.client.search(  # type: ignore[attr-defined]
        index=index_pattern, body=search_query
    )

    all_documents = [hit["_source"] for hit in response["hits"]["hits"]]

    return jsonify(all_documents)


def get_genelastic_version() -> Response:
    """Retourne la version du package genelastic."""
    top_level_package = __package__.split(".")[0]
    return jsonify({"version": version(top_level_package)})
