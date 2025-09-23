<img width="1280" height="200" alt="Github-Banner_spot" src="https://github.com/user-attachments/assets/f65c5d8e-0260-46a4-b0cc-6ebe5c35deff" />

# OSM Tag Search

The repository contains the source code of the steps for the tag search engine.

## Virtual Environment

```
docker build -t op_semantic_engine:latest .
docker run -dit -v $(pwd)/model:/app/model -p 80:8080 --env-file .env op_semantic_engine:latest
```

## Embeddings

We currently use sentence transformers as text embeddings

## API Documentation

## Indexing

To index manual mappings (e.g. synonym_json_test.json), execute the following command.

```shell
bash scripts/index_manual_mapping.sh
```

It is recomended to remove the previous index, so activate clear_index as True

To validate indexing, run the following command by changing the index_name and synonyms values accordingly:
```shell
python -m tests.validation.index_validation \
--index_name manual_mapping_v4 \
--synonyms tests/search_data/imr-tag-search-indices.jsonl \
--validate singular
```

To check osm tags whether they are correctly defined.
```shell
python -m tests.validation.osm_tag_validation \
--input_file {e.g. imr-tag-db_v2.jsonl} >> incorrectly_defined_osm_tags.txt
```


## Checking Duplicates
It is important that tag-imr file should not contain duplicate entries. Run the following code to check the duplicates:

```shell
python -m app.search_engine.check_duplicates \
--input_file {e.g. imr-tag-db_v2.jsonl} \
--output_file duplicates.txt
```

If `duplicates.txt` is not empty, contact with the data providers at the team.

### Clearing index

`curl -X DELETE "[HOST]:9200/manual_mapping?pretty"`

Alternatively detail description can be found
at [link](https://deutschewelle.sharepoint.com/:w:/t/GR-GR-ReCo-KID2/EWZ2XjKlDiNLhLMUBKYVqukBvTDFrbU4AS_Pmb6OE9eQpw?e=LH5fyj)
