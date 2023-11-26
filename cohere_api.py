import cohere
from dotenv import load_dotenv
from os import getenv

load_dotenv()
API_KEY = getenv("COHERE_API_KEY")
co = cohere.Client(API_KEY)

def embed(docs, input_type):
    return co.embed(
      texts=docs,
      model='embed-english-v3.0',
      input_type=input_type
    )

def tokenize(text):
    return co.tokenize(
      text=text,
      model='embed-english-v3.0'
    )

def rerank(query, retrievals, n):
  return co.rerank(
    query = query,
    documents = retrievals,
    model = 'rerank-english-v2.0',
    top_n = n,
  )
