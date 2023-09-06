from rdflib import Namespace, Graph
from dotenv import load_dotenv

load_dotenv()

def load_graph():
    # Namespaces
    WD = Namespace("https://wiki.openstreetmap.org/entity/")
    WDT = Namespace("https://wiki.openstreetmap.org/prop/direct/")
    SCHEMA = Namespace("http://schema.org/")
    WIKIDATA = Namespace("http://www.wikidata.org/entity/")

    g = Graph()
    g.parse(os.getenv("OSM_KG"))

    g.bind("wd", WD)
    g.bind("wdt", WDT)
    g.bind("schema1", SCHEMA)
    g.bind("wikidata", WIKIDATA)

    return g