# OSM Semantic Search

The repository contains the source code of the steps for the OSM semantic search engine.

## Virtual Environment

```
docker build -t op_semantic_engine:latest .
docker run -dit -v $(pwd)/model:/app/model -p 80:8080 --env-file .env op_semantic_engine:latest
```

## Source Collection

Get the wiki ids of the OSM tags/keys from `[Wikidata](https://query.wikidata.org/)` and save the results
as `wikidata.tsv`.

```
SELECT ?wikiData ?wikiDataLabel ?tagInfo ?tagClassLabel ?mainCategoryLabel
WHERE 
{
  ?wikiData wdt:P1282 ?tagInfo .
  OPTIONAL {?wikiData wdt:P31 ?tagClass .}
  OPTIONAL {?wikiData wdt:P910 ?mainCategory .}
  FILTER(STRSTARTS(?tagInfo, 'Tag:') || STRSTARTS(?tagInfo, 'Key:'))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

Checkout `scripts/osm_construct_ops.sh` to learn the steps of constructing custom kg.

These steps are:

- Mapping wikidata ids with osm ids

```shell
python -m app.kg.construction_ops --map --input_file {INPUT_FILE} --output_file {OUTPUT_FILE}
```

- Fetching osm data for each osm id and save them into datasets/osm/raw

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
--synonyms tests/search_data/imr-tag-db_v2.jsonl \
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