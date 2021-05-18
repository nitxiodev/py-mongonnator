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

# UPDATE - v2.0.0
This readme needs to be updated for the upcoming v2.0.0 because it adds minor changes that may break existing 
deployments.

[comment]: <> (## Options)

[comment]: <> (- `query`: a SON object specifying elements which must be present for a document to be included in the result set. Default is `{}` &#40;query all&#41;.)

[comment]: <> (- `limit`: Number of documents per page. Default is `75`.)

[comment]: <> (- `ordering_case`: Ordering sense when retrieving documents from mongo. Valid options are:)

[comment]: <> (    - `ASCENDING`: Ascending sort order.)

[comment]: <> (    - `DESCENDING`: Descending sort order &#40;**default**&#41;.)

[comment]: <> (- `ordering_field`: Field to order collections. Default is `_id`.)

[comment]: <> (- `projection`:  a dict specifying the fields to include or exclude. Please note that the id cannot be excluded because is mandatory in pagination. Default is `{}` &#40;include only the `_id`&#41;.)

[comment]: <> (- `prev_page`: Previous pagination pointer. When no previous page is available, will be None. Default is `None`.)

[comment]: <> (- `next_page`: Next pagination pointer. When no next page is available, will be None. Default is `None`.)

[comment]: <> (- `automatic_pagination`: If you want to paginate automatically in batches of `limit` over entire collection. Default is `True`.)

[comment]: <> (When options are set, **they should remain unchanged during the whole pagination process** except pagination pointers &#40;prev_page/next_page&#41;.)

[comment]: <> (## Built-in API &#40;recommended&#41;)

[comment]: <> (```python)

[comment]: <> (from mongonator import MongoClientWithPagination, ASCENDING)


[comment]: <> (MONGO_URI = 'mongodb://[user]:[password]@[host]:[port]/admin')

[comment]: <> (DATABASE = 'database')

[comment]: <> (COLLECTION = 'collection')

[comment]: <> (# Instantiate mongo client with pagination)

[comment]: <> (mongo_client = MongoClientWithPagination&#40;MONGO_URI&#41;)

[comment]: <> (db = mongo_client[DATABASE])

[comment]: <> (col = db[COLLECTION])

[comment]: <> (query_filter = {'name': {'$ne': None}})


[comment]: <> (# Paginate automatically in batches of 5)

[comment]: <> (for d in col.paginate&#40;query=query_filter, limit=5, projection={'email': 1, 'name': 1},)

[comment]: <> (                      ordering_field='name', ordering=ASCENDING&#41;:)

[comment]: <> (    print&#40;d.response&#41;)

[comment]: <> (    print&#40;d.batch_size&#41;)


[comment]: <> (# Paginate manually in batches of 5)

[comment]: <> (page = col.paginate&#40;query=query_filter, limit=5, projection={'email': 1, 'name': 1},)

[comment]: <> (                      ordering_field='name', ordering=ASCENDING, automatic_pagination=False&#41;)


[comment]: <> (# ahead &#40;next five documents&#41;)

[comment]: <> (next_batch_of_five = col.paginate&#40;query=query_filter, limit=5, projection={'email': 1, 'name': 1},)

[comment]: <> (                      ordering_field='name', ordering=ASCENDING, automatic_pagination=False, next_page=page.next_page&#41;)

               
[comment]: <> (# back &#40;prev five documents from next_batch_of_five situation&#41;)

[comment]: <> (prev_batch_of_five = col.paginate&#40;query=query_filter, limit=5, projection={'email': 1, 'name': 1},)

[comment]: <> (                      ordering_field='name', ordering=ASCENDING, automatic_pagination=False, next_page=next_batch_of_five.prev_page&#41;)

[comment]: <> (```)

[comment]: <> (This method is intended when you just started a new project from scratch or for existing projects if you are willing to substitute every `MongoClient` instance for `MongoClientWithPagination`.)

[comment]: <> (## Explicit API)

[comment]: <> (```python)

[comment]: <> (from mongonator import Paginate, ASCENDING)

[comment]: <> (from pymongo import MongoClient)


[comment]: <> (MONGO_URI = 'mongodb://[user]:[password]@[host]:[port]/admin')

[comment]: <> (DATABASE = 'database')

[comment]: <> (COLLECTION = 'collection')

[comment]: <> (query_filter = {'name': {'$ne': None}})

[comment]: <> (# Instantiate MongoClient from pymongo)

[comment]: <> (with MongoClient&#40;MONGO_URI&#41; as mongo_client:)

[comment]: <> (    db = mongo_client[DATABASE])

[comment]: <> (    col = db[COLLECTION])

[comment]: <> (    # Manual pagination in batches of 2)

[comment]: <> (    paginator = Paginate&#40;)

[comment]: <> (        collection=col,)

[comment]: <> (        query=query_filter,)

[comment]: <> (        limit=2,)

[comment]: <> (        ordering_field='email',)

[comment]: <> (        ordering_case=ASCENDING,)

[comment]: <> (        projection={'email': 1, 'name': 1},)

[comment]: <> (        automatic_pagination=False)

[comment]: <> (    &#41;.paginate&#40;&#41;)

[comment]: <> (    # Print results)

[comment]: <> (    print&#40;"Response: ", paginator.response&#41;)

[comment]: <> (    print&#40;"Prev page: ", paginator.prev_page&#41;)

[comment]: <> (    print&#40;"Next page: ", paginator.next_page&#41;)

[comment]: <> (    print&#40;"Batch size: ", paginator.batch_size&#41;)

[comment]: <> (    # Manual pagination for two next results...)

[comment]: <> (    paginator = Paginate&#40;)

[comment]: <> (        collection=col,)

[comment]: <> (        query=query_filter,)

[comment]: <> (        limit=2,)

[comment]: <> (        ordering_field='email',)

[comment]: <> (        ordering_case=ASCENDING,)

[comment]: <> (        projection={'email': 1, 'name': 1},)

[comment]: <> (        automatic_pagination=False,)

[comment]: <> (        next_page=paginator.next_page,)

[comment]: <> (    &#41;.paginate&#40;&#41;)

[comment]: <> (    # Print results)

[comment]: <> (    print&#40;"Response: ", paginator.response&#41;)

[comment]: <> (    print&#40;"Prev page: ", paginator.prev_page&#41;)

[comment]: <> (    print&#40;"Next page: ", paginator.next_page&#41;)

[comment]: <> (    print&#40;"Batch size: ", paginator.batch_size&#41;)
    
[comment]: <> (    # ... Or simply use automatic pagination in batches of 2 &#40;starting in first document&#41;)

[comment]: <> (    for d in Paginate&#40;)

[comment]: <> (        collection=col,)

[comment]: <> (        query=query_filter,)

[comment]: <> (        limit=2,)

[comment]: <> (        ordering_field='email',)

[comment]: <> (        ordering_case=ASCENDING,)

[comment]: <> (        projection={'email': 1, 'name': 1},)

[comment]: <> (        automatic_pagination=True,)

[comment]: <> (    &#41;.paginate&#40;&#41;:)

[comment]: <> (        print&#40;d.response&#41;)

[comment]: <> (```)

[comment]: <> (This method is intended when you have a big project in production and is not possible to substitute every [MongoClient]&#40;https://api.mongodb.com/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient&#41; call. )
