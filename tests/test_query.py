from unittest.mock import patch

import pytest
from bson import ObjectId

from mongonator import DEFAULT_ORDERING_FIELD, ASCENDING
from mongonator.query import Query


@pytest.fixture
def default_query():
    yield Query(None, None, None, ASCENDING, DEFAULT_ORDERING_FIELD)


@pytest.fixture
def custom_query():
    yield Query(None, None, None, ASCENDING, 'custom_field')


def test_build_sortable_filter_with_default_field(default_query):
    default_query._build_sortable_filter(ASCENDING)
    assert default_query._sortable_filter == [
        ('_id', ASCENDING)
    ]


def test_build_sortable_filter_with_custom_field(custom_query):
    custom_query._build_sortable_filter(ASCENDING)
    assert custom_query._sortable_filter == [
        ('custom_field', ASCENDING),
        ('_id', ASCENDING)
    ]


def test_build_mongo_filter_with_default_field(default_query):
    default_query._build_mongo_filter('custom_field', '5ee7cb5dfce77c2d2b9d84f4', 'mongo_key')
    assert default_query._mongo_filter == {
        '_id': {
            'mongo_key': ObjectId('5ee7cb5dfce77c2d2b9d84f4')
        }
    }


def test_build_mongo_filter_with_custom_field(custom_query):
    custom_query._build_mongo_filter('custom_field', '5ee7cb5dfce77c2d2b9d84f4', 'mongo_key')
    assert custom_query._mongo_filter == {'$or': [{'custom_field': {'mongo_key': 'custom_field'}},
                                                  {'custom_field': 'custom_field',
                                                   '_id': {'mongo_key': ObjectId('5ee7cb5dfce77c2d2b9d84f4')}}]}


def test_build_mongo_filter_with_custom_field_with_or(custom_query):
    custom_query._mongo_filter.update(**{'$or': {'email': 'fake@email.com'}})
    custom_query._build_mongo_filter('custom_field', '5ee7cb5dfce77c2d2b9d84f4', 'mongo_key')
    assert custom_query._mongo_filter == {'$and': [{'$or': [{'custom_field': {'mongo_key': 'custom_field'}},
                                                            {'custom_field': 'custom_field', '_id': {
                                                                'mongo_key': ObjectId('5ee7cb5dfce77c2d2b9d84f4')}}]},
                                                   {'$or': {'email': 'fake@email.com'}}]}


@pytest.mark.parametrize('query, prev_page, next_page, ordering_case, field, result', [
    (None, None, None, ASCENDING, DEFAULT_ORDERING_FIELD, (
            ASCENDING,
    ))
])
def test_build_query(query, prev_page, next_page, ordering_case, field, result):
    with patch('mongonator.query.Query._build_sortable_filter') as mock_filter:
        query = Query(query, prev_page, next_page, ordering_case, field)
        query.build_query()
        mock_filter.assert_called_once_with(*result)


@pytest.mark.parametrize('query, prev_page, next_page, ordering_case, field, result', [
    (None, 'prev_page', None, ASCENDING, DEFAULT_ORDERING_FIELD, (
            'prev_page', False
    )),
    (None, None, 'next_page', ASCENDING, DEFAULT_ORDERING_FIELD, (
            'next_page', True
    ))
])
def test_build_query(query, prev_page, next_page, ordering_case, field, result):
    with patch('mongonator.query.Query._build_internal_structures') as mock_structures:
        query = Query(query, prev_page, next_page, ordering_case, field)
        query.build_query()
        mock_structures.assert_called_once_with(*result)
