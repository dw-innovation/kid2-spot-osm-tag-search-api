import os
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from docarray.typing import NdArray
from docarray import BaseDoc
from docarray.index.backends.elastic import ElasticDocIndex
from pydantic import Field
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

MANUAL_MAPPING = os.getenv('MANUAL_MAPPING')
SEARCH_CONFIDENCE = float(os.getenv('SEARCH_CONFIDENCE'))

class OSMTag(BaseDoc):
    text: str
    osm_tag: str
    uri: str
    name: str
    name_embedding: NdArray[384]
    description_embedding: NdArray[384]


def load_model():
    return SentenceTransformer(
        os.getenv('SENT_TRANSFORMER')
    )


def connect_search_engine():
    return ElasticDocIndex[OSMTag](hosts=os.getenv("SEARCH_ENGINE_HOST"),
                                   index_name=os.getenv("SEARCH_ENGINE_INDEX"))


def search_engine_client():
    return Elasticsearch(
        os.getenv("SEARCH_ENGINE_HOST"),  # Elasticsearch endpoint

    )


def encode(text: str, model):
    embedding = model.encode(text)
    return embedding
