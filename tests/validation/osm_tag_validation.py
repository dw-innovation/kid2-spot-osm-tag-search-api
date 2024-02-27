import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
from tqdm import tqdm
from tqdm import tqdm

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input_file', required=True)

    args = parser.parse_args()

    imr_tag_db = args.input_file

    with open(imr_tag_db, 'r') as json_file:
        imr_tag_db = list(json_file)

    unique_osm_tags = set()
    for imr_tag in tqdm(imr_tag_db, total=len(imr_tag_db)):
        imr_tag = json.loads(imr_tag)
        keyword = imr_tag['keyword'].lower().strip()

        for osm_tag_comb in imr_tag['imr']:
            if isinstance(osm_tag_comb, dict):
                for osm_tags in osm_tag_comb.values():
                    for osm_tag in osm_tags:
                        if 'value' not in osm_tag:
                            if 'and' in osm_tag:
                                osm_tag_bundles = osm_tag['and']
                                for _osm_tag in osm_tag_bundles:
                                    if len(_osm_tag['value'].split(' ')) >= 2:
                                        print('might have misspells')
                                        print("keyword")
                                        print(keyword)
                                        print("osm tags")
                                        print(osm_tags)
                            continue
                        if len(osm_tag['value'].split(' ')) >= 2:
                            print('might have misspells')
                            print("keyword")
                            print(keyword)
                            print("osm tags")
                            print(osm_tags)
                            continue
                        else:
                            continue