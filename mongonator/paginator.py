import base64
import pickle
from collections import namedtuple
from typing import Optional

import pymongo
from bson import ObjectId
from pymongo.collection import Collection

PaginatedResponse = namedtuple('PaginatedResponse', 'response prev_page next_page batch_size')


class Paginate:
    def __init__(self, collection: Collection, query: Optional[dict], projection: Optional[dict],
                 prev_page: Optional[str], next_page: Optional[str], limit: int, ordering_field: int, field: str):
        """
        Create a paginate instance to retrieve results from mongo collection in batches of limit.
        :param collection: Pointer to mongo collection
        :param query: query filter to pass into find method
        :param prev_page: Pointer to previous page
        :param next_page: Pointer to next page
        :param limit: Limit of results to retrieve from db
        :param ordering_field: Ordering case for pagination (pymongo.ASCENDING, pymongo.DESCENDING)
        :param field: Field used to paginate
        """
        self._collection = collection
        self._prev_page = self._decode_pointer(prev_page)
        self._next_page = self._decode_pointer(next_page)
        self._limit = limit
        self._ordering = ordering_field
        self._field = field
        self._query = query
        self._projection = projection

        # Ordering field to sort
        self._sortable_filter = []

        # Filter criteria to query results from collection
        self._mongo_filter = {}

    def _get_next_page_order(self):
        if self._ordering == pymongo.ASCENDING:
            return '$gt', pymongo.ASCENDING
        return '$lt', pymongo.DESCENDING

    def _get_prev_page_order(self):
        if self._ordering == pymongo.ASCENDING:
            return '$lt', pymongo.DESCENDING
        return '$gt', pymongo.ASCENDING

    def _build_sortable_filter(self, field, _id, mongo_key, ordering):
        if self._field != '_id':
            self._sortable_filter.append((self._field, ordering))
            next_page_query = [
                {self._field: {mongo_key: field}},
                {self._field: field,
                 '_id': {mongo_key: ObjectId(_id)}},
            ]

            if '$or' in self._mongo_filter:
                self._mongo_filter['$and'] = [
                    {'$or': next_page_query},
                    {'$or': self._mongo_filter.pop('$or')}
                ]
            else:
                self._mongo_filter['$or'] = next_page_query
        else:
            self._mongo_filter['_id'] = {mongo_key: ObjectId(_id)}

        self._sortable_filter.append(('_id', self._ordering))

    def _build_mongo_query(self):
        if self._query is not None:
            self._mongo_filter.update(**self._query)

        if self._prev_page is not None:
            mongo_key, ordering = self._get_prev_page_order()
            paginated_field, _id = self._prev_page
            self._build_sortable_filter(paginated_field, _id, mongo_key, ordering)

        elif self._next_page is not None:
            mongo_key, ordering = self._get_next_page_order()
            paginated_field, _id = self._next_page
            self._build_sortable_filter(paginated_field, _id, mongo_key, ordering)
        else:
            if self._field != '_id':
                self._sortable_filter.append((self._field, self._ordering))

            self._sortable_filter.append(('_id', self._ordering))

        # _id is mandatory to paginate
        if '_id' in self._projection:
            self._projection.pop('_id')

    def _is_first_query(self):
        return self._prev_page is None and self._next_page is None

    def _return_paginator_pointers(self, collection_data, ordering_case):
        paginator_pointers = {
            'prev_page': None,
            'next_page': None
        }
        if ordering_case == 'initial':

            paginator_pointers['next_page'] = self._encode_pointer(collection_data[-1])
        elif ordering_case == 'ahead':
            paginator_pointers['prev_page'] = self._encode_pointer(collection_data[0])
        elif ordering_case == 'both':
            paginator_pointers['prev_page'] = self._encode_pointer(collection_data[0])
            paginator_pointers['next_page'] = self._encode_pointer(collection_data[-1])

        return paginator_pointers

    def _encode_pointer(self, collection_data):
        return base64.b64encode(pickle.dumps((collection_data.get(self._field), collection_data.get("_id"))))

    def _decode_pointer(self, data):
        if data is not None:
            return pickle.loads(base64.b64decode(data))
        return None

    def paginate(self):
        self._build_mongo_query()

        mongo_response = list(
            self._collection.find(self._mongo_filter, projection=self._projection).sort(self._sortable_filter).limit(
                self._limit + 1)
        )
        paginator_pointers = self._return_paginator_pointers(mongo_response, 'None')
        batch_size = len(mongo_response)
        has_next_page = batch_size > self._limit

        if mongo_response:

            # If has next page, pop last element
            if has_next_page:
                mongo_response = mongo_response[:-1]

            # Is first query?
            if self._is_first_query():
                if has_next_page:
                    paginator_pointers = self._return_paginator_pointers(mongo_response, 'initial')
                else:
                    paginator_pointers = self._return_paginator_pointers(mongo_response, '')
            else:
                # Go back?
                if self._prev_page is not None:
                    mongo_response = mongo_response[::-1]  # reverse order

                    if has_next_page:
                        paginator_pointers = self._return_paginator_pointers(mongo_response, 'both')
                    else:
                        paginator_pointers = self._return_paginator_pointers(mongo_response, 'initial')
                else:
                    if has_next_page:
                        paginator_pointers = self._return_paginator_pointers(mongo_response, 'both')
                    else:
                        paginator_pointers = self._return_paginator_pointers(mongo_response, 'ahead')

        return PaginatedResponse(response=mongo_response,
                                 prev_page=paginator_pointers.get('prev_page'),
                                 next_page=paginator_pointers.get('next_page'),
                                 batch_size=self._limit if (self._limit - batch_size) == -1 else batch_size)
