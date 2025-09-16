from typing import Dict, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from search_engine.search_ops import search_manual_mapping, search_color_mapping
from search_engine.utils import search_engine_client, load_model, MANUAL_MAPPING, SEARCH_CONFIDENCE, COLOR_MAPPING

# Initialize FastAPI app
app = FastAPI()

# Allow all origins for CORS
origins = ["*"]

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load a machine learning model used for search scoring or embedding
MODEL = load_model()

# Connect to the search engine client (e.g., Elasticsearch)
SEARCH_ENGINE = search_engine_client()

@app.get("/search_osm_tag_v2")
def func_search_in_manual_mapping(word: str, limit: int):
    """
    Search for OSM (OpenStreetMap) tags using a manually defined mapping index.

    Args:
        word (str): The search keyword to look up in the manual mapping.
        limit (int): Maximum number of results to return.

    Returns:
        List[Dict]: A list of matched results with scores and tags.

    Description:
        This endpoint uses a custom search engine and preloaded model to perform
        a semantic search over a manually curated OSM tag index. The results are
        filtered by confidence threshold and limited by the `limit` parameter.
    """
    return search_manual_mapping(word=word,
                                 model=MODEL,
                                 client=SEARCH_ENGINE,
                                 limit=limit,
                                 confidence=SEARCH_CONFIDENCE,
                                 index_name=MANUAL_MAPPING)

@app.get("/color_mapping")
def func_color_mapping(color: str):
    """
    Search for a tag mapping related to a given color.

    Args:
        color (str): The color to search for in the color mapping index.

    Returns:
        Dict or List[Dict]: The most relevant result associated with the given color.

    Description:
        This endpoint queries the color mapping index to find semantic matches
        for the provided color string. It returns the top result (limit = 1).
    """
    return search_color_mapping(word=color,
                                client=SEARCH_ENGINE,
                                index_name=COLOR_MAPPING,
                                limit=1)