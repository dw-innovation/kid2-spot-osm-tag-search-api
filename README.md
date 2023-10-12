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

### Clearing index

`curl -X DELETE "[HOST]:9200/manual_mapping?pretty"`

Alternatively detail description can be found
at [link](https://deutschewelle.sharepoint.com/:w:/t/GR-GR-ReCo-KID2/EWZ2XjKlDiNLhLMUBKYVqukBvTDFrbU4AS_Pmb6OE9eQpw?e=LH5fyj)