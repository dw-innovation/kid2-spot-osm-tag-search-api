from app.kg.search_ops import fetch_all_osm_tags, fetch_descriptions, fetch_osm_tag, fetch_plain_name
from app.kg.utils import load_graph
from app.search_engine.utils import OSMTag, encode, load_model, connect_search_engine
from tqdm import tqdm


g = load_graph()

osm_tags = fetch_all_osm_tags(g)

model = load_model()

doc_index = connect_search_engine()
print("Connected to the search engine.")

BATCH = 100
processed_doc = []
for osm_tag in tqdm(osm_tags, total=len(osm_tags)):
    descriptions = fetch_descriptions(g, osm_tag)

    osm_tag_name = fetch_osm_tag(g, osm_tag)
    plain_name = fetch_plain_name(osm_tag_name)

    if not descriptions:
        descriptions = plain_name

    description_embedding = encode(descriptions, model)
    name_embedding = encode(plain_name, model)

    processed_doc.append(
        OSMTag(uri=osm_tag, text=descriptions, description_embedding=description_embedding, osm_tag=osm_tag_name,
               name_embedding=name_embedding, name=plain_name))

    if len(processed_doc) >= BATCH:
        doc_index.index(processed_doc)
        processed_doc = []

if len(processed_doc) >= 1:
    doc_index.index(processed_doc)

print(f'number of docs in the index: {doc_index.num_docs()}')
