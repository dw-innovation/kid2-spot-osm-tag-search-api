from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from docarray.typing import NdArray
from app.search_engine.utils import OSMTag, encode, load_model, connect_search_engine
from docarray import BaseDoc
from docarray.index.backends.weaviate import WeaviateDocumentIndex
from pydantic import Field
import pandas as pd
import numpy as np
from docarray.index.backends.elastic import ElasticDocIndex


def search_osm_tag(word, model, search_engine, limit):
    # find similar documents
    q_embedding = encode(word, model)

    q = (
        search_engine.build_query()
        .find(q_embedding, search_field='embedding', limit=limit)
        .text_search(word, search_field='name')
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
