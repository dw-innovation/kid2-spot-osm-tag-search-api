# OSM Semantic Search
The repository contains the source code of the steps for the OSM semantic search engine.


## Source Collection

Get the wiki ids of the OSM tags/keys from `[Wikidata](https://query.wikidata.org/)` and save the results as `wikidata.tsv`.

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

Checkout `scripts/osm_ops.sh` to learn the steps of constructing custom kg.

These steps are:
- Mapping wikidata ids with osm ids
- Fetching osm data for each osm id and save them into datasets/osm/raw

## Embeddings

```
conda create -n fasttext_embedding python=3.8
conda activate fasttext_embedding
```