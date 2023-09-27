import os
from rdflib import Namespace, Graph
from dotenv import load_dotenv

load_dotenv()

# Namespaces
WD = Namespace("https://wiki.openstreetmap.org/entity/")
WDT = Namespace("https://wiki.openstreetmap.org/prop/direct/")
SCHEMA = Namespace("http://schema.org/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
WIKIBASE = Namespace("http://wikiba.se/ontology#")

def _load_graph(graph_name):
    g = Graph()
    g.parse(graph_name)
    g.bind("wd", WD)
    g.bind("wdt", WDT)
    g.bind("schema1", SCHEMA)
    g.bind("wikidata", WIKIDATA)

    return g


def load_graph():
    return _load_graph(graph_name=os.getenv("OSM_KG"))
