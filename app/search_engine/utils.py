import os
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from docarray.typing import NdArray
from docarray import BaseDoc
from docarray.index.backends.elastic import ElasticDocIndex
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class OSMTag(BaseDoc):
    text: str
    osm_tag: str
    uri: str
    name: str
    embedding: NdArray[384]


def load_model():
    return SentenceTransformer(
        os.getenv('SENT_TRANSFORMER')
    )


def connect_search_engine():
    return ElasticDocIndex[OSMTag](hosts=os.getenv("SEARCH_ENGINE_HOST"),
                                   index_name="osm_tag")


def encode(text: str, model):
    embedding = model.encode(text)
    return embedding
