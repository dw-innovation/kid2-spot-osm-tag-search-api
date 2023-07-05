import pandas as pd
import requests
import re
from tqdm import tqdm
from argparse import ArgumentParser
from diskcache import Cache

cache = Cache('tmp')
WIKIDATA_DOMAIN = 'http://www.wikidata.org/entity/'
OSM_SEARCH_ENDPOINT = 'https://wiki.openstreetmap.org/w/api.php?action=wbsearchentities&format=json&search=TAG&language=en'
OSM_DATA_ENDPOINT = 'https://wiki.openstreetmap.org/wiki/Special:EntityData/TAG_ID.ttl'
OSM_PREFIX_REGEX = r'^(Tag:|Key:)'


@cache.memoize()
def request_osm_mapping(tag_info):
    osm_endpoint = OSM_SEARCH_ENDPOINT.replace('TAG', tag_info)
    response = requests.get(osm_endpoint)
    response.raise_for_status()

    response_data = response.json()["search"]

    if len(response_data) == 0:
        return None

    else:
        response_data = response_data[0]

    osm_id = response_data["id"]
    osm_title = response_data["title"]
    description = response_data["description"] if 'description' in response_data else None

    return {
        "tag_info": tag_info,
        "osm_id": osm_id,
        "osm_title": osm_title,
        "description": description
    }


@cache.memoize()
def request_osm_data(osm_id):
    osm_data_endpoint = OSM_DATA_ENDPOINT.replace('TAG_ID', osm_id)
    response = requests.get(osm_data_endpoint)
    response.raise_for_status()
    return response.content if response.status_code == 200 else None


def map_to_osm(input_file, output_file):
    wikidata_samples = pd.read_csv(input_file, sep='\t')
    mapped_data = []
    tag_ids = wikidata_samples["tagInfo"].unique()
    for tag_info in tqdm(tag_ids, total=len(tag_ids)):
        tag_info = re.sub(OSM_PREFIX_REGEX, '', tag_info)
        response_data = request_osm_data(tag_info)
        if response_data:
            mapped_data.append(response_data)

    mapped_data = pd.DataFrame(mapped_data)
    mapped_data.to_csv(output_file, sep='\t')


def fetch_from_osm(input_file, output_file):
    mappings = pd.read_csv(input_file, sep='\t')

    osm_ids = mappings["osm_id"].tolist()

    for osm_id in tqdm(osm_ids, total=len(osm_ids)):
        osm_data = request_osm_data(osm_id)

        if not osm_data:
            continue

        with open(f'{output_file}/{osm_id}.ttl', "wb") as file:
            file.write(osm_data)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input_file')
    parser.add_argument('--output_file')
    parser.add_argument('--map', action='store_true')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--create_kg', action='store_true')
    args = parser.parse_args()

    if args.map:
        map_to_osm(input_file=args.input_file,
                   output_file=args.output_file)

    if args.fetch:
        fetch_from_osm(input_file=args.input_file,
                       output_file=args.output_file)

    