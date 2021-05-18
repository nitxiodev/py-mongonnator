""" Simple paginator for PyMongo driver using bucket pattern """
from pymongo import MongoClient as MongoClientWithPagination
from pymongo.collection import Collection
from pymongo.database import Database

from mongonator.paginator import Paginate
from mongonator.settings import DEFAULT_LIMIT, DESCENDING, DEFAULT_ORDERING_FIELD, ASCENDING


class PaginatedCollection(Collection):
    def paginate(
        self,
        query=None,
        projection=None,
        prev_page=None,
        next_page=None,
        limit=DEFAULT_LIMIT,
        ordering=DESCENDING,
        ordering_field=DEFAULT_ORDERING_FIELD,
        automatic_pagination=True,
        collation=None,
        extra_pipeline=None,
        use_aggregate_framework=False,
        response_format="default",
    ):
        return Paginate(
            collection=self,
            limit=limit,
            ordering_field=ordering_field,
            ordering_case=ordering,
            query=query,
            projection=projection,
            collation=collation,
            automatic_pagination=automatic_pagination,
            extra_pipeline=extra_pipeline,
            use_aggregate_framework=use_aggregate_framework,
            response_format=response_format,
        ).paginate(
            prev_page=prev_page,
            next_page=next_page,
        )


def getitem(self, name):
    """Override collection class in Database"""
    return PaginatedCollection(self, name)


Database.__getitem__ = getitem

name = "Mongonator"
__all__ = ["MongoClientWithPagination", "DEFAULT_LIMIT", "DEFAULT_ORDERING_FIELD", "ASCENDING", "DESCENDING"]
__version__ = "v2.0.0b"
