from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDFS, OWL
from rdflib.term import Literal
from rdflib.plugins.sparql import prepareQuery
from thefuzz import process, fuzz

WD = Namespace("https://wiki.openstreetmap.org/entity/")
WDT = Namespace("https://wiki.openstreetmap.org/prop/direct/")
SCHEMA = Namespace("http://schema.org/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")


def fetch_all_osm_tags(g: Graph):
    '''
    this function returns the uris of all osm tags
    osm tags
    P2: instance of
    Q2: tag
    P19: permanent tag ID

    osm keys
    P2: instance of
    Q7: tag
    P16: permanent key ID
    P19: permanent osm tag

    :param g:
    :return: list of {uri: , osm_tag: }
    '''
    osm_tag_uri_pairs = set()

    for s, _, n in g.triples((None, WDT["P19"], None)):
        status = g.value(s, WDT["P6"])
        # don't add the deprecated value
        if status == WD["Q5061"]:
            continue
        osm_tag_uri_pairs.add(str(s))

    return osm_tag_uri_pairs


def fetch_all_categories(g: Graph):
    '''
    fetch all categories within osm kg
    P25: category/group name
    :param g:
    :return: list of dictionaries containing category name and uri
    '''

    query = """SELECT DISTINCT ?category ?categoryLabel
        WHERE {
            ?s wdt:P25 ?category .
            ?category rdfs:label ?categoryLabel .
            filter(langMatches(lang(?categoryLabel),"en"))
        }"""

    q = prepareQuery(query, initNs={"wdt": WDT})

    categories = []

    for result in g.query(q):
        categories.append({'uri': str(result.category),
                           'name': str(result.categoryLabel)
                           })
    return categories


def fetch_tags_per_category(category: str, g: Graph):
    '''
    find the tags related to the category
    :param category:
    :return:
    '''

    query = """SELECT DISTINCT ?osmTag ?osmType
        WHERE {
            ?osmTag wdt:P2 wd:Q2 ;
                    wdt:P25 ?category .
            ?category rdfs:label ?categoryLabel .
        }"""

    q = prepareQuery(query, initNs={"wdt": WDT, "wd": WD})
    results = g.query(q, initBindings={'categoryLabel': Literal(category, lang='en')})

    tags_per_category = []
    for result in results:
        osm_tag = result.osmTag
        name = g.value(osm_tag, RDFS.label)
        tags_per_category.append({"uri": str(osm_tag),
                                  "osm_tag": str(name)})

    return tags_per_category


def fetch_tag_properties(osm_tag: str, g: Graph):
    '''
    this function gets the property of an osm tag
     P19: permanent tag ID
     P25: group name
     P33: applies to nodes
     P34: applies to ways
     P35: applies to areas
     P36: applies to relations
     P46: combinations
     P18: different from
     schema:description : description of the tag
    :param osm_tag: string osm_tag name e.g leisure=pitch
    :param g:
    :return: a dictionary containing properties of osm tag
    '''

    if 'wiki.openstreetmap.org' in osm_tag:
        subj = URIRef(osm_tag)
    else:
        subj = g.value(predicate=WDT["P19"], object=Literal(osm_tag))

    osm_tag = fetch_english_name(g, subj)

    # fetch the group name
    group = g.value(subj, WDT["P25"])
    group = str(g.value(group, RDFS.label))

    # fetch description
    description = None
    for o in g.objects(subj, SCHEMA["description"]):
        if o.language == 'en':
            description = str(o)
            break

    # applies to nodes
    applies_to_nodes = g.value(subj, predicate=WDT["P33"])
    applies_to_nodes = str(g.value(applies_to_nodes, RDFS.label))

    # applies to ways
    applies_to_ways = g.value(subj, WDT["P34"])
    applies_to_ways = str(g.value(applies_to_ways, RDFS.label))

    # applies to areas
    applies_to_areas = g.value(subj, WDT["P35"])
    applies_to_areas = str(g.value(applies_to_areas, RDFS.label))

    # applies to relations
    applies_to_relations = g.value(subj, WDT["P36"])
    applies_to_relations = str(g.value(applies_to_relations, RDFS.label))

    # wikidata label
    wikidata_label = fetch_wikidata_label(g, subj)

    # combinations, usually properties
    combinations = []
    for o in g.objects(subj, WDT["P46"]):
        obj_name = fetch_english_name(g, o)

        obj_type = g.value(o, WDT["P2"])
        obj_type = g.value(obj_type, RDFS.label)
        combinations.append({'uri': str(o),
                             'osm_tag': str(obj_name),
                             'type': str(obj_type)})

    # different from
    different_tags = []
    for o in g.objects(subj, WDT["P18"]):
        obj_name = fetch_english_name(g, o)

        obj_type = g.value(o, WDT["P2"])
        obj_type = g.value(obj_type, RDFS.label)
        different_tags.append({'uri': str(o),
                               'osm_tag': str(obj_name),
                               'type': str(obj_type)})

    subj = str(subj)

    return {
        "uri": subj,
        "osm_tag": osm_tag,
        "group": group,
        "description": description,
        "applies_to_nodes": True if applies_to_nodes == "is applicable" else False,
        "applies_to_ways": True if applies_to_ways == "is applicable" else False,
        "applies_to_areas": True if applies_to_areas == "is applicable" else False,
        "applies_to_relations": True if applies_to_relations == "is applicable" else False,
        "wikidata_label": wikidata_label,
        "combinations": combinations,
        "different_from": different_tags,
    }


def fetch_osm_tag(g, subj):
    '''
    fetch the english name of the object which might contain multiple names
    :param g:
    :param o:
    :return:
    '''
    if isinstance(subj, str):
        subj = URIRef(subj)
    obj_name = g.value(subj, WDT["P19"])

    if not obj_name:
        obj_name = g.value(subj, WDT["P16"])

    return str(obj_name)


def fetch_plain_name(osm_tag):
    if "=" in osm_tag:
        plain_name = osm_tag.split("=")[-1]
        plain_name = plain_name.replace("_", " ")
        return plain_name
    elif ":" in osm_tag:
        plain_name = osm_tag.split(":")[-1]
        plain_name = plain_name.replace("_", " ")
        return plain_name

    plain_name = osm_tag
    plain_name = plain_name.replace("_", " ")

    return plain_name


def fetch_english_name(g, subj):
    '''
    fetch the english name of the object which might contain multiple names
    :param g:
    :param o:
    :return:
    '''
    if isinstance(subj, str):
        subj = URIRef(subj)
    obj_name = None
    for o in g.objects(subj, RDFS.label):
        if o.language == 'en':
            obj_name = str(o)
            break
    return obj_name


def fetch_wikidata_label(g, subj):
    '''
    fetch the label from wikidata
    :param g:
    :param o:
    :return:
    '''
    if isinstance(subj, str):
        subj = URIRef(subj)
    # candidate wikidata label
    candidate_labels = set()
    for o in g.objects(subj, predicate=OWL.sameAs):
        wikidata_label = str(g.value(o, RDFS.label))
        candidate_labels.add(wikidata_label)

    name = str(g.value(subj, WDT["P19"]))
    match, _ = process.extract(name, list(candidate_labels), scorer=fuzz.token_set_ratio, limit=1)[0]

    return match


def fetch_descriptions(g, subj):
    '''
    fetch the english descriptions that are scraped from taginfo box and/or osm wiki descriptions
    :param g:
    :param o:
    :return:
    '''
    if isinstance(subj, str):
        subj = URIRef(subj)
    descriptions = set()
    for o in g.objects(subj, SCHEMA.description):
        if o.language == 'en':
            descriptions.add(str(o))
    if len(descriptions) == 0:
        return None

    descriptions = list(descriptions)
    return sorted(descriptions, key=len, reverse=True)[0]


if __name__ == '__main__':
    # print(fetch_all_osm_tags(g))
    # print(fetch_tag_properties(osm_tag='amenity=restaurant', g=g))
    # print(fetch_all_categories(g))
    print(fetch_tags_per_category(category='health'))
