import json
import os
import pandas as pd
from tqdm import tqdm
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from elasticsearch import helpers
from app.search_engine.utils import OSMTag, encode, load_model, connect_search_engine

load_dotenv()

index_name = "test_predefined_table_2"

es = Elasticsearch(
    os.getenv("SEARCH_ENGINE_HOST"),  # Elasticsearch endpoint

)
# es.indices.delete(index=index_name, ignore=[400, 404])
# print(f"Deleted the index {index_name}")


model = load_model()


def create_index(es, index_name, model):
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
            },
            'embeddings': {
                'type': 'dense_vector',
                'dims': 768,
                'index': 'true',
                'similarity': 'cosine'
            }
        }
    }
    # create index
    es.indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings
    )

    with open('tests/search_data/synonym_json_v3.json') as json_file:
        json_data = json.load(json_file)

    # descriptions = pd.read_csv("tests/search_data/Tag_List_v8.csv", sep=",")['description'].tolist()
    actions = []
    for idx, data in enumerate(tqdm(json_data, total=len(json_data))):
        keywords = data['applies_to'].split('|')
        description = " ".join(keyword.lower() for keyword in keywords)
        # description_embedding = encode(description, model)

        # for keyword in keywords:
        #     action = {"index": {"_index": index_name}}
        #     doc = {
        #         "name": keyword.lower(),
        #         "imr": data['imr'],
        #         "description": description,
        #         "embeddings": model.encode(description)
        #     }
        #     actions.append(action)
        #     actions.append(doc)

        action = {"index": {"_index": index_name}}
        doc = {
            "name": keywords[0].lower(),
            "imr": data['imr'],
            "description": description,
            "embeddings": model.encode(description)
        }
        actions.append(action)
        actions.append(doc)
    es.bulk(index=index_name, operations=actions)

    # connection to search engine


create_index(es, index_name, model)
# print(f"Created the index {index_name}")
result = es.count(index=index_name)
print(f"NUmber of documents {result.body['count']}")

queries = ["public toilet", "public toilets", "kremlin", "stupid", "book store", "books store", "tower", "cable way",
           "heliport", "helicopter", "forest",
           "public restroom", "cinema", "movie theater", "public restrooms", "coffee shop", "tree", "trees"]


## query options
# standard text query
def text_query(query):
    return {"match": {"name": query}}


def text_multiple_query(query):
    return {"bool": {
        "should": [
            {
                "match": {
                    "name": query
                }
            },
            {
                "match": {
                    "description": query
                }
            }
        ]
    }}


# vector search query


def hybrid_search_query(query, model):
    return {
        "knn": {
            "field": "description_embedding",
            "query_vector": model.encode(query),
            "k": 5,
            "num_candidates": 1
        },
        "_source": ["description"]
    }


search_types = {
    'standard': text_query
}

for query in queries:
    print(f"Query {query}")

    bm25_query = {"match": {"name": query}}

    query_vector = model.encode(query)
    knn_query = {
        "field": "embeddings",
        "query_vector": query_vector,
        "k": 1,
        "num_candidates": 10
    }

    # resp = es.search(index=index_name, query=text_query(query))
    resp = es.search(index=index_name, query=bm25_query, knn=knn_query, source=["imr", "name"])

    num_docs = resp['hits']['total']['value']

    if num_docs == 0:
        print("No document is returned.")

    else:
        if resp['hits']['hits'][0]['_score'] < 0.79:
            print("Document is below thershold")
            continue
        print("Matched Document")
        print("OSM")
        print(resp['hits']['hits'][0]['_source']['imr'])
        print("name")
        print(resp['hits']['hits'][0]['_source']['name'])
        print("score")
        print(resp['hits']['hits'][0]['_score'])

# delete index
es.indices.delete(index=index_name)
print(f"Deleted the index {index_name}")
