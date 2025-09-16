import os
from dotenv import load_dotenv
from tqdm import tqdm
from loguru import logger
from elasticsearch import Elasticsearch
import pandas as pd

load_dotenv()

if __name__ == '__main__':
    # Name of the Elasticsearch index to create/populate
    index_name = 'color_mappings'

    es = Elasticsearch(
        os.getenv("SEARCH_ENGINE_HOST"),  # Elasticsearch endpoint
        request_timeout = 120
    )

    # Define the index mapping (structure of stored documents)
    index_body = {
        "mappings": {
            "properties": {
                "name": {
                    "type": "keyword"  # Keyword type for exact matches
                }
            }
        }
    }

    es.indices.create(
        index=index_name,
        body=index_body,
        ignore=[400, 404]
    )

    color_bundles = pd.read_csv('datasets/colour_bundles.csv')
    color_bundles = color_bundles.to_dict(orient='records')

    actions = []
    batch_size = 500
    for color_bundle in color_bundles:
        color_values = list(map(lambda x: x.strip(),color_bundle['Colour Values'].split(',')))
        color_descriptors = list(map(lambda x: x.strip(),color_bundle['Colour Descriptors'].split(',')))

        for color_descriptor in tqdm(color_descriptors, total=len(color_descriptors)):
            doc = {
                "name": color_descriptor,
                "color_values": color_values,
            }

            action = {"index": {"_index": index_name}}
            actions.append(action)
            actions.append(doc)

            if len(actions) == batch_size:
                es.bulk(index=index_name, operations=actions)
                actions.clear()

    if len(actions) > 0:
        es.bulk(index=index_name, operations=actions)

    result = es.count(index=index_name)
    logger.info(f"{result.body['count']} tags indexed.")