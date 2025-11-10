<img width="1280" height="200" alt="Github-Banner_spot" src="https://github.com/user-attachments/assets/bec5a984-2f1f-44e7-b50d-cc6354d823cd" />

# 🏷️ SPOT OSM Tag Search API

This repository contains the **semantic tag search engine** for the SPOT system.  
It maps natural language descriptors to relevant **OSM tag bundles**, using a hybrid search system powered by **Elasticsearch** and **sentence transformers**.

---

## 🚀 Quickstart

### Start the virtual environment:

```bash
docker build -t op_semantic_engine:latest .
docker run -dit -v $(pwd)/model:/app/model -p 80:8080 --env-file .env op_semantic_engine:latest
```

### Indexing

To index manual mappings (e.g. synonym_json_test.json), execute the following command.

```bash
bash scripts/index_manual_mapping.sh
```

It is recomended to remove the previous index, so activate clear_index as True

To validate indexing, run the following command by changing the index_name and synonyms values accordingly:

```bash
python -m tests.validation.index_validation \
--index_name manual_mapping_v4 \
--synonyms tests/search_data/imr-tag-search-indices.jsonl \
--validate singular
```

To check osm tags whether they are correctly defined.

```bash
python -m tests.validation.osm_tag_validation \
--input_file {e.g. imr-tag-db_v2.jsonl} >> incorrectly_defined_osm_tags.txt
```

### Checking Duplicates

It is important that tag-imr file should not contain duplicate entries. Run the following code to check the duplicates:

```bash
python -m app.search_engine.check_duplicates \
--input_file {e.g. imr-tag-db_v2.jsonl} \
--output_file duplicates.txt

If duplicates.txt is not empty, contact with the data providers at the team.

### Clearing index

```bash
curl -X DELETE "[HOST]:9200/manual_mapping?pretty"
```

A sample `docker-compose.yml` with an embedded Elasticsearch service is provided in this repo for local development.

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `ELASTICSEARCH_URL` | URL of the Elasticsearch service (e.g. `http://localhost:9200`). |
| `ELASTICSEARCH_INDEX` | Name of the index for tag bundle search. |
| `SENT_TRANSFORMER` | Name of the sentence transformer model used for semantic vector search (e.g. `all-MiniLM-L6-v2`). |
| `MANUAL_MAPPING` | Path to a static JSON file for manual OSM tag bundle mapping. |
| `COLOR_MAPPING` | Path to a color-to-tag bundle mapping file (optional). |
| `PORT` | Port the API will be served on (default: `5000`). |

> **Note:** These values can be adjusted in the `.env` file. Be sure to define them before running the service.

---

## 🔑 Features

- Maps arbitrary text descriptions (e.g. "train tracks", "brown bench") to structured OSM tag bundles
- Uses **hybrid search**: BM25 + SBERT semantic search
- Provides APIs for:
  - Descriptor → tag bundle lookup
  - Color name → tag bundle matching
  - Static mapping override (manual bundle files)

---

## 🧩 Part of the SPOT System

This module is called by:
- [`central-nlp-api`](https://github.com/dw-innovation/kid2-spot-central-nlp-api) — to enrich user queries with actual OSM-compatible tags

It serves as the "semantic bridge" between human language and the OSM tag system.

---

## 🔗 Related Docs

- [Main SPOT Repo](https://github.com/dw-innovation/kid2-spot)
- [Central NLP API](https://github.com/dw-innovation/kid2-spot-central-nlp-api)

---

## 🙌 Contributing

We welcome contributions of all kinds — from developers, journalists, mappers, and more!  
See [CONTRIBUTING.md](https://github.com/dw-innovation/kid2-spot/blob/main/CONTRIBUTING.md) for how to get started.
Also see our [Code of Conduct](https://github.com/dw-innovation/kid2-spot/blob/main/CODE_OF_CONDUCT.md).

---

## 📜 License

Licensed under [AGPLv3](../LICENSE).
