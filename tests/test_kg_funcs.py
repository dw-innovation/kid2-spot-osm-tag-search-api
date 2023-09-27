import unittest
import pandas as pd
from app.kg.utils import load_graph
from app.kg.search_ops import fetch_english_name, fetch_descriptions
from rdflib import URIRef, Namespace
from thefuzz import process, fuzz
from rdflib.namespace import OWL, RDF, RDFS

WD = Namespace("https://wiki.openstreetmap.org/entity/")
WDT = Namespace("https://wiki.openstreetmap.org/prop/direct/")


class TestKGMethods(unittest.TestCase):

    def setUp(self):
        self.g = load_graph()

    def test_wd_label_mapping(self):
        example_wd = WD["Q6961"]

        match = self.linking_func(example_wd)

        self.assertEqual(match, "fast food")

        example_wd = WD["Q6034"]

        match = self.linking_func(example_wd)

        self.assertEqual(match, "church building")

    def linking_func(self, example_wd):
        # candidate wikidata label
        candidate_labels = set()
        for o in self.g.objects(example_wd, predicate=OWL.sameAs):
            wikidata_label = str(self.g.value(o, RDFS.label))
            candidate_labels.add(wikidata_label)
        name = str(self.g.value(example_wd, WDT["P19"]))
        match, score = process.extract(name, list(candidate_labels), scorer=fuzz.token_set_ratio, limit=1)[0]
        return match

    def test_duplicates(self):
        osm_tag_uri_pairs = []
        for s, _, _ in self.g.triples((None, WDT["P2"], WD["Q2"])):
            name = self.g.value(s, WDT["P19"])
            osm_tag_uri_pairs.append({"uri": str(s),
                                      "osm_tag": str(name)})

        data = pd.DataFrame(osm_tag_uri_pairs)
        pair_count = len(data)

        self.assertEqual(len(data['uri'].unique()), len(data["osm_tag"].unique()))
        self.assertEqual(pair_count, len(data['uri'].unique()))

        subj = WD["Q6034"]
        combinations = []
        for o in self.g.objects(subj, WDT["P46"]):
            obj_name = fetch_english_name(self.g, o)

            obj_type = self.g.value(o, WDT["P2"])
            obj_type = self.g.value(obj_type, RDFS.label)
            combinations.append({'uri': str(o),
                                 'osm_tag': str(obj_name),
                                 'type': str(obj_type)})

        data = pd.DataFrame(combinations)
        combination_count = len(data)

        self.assertEqual(len(data['uri'].unique()), len(data["osm_tag"].unique()))
        self.assertEqual(combination_count, len(data['uri'].unique()))

    def test_descriptions(self):
        test_tags = [{
            "osm_tag": WD["Q4819"],
            "descriptions": [
                'amenity=restaurantis applied to generally formal eating places with sit-down facilities selling full meals served by waiters and often licensed (where allowed) to sell alcoholic drinks.',
                'If the restaurant and a hotel is the same add another point and the corresponding properties. (SeeOne feature, one OSM element)',
                'Set anodeor draw as anareaalong the restaurant outline. Tag it withamenity=restaurantandname=*.',
                'A restaurant sells full sit-down meals with servers, and may sell alcohol.', 'Rare combinations:',
                'If applicable:', 'Recommended:', 'Optional:']

        }]

        for test_tag in test_tags:
            descriptions = fetch_descriptions(self.g, test_tag["osm_tag"])
            assert test_tag["descriptions"] == descriptions


if __name__ == '__main__':
    unittest.main()
