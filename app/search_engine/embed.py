from app.kg.search_ops import fetch_all_osm_tags, fetch_description, fetch_osm_tag, fetch_plain_name
from app.kg.utils import load_graph
from app.search_engine.utils import OSMTag, encode, load_model, connect_search_engine
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from docarray.typing import NdArray
from docarray import BaseDoc
from docarray.index.backends.elastic import ElasticDocIndex
from pydantic import Field
import pandas as pd

g = load_graph()

osm_tags = fetch_all_osm_tags(g)

model = load_model()

doc_index = connect_search_engine()
print("Connected to the search engine.")

BATCH = 100
processed_doc = []
for osm_tag in tqdm(osm_tags, total=len(osm_tags)):
    description = fetch_description(g, osm_tag)
    osm_tag_name = fetch_osm_tag(g, osm_tag)
    plain_name = fetch_plain_name(osm_tag_name)

    if not description:
        description = plain_name

    embedding = encode(description, model)

    processed_doc.append(
        OSMTag(uri=osm_tag, text=description, embedding=embedding, osm_tag=osm_tag_name, name=plain_name))

    if len(processed_doc) >= BATCH:
        doc_index.index(processed_doc)
        processed_doc = []

if len(processed_doc) >= 1:
    doc_index.index(processed_doc)

print(f'number of docs in the index: {doc_index.num_docs()}')
