import json
import os
from argparse import ArgumentParser

import pandas as pd
from app.search_engine.utils import OSMTag, encode, load_model, connect_search_engine
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from loguru import logger
from tqdm import tqdm


def read_config(config_path: str) -> dict:
    """
    Load a JSON configuration file.

    Args:
        config_path (str): Path to the JSON config file.

    Returns:
        dict: Parsed JSON configuration as a dictionary.
    """
    with open(config_path) as f:
        config = json.load(f)
    return config


def index_from_file(fpath: str, index_name: str, clear_index: bool, config: dict):
    """
    Indexes documents from a file into an Elasticsearch index.

    Args:
        fpath (str): Path to the input JSONL file (one JSON object per line).
        index_name (str): Name of the Elasticsearch index to use/create.
        clear_index (bool): Whether to delete and recreate the index before indexing.
        config (dict): Configuration dictionary with keys:
                       - 'settings': Path to index settings JSON file.
                       - 'mappings': Path to index mappings JSON file.

    Behavior:
        - Optionally deletes the existing index.
        - Creates a new index with provided settings and mappings.
        - Reads input data from file.
        - Encodes document names using a loaded ML model.
        - Indexes the documents in batches.
    """
    es = Elasticsearch(
        os.getenv("SEARCH_ENGINE_HOST"),  # Elasticsearch endpoint
        request_timeout = 120
    )

    if clear_index:
        es.indices.delete(index=index_name, ignore=[400, 404])
        logger.info(f"Deleted the index {index_name}")

    settings = read_config(config["settings"])
    mappings = read_config(config["mappings"])

    es.indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings,
        ignore=[400, 404]
    )

    logger.info(f"Created index {index_name}.")

    logger.info(f"Loading data at {fpath}")

    with open(fpath, 'r') as json_file:
        data = list(json_file)

    logger.info(f"Data loaded. It has {len(data)} entries.")

    model = load_model()

    logger.info(f"ML model is loaded.")

    actions = []
    batch_size = 500
    logger.info(f"Document indexing started.")
    for row in tqdm(data, total=len(data)):
        row = json.loads(row)
        imr = row['imr']
        name = row['key'].strip().lower()
        cluster_id = row['cluster_id']
        descriptors = row['descriptors']

        action = {"index": {"_index": index_name}}

        doc = {
            "name": name,
            "imr": imr,
            "cluster_id": cluster_id,
            "description": name,
            "embeddings": model.encode(name),
            "descriptors": descriptors
        }
        actions.append(action)
        actions.append(doc)

        if len(actions) == batch_size:
            es.bulk(index=index_name, operations=actions)
            actions.clear()
    if len(actions) > 0:
        es.bulk(index=index_name, operations=actions)
    result = es.count(index=index_name)
    logger.info(f"{result.body['count']} tags indexed.")


if __name__ == '__main__':
    # CLI argument parser for running the script
    parser = ArgumentParser()
    parser.add_argument("--index_manual_mappings", action="store_true")
    parser.add_argument("--index_name", type=str)
    parser.add_argument("--clear_index", action="store_true")
    parser.add_argument("--config_settings", type=str)
    parser.add_argument("--config_mappings", type=str)
    parser.add_argument("--fpath", type=str)

    args = parser.parse_args()

    if args.index_manual_mappings:
        index_from_file(fpath=args.fpath,
                        index_name=args.index_name,
                        clear_index=args.clear_index,
                        config={"settings": args.config_settings,
                                "mappings": args.config_mappings})
