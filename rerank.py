import cohere
from dotenv import load_dotenv
from os import getenv

load_dotenv()
API_KEY = getenv("COHERE_API_KEY")
co = cohere.Client(API_KEY)

def rerank_retrievals(query, retrievals, n):
  """Retrieves the top n reranked out of retrieved documents."""
  responses = co.rerank(
    model = 'rerank-english-v2.0',
    query = query,
    documents = retrievals,
    top_n = n,
  )
  return [result["documents"]["text"] for result in responses["results"]]
