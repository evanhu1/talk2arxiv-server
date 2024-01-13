from rerank import rerank_retrievals
from dotenv import load_dotenv
from os import getenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http import models
from pdf import split_pdf_into_chunks, get_metadata
from embeddings import embed_docs, embed_query;
import uuid

def generate_random_uuid():
    return uuid.uuid4()

load_dotenv()
QDRANT_API_KEY = getenv("QDRANT_API_KEY")
QDRANT_ENDPOINT = "https://1d72f096-5f17-469d-a1c2-570b224c30c2.us-east4-0.gcp.cloud.qdrant.io"

qdrant_client = QdrantClient(
    QDRANT_ENDPOINT,
    api_key=QDRANT_API_KEY,
)

def check_already_embedded(paper_id):
  retrieved_docs = qdrant_client.search(
    collection_name="talk2arxiv",
    limit=1,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="paper_id",
                match=models.MatchValue(
                    value=paper_id,
                ),
            )
        ]
    ),
    query_vector=[0.0 for i in range(1024)]
  )
  return len(retrieved_docs) > 0

def embed_paper(paper_id):
  if check_already_embedded(paper_id):
      return {"status": "error", "message": "Already loaded"}
  
  paper_url = "https://arxiv.org/pdf/" + paper_id + (".pdf" if ".pdf" not in paper_id else "")

  chunk_text_pairs = split_pdf_into_chunks(paper_url)
  embedded_texts = [x['embedded_text'] for x in chunk_text_pairs]
  chunks = [x['chunk'] for x in chunk_text_pairs]
  embeddings = embed_docs(embedded_texts)

  paper_metadata = get_metadata(paper_url)
  paper_title = "" if paper_metadata == "" else paper_metadata["title"]

  qdrant_client.upsert(
     collection_name="talk2arxiv",
     wait=True,
     points=[PointStruct(
      id=str(generate_random_uuid()), 
      vector=embeddings[i], 
      payload={"embedded_text": embedded_texts[i], "chunk": chunks[i], "paper_id": paper_id, "paper_title": paper_title}
   ) for i in range(len(embeddings))])

  return {"status": "success"}

def retrieve_context(query, paper_id):
  N, K = 10, 3

  query_vector = embed_query(query)[0]
  
  retrieved_docs = qdrant_client.search(
    collection_name="talk2arxiv",
    limit=N,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="paper_id",
                match=models.MatchValue(
                    value=paper_id,
                ),
            )
        ]
    ),
    query_vector=query_vector
  )

  texts = [str(doc.payload['embedded_text']) + ":\n" + str(doc.payload['chunk']) for doc in retrieved_docs]
  paper_title = retrieved_docs[0].payload.get('paper_title', "")

  reranked_docs = rerank_retrievals(query, texts, K)

  if reranked_docs:
      return {"status": "success", "data": reranked_docs, "paper_title": paper_title}
  else:
      return {"status": "error", "message": "Vector not found"}

# embed_paper("2208.01066.pdf")
# print(retrieve_context("what is the title?", "https://arxiv.org/pdf/2106.01558.pdf"))

# qdrant_client.upsert(
#      collection_name="talk2arxiv",
#      wait=True,
#      points=[PointStruct(
#       id=str(generate_random_uuid()), 
#       vector=[1]*1024,
#       payload={"paper_id": 1}
#    )]
# )

# print(embed_paper("2106.01558.pdf"))
# print(retrieve_context("hello", "2106.01558.pdf"))
