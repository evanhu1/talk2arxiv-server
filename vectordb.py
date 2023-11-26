from rerank import rerank_retrievals
from dotenv import load_dotenv
from os import getenv
import pinecone
from pdf import split_pdf_into_chunks
from embeddings import embed_docs, embed_query;
import uuid

def generate_random_uuid():
    return uuid.uuid4()

load_dotenv()
PINECONE_API_KEY = getenv("PINECONE_API_KEY")
PINECONE_ENDPOINT = "https://arxiv-euyze3g.svc.gcp-starter.pinecone.io"

pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
index = pinecone.Index("arxiv")
loaded_papers = {}

def embed_paper(paper_id):
  global loaded_papers
  paper_url = "https://arxiv.org/pdf/" + paper_id
  if paper_url in loaded_papers:
      return {"status": "error", "message": "Already loaded"}

  chunk_text_pairs = split_pdf_into_chunks(paper_url)
  embedded_texts = [x['embedded_text'] for x in chunk_text_pairs]
  chunks = [x['chunk'] for x in chunk_text_pairs]
  embeddings = embed_docs(chunks)

  index.upsert([{
      'id': str(generate_random_uuid()), 
      "values": embeddings[i], 
      "metadata": {"embedded_text": embedded_texts[i], "chunk": chunks[i], "paper_id": paper_id}
    } for i in range(len(embeddings))])

  loaded_papers[paper_url] = True
  return {"status": "success"}

def retrieve_context(query, paper_id):
  N, K = 20, 5

  query_vector = embed_query(query)
  
  retrieved_docs = index.query(
    top_k=N,
    filter={"paper_id": {"$eq": paper_id}},
    include_metadata=True,
    vector=query_vector
  )["matches"]

  texts = [str(x['metadata']['chunk']) for x in retrieved_docs]
  
  print(texts)
  reranked_docs = rerank_retrievals(query, texts, K)

  if reranked_docs:
      return {"status": "success", "data": reranked_docs}
  else:
      return {"status": "error", "message": "Vector not found"}

# embed_paper("2208.01066.pdf")
# print(retrieve_context("what is the title?", "https://arxiv.org/pdf/2106.01558.pdf"))
