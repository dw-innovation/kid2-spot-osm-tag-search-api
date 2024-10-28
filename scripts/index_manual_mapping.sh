echo indexing manual mappings

INDEX_NAME=manual_mapping_v5
MANUAL_MAPPINGS="datasets/imr-tag-search-indices.jsonl"
CONFIG_SETTINGS="es_configs/manual_mapping/settings.json"
CONFIG_MAPPINGS="es_configs/manual_mapping/mappings.json"

python -m app.search_engine.index \
--index_manual_mappings \
--index_name $INDEX_NAME \
--fpath $MANUAL_MAPPINGS \
--config_settings $CONFIG_SETTINGS \
--config_mappings $CONFIG_MAPPINGS