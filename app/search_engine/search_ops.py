from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from docarray.typing import NdArray
from search_engine.utils import OSMTag, encode, load_model, connect_search_engine, search_engine_client
from docarray import BaseDoc
from pydantic import Field
import pandas as pd
import numpy as np
from docarray.index.backends.elastic import ElasticDocIndex


# depreceated
def search_osm_tag(word, model, search_engine, limit):
    # find similar documents
    # q_embedding = encode(word, model)

    q = (
        search_engine.build_query()
        # .find(q_embedding, search_field='name_embedding', limit=limit)
        .text_search(word, search_field='name', limit=limit)
        .text_search(word, search_field='text', limit=limit)
        # .find(q_embedding, search_field='description_embedding', limit=limit)
        .build()
    )
    docs, scores = search_engine.execute_query(q)

    results = []
    for doc, score in zip(docs, scores):
        results.append(
            {'uri': doc['uri'],
             'osm_tag': doc['osm_tag'],
             'name': doc['name'],
             'description': doc['text'],
             'score': score}
        )

    return results


def construct_bm25_query(query):
    return {"match": {"description": query}}


def construct_knn_query(query_vector):
    return {
        "field": "embeddings",
        "query_vector": query_vector,
        "k": 1,
        "num_candidates": 10
    }


def search_manual_mapping(word, client, model, index_name, confidence=0.79, limit=1):
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
