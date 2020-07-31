import types
from unittest.mock import Mock

import pytest
from bson import ObjectId

from mongonator import Paginate
from mongonator.paginator import PaginatedResponse


@pytest.fixture
def mongo_collection():
    yield Mock()


def test_paginate_one_batch(mongo_collection):
    mongo_collection.find.return_value.sort.return_value.limit.return_value = []
    paginator = Paginate(mongo_collection, 1, 1, '_id')
    response = paginator.paginate_one_batch()

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )
    assert response == PaginatedResponse(
        response=[], prev_page=None, next_page=None, batch_size=0
    )


def test_paginate_one_batch_with_pages(mongo_collection):
    mongo_collection.find.return_value.sort.return_value.limit.return_value = [{
        'id': 1
    }, {
        'id': 2
    }]
    paginator = Paginate(mongo_collection, 1, 1, '_id')
    response = paginator.paginate_one_batch()

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )

    assert isinstance(response, PaginatedResponse)
    assert response.response == [{'id': 1}]
    assert response.next_page is not None


def test_paginate(mongo_collection):
    returned_data = [
        {
            "_id": ObjectId("5ee1e040d3bcce48e169620b"),
            'id': 1
        },
    ]

    mongo_collection.find.return_value.sort.return_value.limit.return_value = returned_data
    paginator = Paginate(mongo_collection, 1, 1, 'id', automatic_pagination=True)
    response = paginator.paginate()
    assert isinstance(response, types.GeneratorType)

    for idx, r in enumerate(response):
        assert isinstance(r, PaginatedResponse)
        assert r.response == [returned_data[idx]]
        assert r.next_page is None

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )


def test_paginate_no_automatic(mongo_collection):
    returned_data = [
        {
            "_id": ObjectId("5ee1e040d3bcce48e169620b"),
            'id': 1
        },
    ]

    mongo_collection.find.return_value.sort.return_value.limit.return_value = returned_data
    paginator = Paginate(mongo_collection, 1, 1, 'id', automatic_pagination=False)
    response = paginator.paginate()

    assert isinstance(response, PaginatedResponse)
    assert response.response == [{
        "_id": ObjectId("5ee1e040d3bcce48e169620b"),
        'id': 1
    }]
    assert response.next_page is None

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )
