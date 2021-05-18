import types
from unittest.mock import Mock

import pytest
from bson import ObjectId

from mongonator import Paginate, AsIsWrapper, ChatWrapper
from mongonator.paginator import PaginatedResponse


@pytest.fixture
def mongo_collection():
    yield Mock()


def test_paginate_one_batch(mongo_collection):
    mongo_collection.find.return_value.sort.return_value.limit.return_value = []
    paginator = Paginate(mongo_collection, 1, 1, "_id", response_wrapper=AsIsWrapper())
    response = paginator.paginate_one_batch()

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )
    assert response == PaginatedResponse(response=[], prev_page=None, next_page=None, batch_size=0)


def test_paginate_one_batch_with_pages(mongo_collection):
    mongo_collection.find.return_value.sort.return_value.limit.return_value = [{"id": 1}, {"id": 2}]
    paginator = Paginate(mongo_collection, 1, 1, "_id", response_wrapper=AsIsWrapper())
    response = paginator.paginate_one_batch()

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )

    assert isinstance(response, PaginatedResponse)
    assert response.response == [{"id": 1}]
    assert response.next_page is not None


def test_paginate(mongo_collection):
    returned_data = [
        {"_id": ObjectId("5ee1e040d3bcce48e169620b"), "id": 1},
    ]

    mongo_collection.find.return_value.sort.return_value.limit.return_value = returned_data
    paginator = Paginate(mongo_collection, 1, 1, "id", automatic_pagination=True, response_wrapper=AsIsWrapper())
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
        {"_id": ObjectId("5ee1e040d3bcce48e169620b"), "id": 1},
    ]

    mongo_collection.find.return_value.sort.return_value.limit.return_value = returned_data
    paginator = Paginate(mongo_collection, 1, 1, "id", automatic_pagination=False, response_wrapper=AsIsWrapper())
    response = paginator.paginate()

    assert isinstance(response, PaginatedResponse)
    assert response.response == [{"_id": ObjectId("5ee1e040d3bcce48e169620b"), "id": 1}]
    assert response.next_page is None

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )


def test_paginate_chat_output(mongo_collection):
    returned_data = [
        {"_id": ObjectId("6079f9f5c5f04b0acecb68e5"), "id": 6},
        {"_id": ObjectId("6079f9f5c5f04b0acecb68e8"), "id": 5},
    ]

    mongo_collection.find.return_value.sort.return_value.limit.return_value = returned_data
    paginator = Paginate(mongo_collection, 2, -1, "id", automatic_pagination=False, response_wrapper=ChatWrapper())
    response = paginator.paginate()

    assert isinstance(response, PaginatedResponse)
    assert response.response == [
        {"_id": ObjectId("6079f9f5c5f04b0acecb68e8"), "id": 5},
        {"_id": ObjectId("6079f9f5c5f04b0acecb68e5"), "id": 6},
    ]
    assert response.next_page is None

    mongo_collection.find.assert_called_once_with(
        {},
        projection={},
    )


def test_paginate_chat_output_wrong_ordering(mongo_collection):

    with pytest.raises(ValueError) as error:
        paginator = Paginate(mongo_collection, 2, 1, "id", automatic_pagination=False, response_wrapper=ChatWrapper())
        _ = paginator.paginate()

    assert str(error.value) == "Display data as chat must be coupled to DESCENDING ordering"
