import pandas as pd
from app.search_engine.utils import search_engine_client, load_model
from pathlib import Path
from loguru import logger


def construct_bm25_query(query):
    return {"match": {"description": query}}


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
    resp = client.search(index=index_name, query=construct_bm25_query(query=word), knn=construct_knn_query(query_vector),
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


if __name__ == '__main__':
    queries = ["public toilet", "public toilets", "kremlin", "stupid", "book store", "books store", "tower",
               "cable way",
               "heliport", "helicopter", "forest",
               "public restroom", "cinema", "movie theater", "public restrooms", "coffee shop", "tree", "trees",
               "skyscraper", "restaurant", "theater"]
    index_name = "manual_mapping"
    es_client = search_engine_client()
    result = es_client.count(index=index_name)
    logger.info(f"{result.body['count']} tags indexed.")

    model = load_model()

    for query in queries:
        result = search_manual_mapping(word=query, model=load_model(), client=es_client, index_name=index_name, limit=3)
        print(result)