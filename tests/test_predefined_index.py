import json
import os
import pandas as pd
from tqdm import tqdm
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from elasticsearch import helpers

load_dotenv()

index_name = "test_predefined_table"

settings = {
    'analysis': {
        'analyzer': {
            'name_search': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': [
                    'lowercase',
                    'synonym',
                    'asciifolding',
                    'snowball',
                    'word_delimiter_graph'
                ],
            },
        },
        'filter': {
            'synonym': {
                'type': 'synonym',
                'lenient': True,
                'synonyms': [
                    'toilet, restroom',
                    'cinema, movie theater'
                ]
            }
        }
    }
}

mappings = {
    'properties': {
        'name': {
            'type': 'text',
            'analyzer': 'name_search'
        }
    }
}

# connection to search engine
es = Elasticsearch(
    os.getenv("SEARCH_ENGINE_HOST"),  # Elasticsearch endpoint
)

print("Connected to the search engine")

# create index
es.indices.create(
    index=index_name,
    settings=settings,
    mappings=mappings,
    ignore=400
)

print(f"Created the index {index_name}")

print(es.info())

# Indexing documents

with open('tests/search_data/synonym_json_test_v2.json') as json_file:
    json_data = json.load(json_file)

descriptions = pd.read_csv("tests/search_data/Tag_List_v8.csv", sep=",")['description'].tolist()

for idx, data in enumerate(tqdm(json_data, total=len(json_data))):
    keywords = data['applies_to'].split('|')

    for keyword in keywords:

        # find description for the keyword
        description = keyword
        for sent in descriptions:
            if keyword in sent:
                description = sent
                continue

        resp = es.index(index=index_name, id=idx, document={
            "name": keyword,
            "imr": data['imr'],
            "description": description
        })


queries = ["public toilet", "public toilets", "kremlin", "stupid", "book store", "books store", "tower", "cable way",
           "heliport", "helicopter", "forest",
           "public restroom", "cinema", "movie theater", "public restrooms"]

for query in queries:
    print(f"Query {query}")
    resp = es.search(index=index_name, query={"match": {"name": query}})

    num_docs = resp['hits']['total']['value']

    if num_docs == 0:
        print("No document is returned.")

    else:
        print("Matched Document")
        print("OSM")
        print(resp['hits']['hits'][0]['_source']['imr'])
        print("name")
        print(resp['hits']['hits'][0]['_source']['name'])

# delete index
es.indices.delete(index=index_name)
print(f"Deleted the index {index_name}")
