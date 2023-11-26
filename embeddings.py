from cohere_api import embed

def embed_docs(chunks):
    return embed(
      docs=chunks,
      input_type='search_document'
    ).embeddings

def embed_query(query):
    return embed(
      docs=[query],
      input_type='search_query'
    ).embeddings

