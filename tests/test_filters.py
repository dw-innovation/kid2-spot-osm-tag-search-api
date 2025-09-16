import unittest
from app.kg.search_ops import fetch_all_osm_tags
from app.kg.utils import _load_graph, WD, WIKIBASE, WDT, WIKIDATA, SCHEMA


class TestKGMethods(unittest.TestCase):
    """
    Unit tests for knowledge graph (KG) operations related to OSM tag processing.
    """

    def setUp(self):
        """
        Load the RDF knowledge graph before each test case.
        """
        self.g = _load_graph("datasets/osm/osm_enriched_kg_v3.ttl")

    def test_filter_out_depreciations(self):
        """
        Ensure that deprecated OSM tags are correctly filtered out from the graph.

        Fails if any known deprecated tag is found in the list returned by fetch_all_osm_tags().
        """
        depreceated_values = ["https://wiki.openstreetmap.org/entity/Q6255",
                              "https://wiki.openstreetmap.org/entity/Q1184"]
        all_osm_tags = fetch_all_osm_tags(self.g)

        for depreceated_value in depreceated_values:
            if depreceated_value in all_osm_tags:
                raise Exception(f"Depreceated value {depreceated_value} is not filtered")


if __name__ == '__main__':
    unittest.main()
