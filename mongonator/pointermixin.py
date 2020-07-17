import base64
import pickle

from mongonator import ASCENDING, DESCENDING


class PointerMixin:
    def encode(self, collection_data, field):
        return base64.b64encode(pickle.dumps((collection_data.get(field), collection_data.get("_id"))))

    def decode(self, encoded_pointer):
        if encoded_pointer is not None:
            return pickle.loads(base64.b64decode(encoded_pointer))
        return None

    def paginator_pointers(self, collection_data, ordering_case, field):
        paginator_pointers = {
            'prev_page': None,
            'next_page': None
        }
        if ordering_case == 'initial':
            paginator_pointers['next_page'] = self.encode(collection_data[-1], field)
        elif ordering_case == 'ahead':
            paginator_pointers['prev_page'] = self.encode(collection_data[0], field)
        elif ordering_case == 'both':
            paginator_pointers['prev_page'] = self.encode(collection_data[0], field)
            paginator_pointers['next_page'] = self.encode(collection_data[-1], field)

        return paginator_pointers

    def get_page_order(self, ordering_case, next=False):
        def _get_next_page_order(ordering_case):
            if ordering_case == ASCENDING:
                return '$gt', ASCENDING
            return '$lt', DESCENDING

        def _get_prev_page_order(ordering_case):
            if ordering_case == ASCENDING:
                return '$lt', DESCENDING
            return '$gt', ASCENDING

        return _get_next_page_order(ordering_case) if next else _get_prev_page_order(ordering_case)
