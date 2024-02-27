import json
from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from tqdm import tqdm

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input_file', required=True)
    parser.add_argument('--output_file', required=True)

    args = parser.parse_args()

    imr_tag_db = args.input_file
    output_file = args.output_file

    with open(imr_tag_db, 'r') as json_file:
        imr_tag_db = list(json_file)

    processed_data = list()
    duplicates = set()
    for imr_tag in tqdm(imr_tag_db, total=len(imr_tag_db)):
        imr_tag = json.loads(imr_tag)
        keyword = imr_tag['keyword'].lower().strip()

        if keyword in processed_data:
            duplicates.add(keyword)
        else:
            processed_data.append(keyword)

    with open(output_file, 'a') as f:
        for duplicate in duplicates:
            f.write(f'{duplicate}\n')
