import pandas as pd
import json
import inflect
from app.search_engine.utils import search_engine_client, load_model
from pathlib import Path
from loguru import logger
from tqdm import tqdm


def construct_bm25_query(query):
    return {"match": {"name": query}}


def construct_knn_query(query_vector):
    return {
        "field": "embeddings",
        "query_vector": query_vector,
        "k": 2,
        "num_candidates": 10
    }


def search_manual_mapping(word, client, model, index_name, confidence=0.79, limit=1):
    logger.info(f"Querying {word}")

    query_vector = model.encode(word)
    resp = client.search(index=index_name, query=construct_bm25_query(query=word),
                         knn=construct_knn_query(query_vector),
                         source=["imr", "name"])

    num_docs = resp['hits']['total']['value']

    if num_docs == 0:
        logger.info("No document is matched")
        return []

    else:
        results = resp['hits']['hits'][:limit]

        search_results = []

        for result in results:
            if result['_score'] < confidence:
                continue

            search_results.append({
                'imr': result['_source']['imr'],
                "name": result['_source']['name'],
                "score": result['_score'],
            })

        return search_results


index_name = "manual_mapping_v2"
es_client = search_engine_client()
result = es_client.count(index=index_name)
logger.info(f"{result.body['count']} tags indexed.")

model = load_model()


def one_to_one_match(data):
    err = 0
    for idx, key_value in enumerate(tqdm(data, total=len(data))):
        name = key_value.lower()
        result = search_manual_mapping(word=name, model=load_model(), client=es_client, index_name=index_name,
                                           limit=1)
        expected_query = data[key_value]
        if len(result) == 0:
            print(f"No match is found for {keyword}")
            err += 1
            continue

        if expected_query != result[0]["imr"]:
            print(f"the mismatch for {name}")
            print("===expected===")
            print(expected_query)
            print("===real===")
            print(result)
            err += 1
            continue
    print(f"Number of mismatch is {err}")


def test_plural_search(data):
    p = inflect.engine()
    err = 0
    for idx, key_value in enumerate(tqdm(data, total=len(data))):
        name = key_value.lower()
        expected_query = data[key_value]
        keyword = p.plural_noun(name)

        result = search_manual_mapping(word=keyword, model=load_model(), client=es_client, index_name=index_name,
                                       limit=1)
        if len(result) == 0:
            print(f"No match is found for {keyword}")
            err += 1
            continue

        if expected_query != result[0]["imr"]:
            print(f"the mismatch for {name}")
            print("===expected===")
            print(expected_query)
            print("===real===")
            print(result)
            err += 1
            continue
    print(f"Number of mismatch is {err}")


if __name__ == '__main__':
    synonyms = "tests/search_data/imr-tag-db_v1.json"

    with open(synonyms) as f:
        data = json.load(f)

    # one_to_one_match(data)
    test_plural_search(data)
