import os
import pandas as pd
from tqdm import tqdm
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    index_name = "color_mappings"

    client = Elasticsearch(
        os.getenv("SEARCH_ENGINE_HOST"),  # Elasticsearch endpoint

    )

    color_bundles = pd.read_csv('datasets/colour_bundles.csv')
    color_bundles = color_bundles.to_dict(orient='records')

    actions = []
    batch_size = 500
    for color_bundle in color_bundles:
        color_values = list(map(lambda x: x.strip(),color_bundle['Colour Values'].split(',')))
        color_descriptors = list(map(lambda x: x.strip(),color_bundle['Colour Descriptors'].split(',')))

        for color_descriptor in tqdm(color_descriptors, total=len(color_descriptors)):
            print(color_descriptor)
            results = client.search(index=index_name, query={"match": {"name": color_descriptor}},
                                 source=["name", "color_values"],
                                 timeout="60s")

            print(results)

            break