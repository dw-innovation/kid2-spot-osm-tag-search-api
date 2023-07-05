#echo Mapping wikidata ids with osm ids
#
#python -m code.osm_ops \
#--input_file datasets/wikidata.tsv \
#--output_file datasets/osm_wikidata_mapping.tsv \
#--map

#echo Fetch osm data for each osm id and save them into datasets/osm/raw
#
#python -m code.osm_ops \
#--input_file datasets/osm_wikidata_mapping.tsv \
#--output_file datasets/osm/raw \
#--fetch

echo