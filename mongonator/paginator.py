from typing import Optional, Union, Literal

from pymongo.collection import Collection

from mongonator import settings
from mongonator.query import FindQuery, AggregateQuery


class Paginate:
    """Bucket pattern paginator over mongo documents"""

    # Default lookup engine to perform the queries against mongodb
    queryset = FindQuery

    # The default page size
    page_size = settings.DEFAULT_LIMIT

    # The default ordering case
    ordering = settings.DEFAULT_ORDERING_FIELD

    def __init__(
        self,
        collection: Collection,
        limit: int,
        ordering_case: int,
        ordering_field: str,
        query: Optional[dict] = None,
        projection: Optional[dict] = None,
        collation: Optional[dict] = None,
        automatic_pagination: Optional[bool] = True,
        extra_pipeline: Optional[list] = None,
        response_format: Literal["chat", "default"] = "default",
    ):
        projection = projection or {}
        projection_copy = projection.copy()

        # Add _id as default projection
        projection_copy.update(**{"_id": True})

        # Get original projection to avoid passing non requested fields in response
        dropped_fields = {field: False for field in list(set(projection_copy.keys()) - set(projection.keys()))}

        # Complex queries needs aggregate framework
        if dropped_fields or collation or extra_pipeline:
            self.queryset = AggregateQuery

        # Instance queryset
        self.queryset = self.queryset(
            query=query,
            ordering_case=ordering_case,
            ordering_field=ordering_field,
            response_wrapper=response_format,
            excluded_fields=dropped_fields,
        )

        self._collection = collection
        self._projection = projection
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
                projection=self._projection,
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
            projection=self._projection,
            collation=self._collation,
            extra_pipeline=self._extra_pipeline,
            prev_page=prev_page,
            next_page=next_page,
        )

        if self._automatic_pagination:
            return self._pagination_in_batches(response)
        else:
            return response
