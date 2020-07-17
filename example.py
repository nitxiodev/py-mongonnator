import re

from mongonator import MongoClientWithPagination

if __name__ == '__main__':
    mongo_uri = 'mongodb://local:123adm456@127.0.0.1:27017/admin'
    db = 'adtuo-leads'
    col = 'leads'

    mongo_client = MongoClientWithPagination(mongo_uri)
    db = mongo_client[db]
    col = db[col]

    query = {'campaign_name': {'$ne': None}}
    # query = {'email': re.compile(re.escape('ca'), re.IGNORECASE),
    #          'form_id': re.compile(re.escape('55158'), re.IGNORECASE)}
    # query = {'$or': [{'email': re.compile(re.escape('ca'), re.IGNORECASE)},
    #                  {'form_id': re.compile(re.escape('54'), re.IGNORECASE)}]}
    # query = {'campaign_name': None}
    # query = None

    ordering = 1

    for d in col.paginate(query=query, limit=1, projection={'email': 1, 'form_id': 1, '_id': 0},
                          ordering_field='email', ordering=ordering):
        print(d.response)
        print(d.batch_size)

    for i in col.find(query, projection={'email': 1, 'form_id': 1}).sort('email', 1):
        print(i)
