from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from search_engine.utils import search_engine_client, load_model, MANUAL_MAPPING
from kg.utils import load_graph
from kg.search_ops import fetch_tag_properties, fetch_all_osm_tags, fetch_all_categories, fetch_tags_per_category
from search_engine.search_ops import search_osm_tag, search_manual_mapping

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

# connect to the graph
GRAPH = load_graph()


@app.get("/search_osm_tag")
def func_search_osm_tag(word: str, limit: int, detail: bool):
    if detail:
        results = search_osm_tag(word, model=MODEL, search_engine=SEARCH_ENGINE, limit=limit)
        return list(map(lambda result: fetch_tag_properties(result['uri'], GRAPH), results))
    else:
        return search_osm_tag(word, model=MODEL, search_engine=SEARCH_ENGINE, limit=limit)


@app.get("/search_osm_tag_v2")
def func_search_in_manual_mapping(word: str, limit: int):
    return search_manual_mapping(word=word, model=MODEL, client=SEARCH_ENGINE, limit=limit, index_name=MANUAL_MAPPING)


@app.get("/fetch_all_osm_tags")
def func_fetch_all_osm_tags():
    return fetch_all_osm_tags(GRAPH)


@app.get("/fetch_all_categories")
def func_fetch_all_categories():
    return fetch_all_categories(GRAPH)


@app.get("/fetch_tags_per_category")
def func_fetch_tags_per_category(category):
    return fetch_tags_per_category(category, GRAPH)


@app.get("/fetch_tag_properties")
def func_fetch_tag_properties(osm_tag):
    return fetch_tag_properties(osm_tag, GRAPH)
