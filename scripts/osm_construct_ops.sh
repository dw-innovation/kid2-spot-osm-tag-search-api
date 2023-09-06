#echo Mapping wikidata ids with osm ids
#
#python -m code.kg.construction_ops \
#--input_file datasets/wikidata.tsv \
#--output_file datasets/osm_wikidata_mapping.tsv \
#--map

#echo Fetch osm data for each osm id and save them into datasets/osm/raw
#
#python -m app.kg.construction_ops \
#--input_file datasets/osm_wikidata_mapping_v3.tsv \
#--output_file datasets/osm/raw \
#--fetch


echo merge knowledge graphs for constructing

python -m app.kg.construction_ops \
--input_file datasets/osm/raw \
--output_file datasets/osm/osm_kg.ttl \
--merge_kg


echo create a custom OSM kg combining selected wikidata combination and osm combination
python -m app.kg.construction_ops \
--wikidata_ref datasets/wikidata_v2.tsv \
--osm_ref datasets/osm/osm_kg.ttl \
--mapping_ref datasets/osm_wikidata_mapping_v3.tsv \
--output_file datasets/osm/osm_enriched_kg.ttl \
--create_kg
