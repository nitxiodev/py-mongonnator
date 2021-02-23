# PyMongonnator ![Build](https://github.com/nitxiodev/py-mongonnator/workflows/Build/badge.svg?branch=master)
Just a simple production-ready mongo paginator written in Python for [PyMongo](https://github.com/mongodb/mongo-python-driver) package using bucket pattern. This package is based in this wonderful `Javascript` module: [mongo-cursor-pagination](https://www.npmjs.com/package/mongo-cursor-pagination).
The reason for making this library was to paginate over thousands of data stored in mongo collections and we didn't find any library that seamlessly integrated with Pymongo. 

# Installation 
```bash
pip install PyMongonnator
```
### Python version compat
`PyMongonnator` is compatible with the latest Python3 versions: `3`, `3.5`, `3.6`, `3.7`, `3.8`. 

# Usage

`PyMongonnator` exposes two ways to paginate over collections:

- Built-in API importing overriden MongoClient class.
- Explicit API passing a MongoClient collection into Paginator method.

## Options

- `query`: a SON object specifying elements which must be present for a document to be included in the result set. Default is `{}` (query all).
- `limit`: Number of documents per page. Default is `75`.
- `ordering_case`: Ordering sense when retrieving documents from mongo. Valid options are:
    - `ASCENDING`: Ascending sort order.
    - `DESCENDING`: Descending sort order (**default**).
- `ordering_field`: Field to order collections. Default is `_id`.
- `projection`:  a dict specifying the fields to include or exclude. Please note that the id cannot be excluded because is mandatory in pagination. Default is `{}` (include only the `_id`).
- `prev_page`: Previous pagination pointer. When no previous page is available, will be None. Default is `None`.
- `next_page`: Next pagination pointer. When no next page is available, will be None. Default is `None`.
- `automatic_pagination`: If you want to paginate automatically in batches of `limit` over entire collection. Default is `True`.

When options are set, **they should remain unchanged during the whole pagination process** except pagination pointers (prev_page/next_page).

## Built-in API (recommended)
```python
from mongonator import MongoClientWithPagination, ASCENDING


MONGO_URI = 'mongodb://[user]:[password]@[host]:[port]/admin'
DATABASE = 'database'
COLLECTION = 'collection'

# Instantiate mongo client with pagination
mongo_client = MongoClientWithPagination(MONGO_URI)
db = mongo_client[DATABASE]
col = db[COLLECTION]

query_filter = {'name': {'$ne': None}}


# Paginate automatically in batches of 5
for d in col.paginate(query=query_filter, limit=5, projection={'email': 1, 'name': 1},
                      ordering_field='name', ordering=ASCENDING):
    print(d.response)
    print(d.batch_size)


# Paginate manually in batches of 5
page = col.paginate(query=query_filter, limit=5, projection={'email': 1, 'name': 1},
                      ordering_field='name', ordering=ASCENDING, automatic_pagination=False)


# ahead (next five documents)
next_batch_of_five = col.paginate(query=query_filter, limit=5, projection={'email': 1, 'name': 1},
                      ordering_field='name', ordering=ASCENDING, automatic_pagination=False, next_page=page.next_page)

               
# back (prev five documents from next_batch_of_five situation)
prev_batch_of_five = col.paginate(query=query_filter, limit=5, projection={'email': 1, 'name': 1},
                      ordering_field='name', ordering=ASCENDING, automatic_pagination=False, next_page=next_batch_of_five.prev_page)
```

This method is intended when you just started a new project from scratch or for existing projects if you are willing to substitute every `MongoClient` instance for `MongoClientWithPagination`.

## Explicit API
```python
from mongonator import Paginate, ASCENDING
from pymongo import MongoClient


MONGO_URI = 'mongodb://[user]:[password]@[host]:[port]/admin'
DATABASE = 'database'
COLLECTION = 'collection'

query_filter = {'name': {'$ne': None}}

# Instantiate MongoClient from pymongo
with MongoClient(MONGO_URI) as mongo_client:
    db = mongo_client[DATABASE]
    col = db[COLLECTION]

    # Manual pagination in batches of 2
    paginator = Paginate(
        collection=col,
        query=query_filter,
        limit=2,
        ordering_field='email',
        ordering_case=ASCENDING,
        projection={'email': 1, 'name': 1},
        automatic_pagination=False
    ).paginate()

    # Print results
    print("Response: ", paginator.response)
    print("Prev page: ", paginator.prev_page)
    print("Next page: ", paginator.next_page)
    print("Batch size: ", paginator.batch_size)

    # Manual pagination for two next results...
    paginator = Paginate(
        collection=col,
        query=query_filter,
        limit=2,
        ordering_field='email',
        ordering_case=ASCENDING,
        projection={'email': 1, 'name': 1},
        automatic_pagination=False,
        next_page=paginator.next_page,
    ).paginate()

    # Print results
    print("Response: ", paginator.response)
    print("Prev page: ", paginator.prev_page)
    print("Next page: ", paginator.next_page)
    print("Batch size: ", paginator.batch_size)
    
    # ... Or simply use automatic pagination in batches of 2 (starting in first document)
    for d in Paginate(
        collection=col,
        query=query_filter,
        limit=2,
        ordering_field='email',
        ordering_case=ASCENDING,
        projection={'email': 1, 'name': 1},
        automatic_pagination=True,
    ).paginate():
        print(d.response)
```

This method is intended when you have a big project in production and is not possible to substitute every [MongoClient](https://api.mongodb.com/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient) call. 
