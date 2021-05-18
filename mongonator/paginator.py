import logging
from typing import Optional

from pymongo.collection import Collection

import mongonator
from mongonator import settings
from mongonator.exceptions import MongonatorError
from mongonator.query import FindQuery, AggregateQuery

logger = logging.getLogger("mongonnator")


class Paginate:
    """Bucket pattern paginator over mongo documents"""

    # Default lookup engine to perform the queries against mongodb
    queryset = FindQuery

    def __init__(
        self,
        collection: Collection,
        limit: int,
        ordering_case: int,
        ordering_field: str = settings.DEFAULT_ORDERING_FIELD,
        query: Optional[dict] = None,
        projection: Optional[dict] = None,
        collation: Optional[dict] = None,
        automatic_pagination: Optional[bool] = True,
        extra_pipeline: Optional[list] = None,
        use_aggregate_framework: bool = False,
        response_format: Optional[str] = "default",
    ):
        if ordering_field is None:
            raise MongonatorError("Ordering field must be set and cannot be None. You can leave the default "
                                  "ordering_field (internal mongo _id).")

        # Complex queries needs aggregate framework
        if extra_pipeline or use_aggregate_framework:
            self.queryset = AggregateQuery

        if ordering_case == mongonator.ASCENDING and response_format == "chat":
            logger.warning(
                "Response format 'chat' requires DESCENDING order, but ASCENDING order has been found. "
                "Ordering case has been changed."
            )
            ordering_case = mongonator.DESCENDING

        # Instance queryset
        self.queryset = self.queryset(
            query=query,
            ordering_case=ordering_case,
            ordering_field=ordering_field,
            response_wrapper=response_format,
            projection=projection,
        )

        self._collection = collection
        self._limit = limit
        self._automatic_pagination = automatic_pagination
        self._extra_pipeline = extra_pipeline or []
        self._collation = collation or {}

    def _pagination_in_batches(self, response):
        yield response
        while response.next_page:
            response = self.queryset.run_query(
                collection=self._collection,
                page_size=self._limit,
                collation=self._collation,
                extra_pipeline=self._extra_pipeline,
                next_page=response.next_page,
            )
            yield response

    def paginate(self, prev_page, next_page):
        """Paginate in batches of `limit` size over entire collection"""

        response = self.queryset.run_query(
            collection=self._collection,
            page_size=self._limit,
            collation=self._collation,
            extra_pipeline=self._extra_pipeline,
            prev_page=prev_page,
            next_page=next_page,
        )

        if self._automatic_pagination:
            return self._pagination_in_batches(response)
        else:
            return response
