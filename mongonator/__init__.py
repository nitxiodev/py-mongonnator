""" Simple paginator for PyMongo driver using bucket pattern """
import pymongo
from pymongo import MongoClient as MongoClientWithPagination
from pymongo.collection import Collection
from pymongo.database import Database

from mongonator.paginator import Paginate

# ORDERINGS
ASCENDING = pymongo.ASCENDING
DESCENDING = pymongo.DESCENDING

# DEFAULT ORDERING FIELD
DEFAULT_ORDERING_FIELD = '_id'

# DEFAULT PAGINATION LIMIT
DEFAULT_LIMIT = 75


class PaginatedCollection(Collection):
    def paginate(self, query=None, projection=None, prev_page=None, next_page=None,
                 limit=DEFAULT_LIMIT, ordering=DESCENDING, ordering_field=DEFAULT_ORDERING_FIELD,
                 automatic_pagination=True):
        return Paginate(self, query, projection, prev_page, next_page, limit, ordering, ordering_field,
                        automatic_pagination).paginate()


def getitem(self, name):
    """Override collection class in Database"""
    return PaginatedCollection(self, name)


Database.__getitem__ = getitem

name = 'Mongonator'
__all__ = ['MongoClientWithPagination']
