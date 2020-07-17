import pytest
from bson import ObjectId

from mongonator import ASCENDING, DESCENDING
from mongonator.pointermixin import PointerMixin


@pytest.fixture
def pointer_mixin():
    yield PointerMixin()


def test_decode(pointer_mixin):
    collection_data = {
        'mock_field': 'mocked_field',
        '_id': ObjectId('5ee7cb5dfce77c2d2b9d84f4')
    }

    encoded_data = pointer_mixin.encode(collection_data, field='mock_field')
    decoded_data = pointer_mixin.decode(encoded_data)

    assert decoded_data == (collection_data.get('mock_field'), collection_data.get('_id'))


def test_pagination_pointer_initial(pointer_mixin):
    collection_data = [{
        'mock_field': 'mocked_field',
        '_id': ObjectId('5ee7cb5dfce77c2d2b9d84f4')
    }]

    paginator_pointers = pointer_mixin.paginator_pointers(collection_data, 'initial', 'mock_field')
    assert paginator_pointers == {
        'prev_page': None,
        'next_page': pointer_mixin.encode(collection_data[-1], 'mock_field')
    }


def test_pagination_pointer_ahead(pointer_mixin):
    collection_data = [{
        'mock_field': 'mocked_field',
        '_id': ObjectId('5ee7cb5dfce77c2d2b9d84f4')
    }]

    paginator_pointers = pointer_mixin.paginator_pointers(collection_data, 'ahead', 'mock_field')
    assert paginator_pointers == {
        'prev_page': pointer_mixin.encode(collection_data[0], 'mock_field'),
        'next_page': None
    }


def test_pagination_pointer_both(pointer_mixin):
    collection_data = [{
        'mock_field': 'mocked_field',
        '_id': ObjectId('5ee7cb5dfce77c2d2b9d84f4')
    }]

    paginator_pointers = pointer_mixin.paginator_pointers(collection_data, 'both', 'mock_field')
    assert paginator_pointers == {
        'prev_page': pointer_mixin.encode(collection_data[0], 'mock_field'),
        'next_page': pointer_mixin.encode(collection_data[-1], 'mock_field')
    }


def test_get_page_order_prev_ascending_order(pointer_mixin):
    page_order = pointer_mixin.get_page_order(ASCENDING, next=False)
    assert page_order == ('$lt', DESCENDING)


def test_get_page_order_prev_descending_order(pointer_mixin):
    page_order = pointer_mixin.get_page_order(DESCENDING, next=False)
    assert page_order == ('$gt', ASCENDING)


def test_get_page_order_next_ascending_order(pointer_mixin):
    page_order = pointer_mixin.get_page_order(ASCENDING, next=True)
    assert page_order == ('$gt', ASCENDING)


def test_get_page_order_next_descending_order(pointer_mixin):
    page_order = pointer_mixin.get_page_order(DESCENDING, next=True)
    assert page_order == ('$lt', DESCENDING)
