from collections import namedtuple

from bson import ObjectId
from pymongo.collation import Collation

from mongonator.pointermixin import PointerMixin
from mongonator.wrapper import DefaultResponseWrapper, ChatResponseWrapper

PaginatedResponse = namedtuple("PaginatedResponse", "response prev_page next_page batch_size")


class Query(PointerMixin):
    # Default response wrapper to display results
    response_wrapper = DefaultResponseWrapper

    def __init__(self, query, ordering_case, ordering_field, response_wrapper, projection):
        self._ordering = ordering_case
        self._ordering_field = ordering_field
        self._query = query or {}

        # Filter criteria to query results from collection
        self._mongo_filter = {}

        # Default response wrapper
        self.response_wrapper = ChatResponseWrapper if response_wrapper == "chat" else self.response_wrapper

        # Make a copy of projection to add _id as is required for pagination
        self._projection = projection or {}
        self._projection_copy = self._projection.copy()
        self._projection_copy.update(**{"_id": True, ordering_field: True})

    def _build_mongo_filter(self, ordering_field, _id, mongo_key):
        if self._ordering_field != "_id":
            next_page_query = [
                {self._ordering_field: {mongo_key: ordering_field}},
                {self._ordering_field: ordering_field, "_id": {mongo_key: ObjectId(_id)}},
            ]

            if "$or" in self._mongo_filter:
                self._mongo_filter["$and"] = [{"$or": next_page_query}, {"$or": self._mongo_filter.pop("$or")}]
            else:
                self._mongo_filter["$or"] = next_page_query
        else:
            self._mongo_filter["_id"] = {mongo_key: ObjectId(_id)}

    def _build_internal_structures(self, paginator_pointer, next):
        mongo_key, ordering = self.get_page_order(self._ordering, next)
        paginated_ordering_field, _id = self.decode(paginator_pointer)
        self._build_sortable_filter(ordering)
        self._build_mongo_filter(paginated_ordering_field, _id, mongo_key)

    def build_query(self, prev_page, next_page):
        if self._query is not None:
            self._mongo_filter.update(**self._query)

        if prev_page is not None:
            self._build_internal_structures(prev_page, False)
        elif next_page is not None:
            self._build_internal_structures(next_page, True)
        else:
            self._build_sortable_filter(self._ordering)

    def run_query(self, collection, page_size, collation, extra_pipeline, prev_page=None, next_page=None):
        """Run query against mongodb and return the paginated response"""
        self.build_query(prev_page, next_page)

        mongo_response = list(
            self(collection=collection, page_size=page_size, collation=collation, extra_pipeline=extra_pipeline)
        )

        paginator_pointers = self.paginator_pointers(mongo_response, "None", self._ordering_field)
        batch_size = len(mongo_response)
        has_next_page = batch_size > page_size

        if mongo_response:
            # If has next page, pop last element
            if has_next_page:
                mongo_response = mongo_response[:-1]

            # Is first query?
            if prev_page is None and next_page is None:
                if has_next_page:
                    paginator_pointers = self.paginator_pointers(mongo_response, "initial", self._ordering_field)
                else:
                    paginator_pointers = self.paginator_pointers(mongo_response, "", self._ordering_field)
            else:
                # Go back?
                if prev_page is not None:
                    mongo_response = mongo_response[::-1]  # reverse order

                    if has_next_page:
                        paginator_pointers = self.paginator_pointers(mongo_response, "both", self._ordering_field)
                    else:
                        paginator_pointers = self.paginator_pointers(mongo_response, "initial", self._ordering_field)
                else:
                    if has_next_page:
                        paginator_pointers = self.paginator_pointers(mongo_response, "both", self._ordering_field)
                    else:
                        paginator_pointers = self.paginator_pointers(mongo_response, "ahead", self._ordering_field)

        return PaginatedResponse(
            response=self.response_wrapper(mongo_response).format(),
            prev_page=paginator_pointers.get("prev_page"),
            next_page=paginator_pointers.get("next_page"),
            batch_size=page_size if (page_size - batch_size) == -1 else batch_size,
        )


class FindQuery(Query):
    mongo_method = "find"

    # Ordering ordering_field to sort
    sortable_filter = []

    def _build_sortable_filter(self, ordering):
        if self._ordering_field != "_id":
            self.sortable_filter.append((self._ordering_field, ordering))

        self.sortable_filter.append(("_id", self._ordering))

    def __call__(self, collection, page_size, collation, **kwargs):
        return (
            getattr(collection, self.mongo_method)(filter=self._mongo_filter, projection=self._projection_copy)
            .sort(self.sortable_filter)
            .collation(Collation(**collation) if collation else None)
            .limit(page_size + 1)
        )


class AggregateQuery(Query):
    mongo_method = "aggregate"

    # Ordering ordering_field to sort
    sortable_filter = {}

    def _build_sortable_filter(self, ordering):
        if self._ordering_field != "_id":
            self.sortable_filter[self._ordering_field] = ordering

        self.sortable_filter["_id"] = self._ordering

    def sanitize_pipeline(self, extra_pipeline):
        """Sanitize project stage in extra_pipeline to avoid drop needed fields for pagination"""
        sanitized_fields = set(self._projection_copy.keys()) - set(self._projection.keys())

        if sanitized_fields:
            for stage in extra_pipeline:
                if "$project" in stage.keys():
                    stage["$project"].update(**{"_id": True, self._ordering_field: True})

    def __call__(self, collection, page_size, collation, extra_pipeline, **kwargs):
        # Drop redundant kwargs
        kwargs.pop("allowDiskUse", None)
        self.sanitize_pipeline(extra_pipeline=extra_pipeline)

        return getattr(collection, self.mongo_method)(
            [
                {"$match": self._mongo_filter},
                {"$project": self._projection_copy},
                {"$sort": self.sortable_filter},
                {"$limit": page_size + 1},
            ]
            + extra_pipeline,
            collation=Collation(**collation) if collation else None,
            allowDiskUse=True,
            **kwargs,
        )
