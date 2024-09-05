import json
from argparse import ArgumentParser
from pathlib import Path

import inflect
import pandas as pd
from app.search_engine.utils import search_engine_client, load_model
from loguru import logger
from tqdm import tqdm


def construct_bm25_query(query):
    return {"match": {"name": query}}


def construct_knn_query(query_vector):
    return {
        "field": "embeddings",
        "query_vector": query_vector,
        "k": 10,
        "num_candidates": 100
    }


def search_manual_mapping(word, client, model, index_name, confidence=0.79, limit=1):
    logger.info(f"Querying {word}")

    query_vector = model.encode(word)
    resp = client.search(index=index_name, query=construct_bm25_query(query=word),
                         knn=construct_knn_query(query_vector),
                         source=["imr", "name"],
                         timeout="60s")

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


def one_to_one_match(data):
    err = 0
    for idx, row in enumerate(tqdm(data, total=len(data))):
        row = json.loads(row)
        name = row["key"].lower()
        if len(name) == 0:
            continue

        expected_query = row["imr"]
        result = search_manual_mapping(word=name, model=load_model(), client=es_client, index_name=index_name,
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


def plural_match(data):
    p = inflect.engine()
    err = 0
    for idx, row in enumerate(tqdm(data, total=len(data))):
        row = json.loads(row)
        name = row["key"].lower()
        expected_query = row["imr"]
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
    parser = ArgumentParser()
    parser.add_argument('--index_name', type=str)
    parser.add_argument('--synonyms', type=str)
    parser.add_argument('--validate', type=str, choices=['plural', 'singular'])

    args = parser.parse_args()
    synonyms = args.synonyms

    index_name = args.index_name
    es_client = search_engine_client()
    result = es_client.count(index=index_name)
    logger.info(f"{result.body['count']} tags indexed.")

    model = load_model()

    with open(synonyms, 'r') as json_file:
        data = list(json_file)

    if args.validate == 'singular':
        one_to_one_match(data)
    elif args.validate == 'plural':
        plural_match(data)
    else:
        raise ValueError("Invalid option for validation")
