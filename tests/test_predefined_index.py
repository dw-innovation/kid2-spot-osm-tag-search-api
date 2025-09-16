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


def create_index(es: Elasticsearch, index_name: str, model) -> None:
    """
    Create and populate a temporary Elasticsearch index for synonym/OSM-tag tests.

    Args:
        es (Elasticsearch): Connected Elasticsearch client.
        index_name (str): Name of the index to create.
        model: Embedding model with an `.encode(text)` method that returns a vector.

    Side Effects:
        - Creates (or overwrites) an index with custom analysis (synonyms, snowball, etc.).
        - Bulk indexes documents derived from `tests/search_data/synonym_json_v3.json`.

    Notes:
        - Documents are stored with fields:
            * name (text, analyzed)
            * imr (opaque identifier/value from the JSON)
            * description (joined keywords used as the text to embed)
            * embeddings (dense_vector encoded from description)
        - This function performs a one-shot bulk index for all documents in the JSON file.
    """
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

    # Create the index with custom analysis & vector mapping.
    es.indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings
    )

    # Load fixture data used to create test documents.
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

# standard text query
def text_query(query: str) -> Dict:
    """
    Build a standard BM25 match query on the `name` field.

    Args:
        query (str): User query string.

    Returns:
        dict: Elasticsearch `match` query targeting the `name` field.
    """
    return {"match": {"name": query}}

def text_multiple_query(query: str) -> Dict:
    """
    Build a BM25 query that matches against both `name` and `description`.

    Args:
        query (str): User query string.

    Returns:
        dict: Elasticsearch `bool` query with `should` clauses for `name` and `description`.
    """
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

def hybrid_search_query(query: str, model) -> Dict:
    """
    Build a (unused here) hybrid-style payload with kNN on an embedding field.

    Args:
        query (str): User query string to embed.
        model: Embedding model with `.encode`.

    Returns:
        dict: An example request body with a kNN block and _source selection.

    Note:
        The mapping in this script defines the vector field as `embeddings`.
        If you use this helper, ensure the `field` matches that mapping.
    """
    return {
        "knn": {
            "field": "description_embedding",
            "query_vector": model.encode(query),
            "k": 5,
            "num_candidates": 1
        },
        "_source": ["description"]
    }



# ---- Index creation and quick search trials (script mode) ----


create_index(es, index_name, model)
# print(f"Created the index {index_name}")
result = es.count(index=index_name)
print(f"NUmber of documents {result.body['count']}")

queries = ["public toilet", "public toilets", "kremlin", "stupid", "book store", "books store", "tower", "cable way",
           "heliport", "helicopter", "forest",
           "public restroom", "cinema", "movie theater", "public restrooms", "coffee shop", "tree", "trees"]

search_types = {
    'standard': text_query
}


# Quick demo loop: BM25 + kNN (hybrid) search against the temporary index.
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

    # Perform a hybrid search: lexical BM25 + vector kNN.
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

# Clean up the temporary index after trials.
es.indices.delete(index=index_name)
print(f"Deleted the index {index_name}")
