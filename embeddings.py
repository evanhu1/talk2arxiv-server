import cohere
from dotenv import load_dotenv
from os import getenv

load_dotenv()
API_KEY = getenv("COHERE_API_KEY")
co = cohere.Client(API_KEY)

def embed_docs(docs):
    return co.embed(
      texts=docs,
      model='embed-english-v3.0',
      input_type='search_document'
    ).embeddings

def embed_query(docs):
    return co.embed(
      texts=docs,
      model='embed-english-v3.0',
      input_type='search_query'
    ).embeddings
