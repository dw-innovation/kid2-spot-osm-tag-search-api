from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from docarray.typing import NdArray
from search_engine.utils import OSMTag, encode, load_model, connect_search_engine, search_engine_client
from docarray import BaseDoc
from pydantic import Field
import pandas as pd
import numpy as np
from docarray.index.backends.elastic import ElasticDocIndex

def construct_bm25_query(query):
    return {"match": {"name": query}}


def construct_knn_query(query_vector):
    return {
        "field": "embeddings",
        "query_vector": query_vector,
        "k": 10,
        "num_candidates": 100
    }


def search_manual_mapping(word, client, model, index_name, confidence=0.5, limit=1):
    query_vector = model.encode(word)
    resp = client.search(index=index_name,
                         query=construct_bm25_query(query=word),
                         knn=construct_knn_query(query_vector),
                         source=["imr", "name"],
                         request_timeout=30)

    num_docs = resp['hits']['total']['value']
    if num_docs == 0:
        print("No document is matched")
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
