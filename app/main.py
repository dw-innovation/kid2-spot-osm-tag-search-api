from typing import Dict, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from search_engine.search_ops import search_manual_mapping
from search_engine.utils import search_engine_client, load_model, MANUAL_MAPPING, SEARCH_CONFIDENCE

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load model
MODEL = load_model()

# connect search engine
SEARCH_ENGINE = search_engine_client()


@app.get("/search_osm_tag_v2")
def func_search_in_manual_mapping(word: str, limit: int):
    return search_manual_mapping(word=word,
                                 model=MODEL,
                                 client=SEARCH_ENGINE,
                                 limit=limit,
                                 confidence=SEARCH_CONFIDENCE,
                                 index_name=MANUAL_MAPPING)
