import json
from argparse import ArgumentParser
from loguru import logger
import os
import pandas as pd
from tqdm import tqdm
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from elasticsearch import helpers
from app.search_engine.utils import OSMTag, encode, load_model, connect_search_engine


def read_config(config_path):
    with open(config_path) as f:
        config = json.load(f)
    return config


def index_from_file(fpath, index_name, clear_index, config):
    es = Elasticsearch(
        os.getenv("SEARCH_ENGINE_HOST"),  # Elasticsearch endpoint

    )

    if clear_index:
        es.indices.delete(index=index_name, ignore=[400, 404])
        logger.info(f"Deleted the index {index_name}")

    settings = read_config(config["settings"])
    mappings = read_config(config["mappings"])

    # create index
    es.indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings,
        ignore=[400, 404]
    )

    logger.info(f"Created index {index_name}.")

    logger.info(f"Loading data at {fpath}")

    with open(fpath) as json_file:
        data = json.load(json_file)

    logger.info(f"Data loaded. It has {len(data)} entries.")

    model = load_model()

    logger.info(f"ML model is loaded.")

    actions = []

    logger.info(f"Document indexing started.")
    for idx, row in enumerate(tqdm(data, total=len(data))):
        keywords = row['applies_to'].split('|')
        description = " ".join(keyword.lower() for keyword in keywords)
        action = {"index": {"_index": index_name}}
        doc = {
            "name": keywords[0].lower(),
            "imr": row['imr'],
            "description": description,
            "embeddings": model.encode(description)
        }
        actions.append(action)
        actions.append(doc)
    es.bulk(index=index_name, operations=actions)

    result = es.count(index=index_name)
    logger.info(f"{result.body['count']} tags indexed.")


if __name__ == '__main__':
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
