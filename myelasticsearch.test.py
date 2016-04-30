# IPython log file

from elasticsearch import Elasticsearch

index = 'test'
content1 = {
    'test': 'There is <i>some</i> <b>HTML</b>',
    'hello': 'World'
}
content2 = {
    'test': 'There is <a href="">some other</a> <b>HTML</b>',
    'hello': 'World2'
}

es = Elasticsearch(host='el')
es.info()
es.indices.create(index=index)
es.indices.stats()

es.index(index=index, id=1, body=content1, doc_type='some')
es.index(index=index, id=2, body=content2, doc_type='some')

es.get(index=index, doc_type='some', 1)

# get all
es.search(index=index)

# query all fields, lowercase, no html
es.search(index=index, body={"query": {"match": {"test": "some"}}})
es.search(index=index, body={"query": {"match": {"test": "some HTML"}}})

# Update existing
es.update(index=index,
          id=1, body={"doc": {'hello': 'no world'}}, doc_type='some')
es.search(index=index)

# Add a new field
es.update(index=index, id=1, body={"doc": {'trans': 'test'}}, doc_type='some')
es.search(index=index)

# Limit output
es.search(index=index, size=1)

# More tests
from elasticsearch import Elasticsearch
es = Elasticsearch(host='el')
es.search(index='autocomplete', body={'query': {"match": {"_all": {"query": "agen _1"}}}}, sort=["extrait:asc"])
