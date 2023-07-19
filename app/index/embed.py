from app.kg.search_ops import fetch_all_osm_tags, fetch_wikidata_label
from app.kg.utils import load_graph
from tqdm import tqdm
from docarray import Document, DocumentArray
import fasttext

g = load_graph()
model = fasttext.load_model("model/model.bin")

da = DocumentArray(
    storage='sqlite', config={'connection': 'databases/op_tags.db', 'table_name': 'op_tags'}
)

osm_tags= fetch_all_osm_tags(g)
# fetch tags, vectorize with fasttext and index them into the search engine
for osm_tag in tqdm(osm_tags, total=len(osm_tags)):
    wd_name = fetch_wikidata_label(g, osm_tag["uri"])
    da.append(Document(embedding=model[wd_name], text=wd_name, tag=osm_tag))


