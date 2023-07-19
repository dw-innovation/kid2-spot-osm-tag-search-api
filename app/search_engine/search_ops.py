import numpy as np
def search_osm_tag(word, model, search_engine, limit):
    wv = model[word]

    os_tags = search_engine.find(np.array(wv), metric='cosine', limit=limit, exclude_self=True)
    results = []
    for idx, os_tag in enumerate(os_tags):


        # it might be a bug at the library, so we ignore the last item
        if idx == len(os_tags) -1:
            continue

        results.append(
            {'uri': os_tag.tags['tag']['uri'],
             'osm_tag': os_tag.tags['tag']['osm_tag']}
        )

    return results