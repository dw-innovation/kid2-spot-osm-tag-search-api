import unittest
from app.kg.construction_ops import scrape_osm_wiki_description, process_osm_wiki_description


class TestKGMethods(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_wiki_descriptions(self):
        test_osm_tags = [
            {
                "osm_tag": "healthcare:speciality=hepatology",
                "descriptions": [
                    "Medical speciality concerning the study of liver, gallbladder, biliary tree, and pancreas as well as management of their disorders."]
            },
            {
                "osm_tag": "healthcare:speciality=endocrinology",
                "descriptions": [
                    "Medical speciality concerning the endocrine system, its diseases, and its specific secretions known as hormones."
                ]
            }
            ,
            {
                "osm_tag": "baseball=softball",
                "descriptions": ['Type of baseball that is played on a field.',
                                 'A modified form of baseball played on a smaller field with a larger ball, seven rather than nine innings, and underarm pitching. The game evolved during the late 19th century from a form of indoor baseball.',
                                 'Usesport=softballinstead.']

            },
            {
                "osm_tag": "amenity=restaurant",
                "descriptions": ['A restaurant sells full sit-down meals with servers, and may sell alcohol.',
                                 'amenity=restaurantis applied to generally formal eating places with sit-down facilities selling full meals served by waiters and often licensed (where allowed) to sell alcoholic drinks.',
                                 'Set anodeor draw as anareaalong the restaurant outline. Tag it withamenity=restaurantandname=*.',
                                 'Recommended:', 'Optional:', 'If applicable:', 'Rare combinations:',
                                 'If the restaurant and a hotel is the same add another point and the corresponding properties. (SeeOne feature, one OSM element)']

            }
        ]

        for test_osm_tag in test_osm_tags:
            wiki_descriptions = process_osm_wiki_description(scrape_osm_wiki_description(test_osm_tag["osm_tag"]))

            if wiki_descriptions is None:
                raise TypeError

            for test_description in test_osm_tag["descriptions"]:
                assert test_description in wiki_descriptions


if __name__ == '__main__':
    unittest.main()
