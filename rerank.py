from cohere_api import rerank

def rerank_retrievals(query, retrievals, n):
  """Retrieves the top n reranked out of retrieved documents."""
  responses = rerank(
    query = query,
    retrievals = retrievals,
    n = n,
  ).results
  return [result.document["text"] for result in responses]
