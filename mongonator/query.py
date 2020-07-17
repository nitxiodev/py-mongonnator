from bson import ObjectId

from mongonator.pointermixin import PointerMixin


class Query(PointerMixin):
    def __init__(self, query, prev_page, next_page, ordering_case, field):
        self._ordering = ordering_case
        self._prev_page = prev_page
        self._next_page = next_page
        self._field = field
        self._query = query

        # Ordering field to sort
        self._sortable_filter = []

        # Filter criteria to query results from collection
        self._mongo_filter = {}

    @property
    def is_first_query(self):
        return self._prev_page is None and self._next_page is None

    def _build_mongo_filter(self, field, _id, mongo_key):
        if self._field != '_id':
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

    def _build_sortable_filter(self, ordering):
        if self._field != '_id':
            self._sortable_filter.append((self._field, ordering))

        self._sortable_filter.append(('_id', self._ordering))

    def _build_internal_structures(self, paginator_pointer, next):
        mongo_key, ordering = self.get_page_order(self._ordering, next)
        paginated_field, _id = self.decode(paginator_pointer)
        self._build_sortable_filter(ordering)
        self._build_mongo_filter(paginated_field, _id, mongo_key)

    def build_query(self):
        if self._query is not None:
            self._mongo_filter.update(**self._query)

        if self._prev_page is not None:
            self._build_internal_structures(self._prev_page, False)
        elif self._next_page is not None:
            self._build_internal_structures(self._next_page, True)
        else:
            self._build_sortable_filter(self._ordering)
