import datetime
import logging
import time
import typing
from abc import ABC
from typing import Any

import elastic_transport
import elasticsearch.helpers
from elasticsearch import Elasticsearch

from .exceptions import DBIntegrityError
from .types import Bucket, BulkItems

logger = logging.getLogger("genelastic")


class ElasticConn(ABC):
    """Abstract class representing a connector for an Elasticsearch server."""

    client: Elasticsearch

    def __init__(self, url: str, fingerprint: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize an elasticsearch client instance.

        :url: URL of the Elasticsearch host.
        :fingerprint: sha256 certificate fingerprint for a secure HTTP connection.
        :returns: The configured elasticsearch client instance.
        :raises SystemExit: If the connection to the Elasticsearch server failed.
        """
        try:
            self.client = Elasticsearch(
                url,
                ssl_assert_fingerprint=fingerprint,
                # Verify cert only when the fingerprint is not None.
                verify_certs=bool(fingerprint),
                **kwargs,
            )
            self.client.info()
        except (
            elastic_transport.TransportError,
            elasticsearch.AuthenticationException,
        ) as e:
            raise SystemExit(e) from e


class ElasticImportConn(ElasticConn):
    """Connector to import data into an Elasticsearch database."""

    def import_items(
        self, bulk_items: BulkItems, start_time: float, total_items: int
    ) -> None:
        """Import items to the Elasticsearch database."""
        if len(bulk_items) > 0:
            elasticsearch.helpers.bulk(self.client, bulk_items)
        elapsed = time.perf_counter() - start_time
        logger.info(
            "Imported %d items in %s (%f items/s).",
            total_items,
            datetime.timedelta(seconds=elapsed),
            total_items / elapsed,
        )


class ElasticQueryConn(ElasticConn):
    """Connector to query data from an Elasticsearch database."""

    def get_indices(self) -> Any | str:  # noqa: ANN401
        """Return all indices."""
        return self.client.cat.indices(format="json").body

    def get_document_by_id(self, index: str, document_id: str) -> Any | str:  # noqa: ANN401
        """Return a document by its ID."""
        return self.client.get(index=index, id=document_id).body

    def run_composite_aggregation(
        self, index: str, query: dict[str, typing.Any]
    ) -> list[Bucket]:
        """Executes a composite aggregation on an Elasticsearch index and
        returns all paginated results.

        :param index: Name of the index to query.
        :param query: Aggregation query to run.
        :return: List of aggregation results.
        """
        # Extract the aggregation name from the query dict.
        agg_name = next(iter(query["aggs"]))
        all_buckets: list[Bucket] = []

        try:
            logger.debug(
                "Running composite aggregation query %s on index '%s'.",
                query,
                index,
            )
            response = self.client.search(index=index, body=query)
        except elasticsearch.NotFoundError as e:
            msg = f"Error: {e.message} for index '{index}'."
            raise SystemExit(msg) from e

        while True:
            # Extract buckets from the response.
            buckets: list[Bucket] = response["aggregations"][agg_name][
                "buckets"
            ]
            all_buckets.extend(buckets)

            # Check if there are more results to fetch.
            if "after_key" in response["aggregations"][agg_name]:
                after_key = response["aggregations"][agg_name]["after_key"]
                query["aggs"][agg_name]["composite"]["after"] = after_key
                try:
                    logger.debug(
                        "Running query %s on index '%s'.", query, index
                    )
                    # Fetch the next page of results.
                    response = self.client.search(index=index, body=query)
                except elasticsearch.NotFoundError as e:
                    msg = f"Error: {e.message} for index '{index}'."
                    raise SystemExit(msg) from e
            else:
                break

        return all_buckets

    def get_field_values(self, index: str, field_name: str) -> set[str]:
        """Return a set of values for a given field."""
        values = set()

        query = {
            "size": 0,
            "aggs": {
                "get_field_values": {
                    "composite": {
                        "sources": {
                            "values": {
                                "terms": {"field": f"{field_name}.keyword"}
                            }
                        },
                        "size": 1000,
                    }
                }
            },
        }

        buckets: list[Bucket] = self.run_composite_aggregation(index, query)

        for bucket in buckets:
            values.add(bucket["key"]["values"])

        return values

    def search_by_field_value(
        self, index: str, field: str, value: str
    ) -> dict[str, typing.Any] | None:
        """Search a document by a value for a certain field."""
        logger.info(
            "Searching for field '%s' with value '%s' inside index '%s'.",
            field,
            value,
            index,
        )
        search_query = {
            "query": {
                "term": {
                    f"{field}.keyword": value,
                }
            }
        }

        response = self.client.search(index=index, body=search_query)

        try:
            return response["hits"]["hits"][0]["_source"]  # type: ignore[no-any-return]
        except KeyError:
            return None

    def ensure_unique(self, index: str, field: str) -> None:
        """Ensure that all values of a field in an index are all unique.

        :param index: Name of the index.
        :param field: Field name to check for value uniqueness.
        :raises genelastic.common.DBIntegrityError:
            Some values of the given field are duplicated in the index.
        """
        logger.info(
            "Ensuring that the field '%s' in the index '%s' only contains unique values...",
            field,
            index,
        )
        query = {
            "size": 0,
            "aggs": {
                "duplicate_proc_ids": {
                    "terms": {
                        "field": f"{field}.keyword",
                        "size": 10000,
                        "min_doc_count": 2,
                    }
                }
            },
        }
        buckets: list[Bucket] = self.run_composite_aggregation(index, query)
        duplicated_processes: set[str] = {
            str(bucket["key"]) for bucket in buckets
        }

        if len(duplicated_processes) > 0:
            msg = f"Found non-unique value for field {field} in index '{index}': {', '.join(duplicated_processes)}."
            raise DBIntegrityError(msg)

        logger.info(
            "All values of field '%s' in index '%s' are unique.", field, index
        )
