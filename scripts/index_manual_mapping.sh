echo indexing manual mappings

INDEX_NAME=manual_mapping
MANUAL_MAPPINGS="tests/search_data/synonym_json_v3.json"
CONFIG_SETTINGS="es_configs/manual_mapping/settings.json"
CONFIG_MAPPINGS="es_configs/manual_mapping/mappings.json"

python -m app.search_engine.index \
--index_manual_mappings \
--index_name $INDEX_NAME \
--fpath $MANUAL_MAPPINGS \
--config_settings $CONFIG_SETTINGS \
--config_mappings $CONFIG_MAPPINGS