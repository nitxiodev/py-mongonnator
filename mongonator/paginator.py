from collections import namedtuple
from typing import Optional

from pymongo.collection import Collection

from mongonator.query import Query

PaginatedResponse = namedtuple('PaginatedResponse', 'response prev_page next_page batch_size')


class Paginate(Query):
    def __init__(self, collection: Collection, query: Optional[dict], projection: Optional[dict],
                 prev_page: Optional[str], next_page: Optional[str], limit: int, ordering_field: int, field: str,
                 automatic_pagination: Optional[bool]):
        """
        Create a paginate instance to retrieve results from mongo collection in batches of limit.
        :param collection: Pointer to mongo collection
        :param query: query filter to pass into find method
        :param prev_page: Pointer to previous page
        :param next_page: Pointer to next page
        :param limit: Limit of results to retrieve from db
        :param ordering_field: Ordering case for pagination (ASCENDING, DESCENDING)
        :param field: Field used to paginate
        """
        super(Paginate, self).__init__(query, prev_page, next_page, ordering_field, field)

        self._collection = collection
        self._limit = limit
        self._projection = projection
        self._automatic_pagination = automatic_pagination

        # _id is mandatory to paginate
        if '_id' in self._projection:
            self._projection.pop('_id')

    def paginate_one_batch(self):
        self.build_query()

        mongo_response = list(
            self._collection.find(self._mongo_filter, projection=self._projection).sort(self._sortable_filter).limit(
                self._limit + 1)
        )
        paginator_pointers = self.paginator_pointers(mongo_response, 'None', self._field)
        batch_size = len(mongo_response)
        has_next_page = batch_size > self._limit

        if mongo_response:

            # If has next page, pop last element
            if has_next_page:
                mongo_response = mongo_response[:-1]

            # Is first query?
            if self.is_first_query:
                if has_next_page:
                    paginator_pointers = self.paginator_pointers(mongo_response, 'initial', self._field)
                else:
                    paginator_pointers = self.paginator_pointers(mongo_response, '', self._field)
            else:
                # Go back?
                if self._prev_page is not None:
                    mongo_response = mongo_response[::-1]  # reverse order

                    if has_next_page:
                        paginator_pointers = self.paginator_pointers(mongo_response, 'both', self._field)
                    else:
                        paginator_pointers = self.paginator_pointers(mongo_response, 'initial', self._field)
                else:
                    if has_next_page:
                        paginator_pointers = self.paginator_pointers(mongo_response, 'both', self._field)
                    else:
                        paginator_pointers = self.paginator_pointers(mongo_response, 'ahead', self._field)

        return PaginatedResponse(response=mongo_response,
                                 prev_page=paginator_pointers.get('prev_page'),
                                 next_page=paginator_pointers.get('next_page'),
                                 batch_size=self._limit if (self._limit - batch_size) == -1 else batch_size)

    def paginate(self):
        """Paginate in batches of `limit` size over entire collection"""
        response = self.paginate_one_batch()

        if self._automatic_pagination:
            yield response
            while response.next_page:
                response = Paginate(self._collection, self._query, self._projection, self._prev_page,
                                    response.next_page, self._limit, self._ordering,
                                    self._field, self._automatic_pagination).paginate_one_batch()
                yield response
        else:
            return response
