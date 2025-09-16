def construct_bm25_query(query):
    """
    Construct a BM25 full-text search query on the 'name' field.

    Args:
        query (str): The input search term.

    Returns:
        dict: A BM25 query compatible with Elasticsearch.
    """
    return {"match": {"name": query}}


def construct_knn_query(query_vector):
    """
    Construct a k-NN (vector similarity) search query.

    Args:
        query_vector (List[float]): The embedding vector for the input query.

    Returns:
        dict: A k-NN query compatible with Elasticsearch's approximate vector search.
    """
    return {
        "field": "embeddings",
        "query_vector": query_vector,
        "k": 10,
        "num_candidates": 100
    }


def search_manual_mapping(word, client, model, index_name, confidence=0.5, limit=1):
    """
    Search for a manual mapping of an OSM tag using both BM25 and k-NN search.

    Args:
        word (str): The search query.
        client (Elasticsearch): Elasticsearch client instance.
        model: The model used to encode the query into a vector.
        index_name (str): Name of the Elasticsearch index.
        confidence (float): Minimum acceptable score for returned results.
        limit (int): Maximum number of results to return.

    Returns:
        List[dict]: A list of matching OSM tag documents, each containing 'imr', 'name', and 'score'.

    Notes:
        Combines semantic vector search and keyword match using hybrid search.
    """
    query_vector = model.encode(word)
    resp = client.search(index=index_name,
                         query=construct_bm25_query(query=word),
                         knn=construct_knn_query(query_vector),
                         source=["imr", "name"],
                         request_timeout=30)

    num_docs = resp['hits']['total']['value']
    if num_docs == 0:
        print("No document is matched")
        return []

    else:
        results = resp['hits']['hits'][:limit]

        search_results = []

        for result in results:
            if result['_score'] < confidence:
                continue

            search_results.append({
                'imr': result['_source']['imr'],
                "name": result['_source']['name'],
                "score": result['_score'],
            })

        return search_results

def search_color_mapping(word, client, index_name, limit=1):
    """
    Search for color descriptor mappings in the color index using BM25.

    Args:
        word (str): The input color descriptor to search for.
        client (Elasticsearch): Elasticsearch client instance.
        index_name (str): Name of the color mapping index.
        limit (int): Number of results to return (default is 1).

    Returns:
        dict or None: A dictionary with the matched 'name' and its corresponding 'color_values',
                      or None if no match is found.
    """
    resp = client.search(index=index_name,
                         query=construct_bm25_query(query=word),
                         source=["name", "color_values"],
                         request_timeout=30)

    num_docs = resp['hits']['total']['value']
    if num_docs == 0:
        print("No document is matched")
        return None
    else:
        result = resp['hits']['hits'][:limit][0]
        return {
            "name":  result['_source']['name'],
            "color_values": result['_source']["color_values"],
        }