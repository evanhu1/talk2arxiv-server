from flask import Flask, request, jsonify
import requests
import cohere
from rerank import rerank_retrievals
import re
from dotenv import load_dotenv
from os import getenv
import pinecone

load_dotenv()
COHERE_API_KEY = getenv("COHERE_API_KEY")
PINECONE_API_KEY = getenv("PINECONE_API_KEY")
pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
co = cohere.Client(COHERE_API_KEY)
app = Flask(__name__)
PINECONE_ENDPOINT = "https://arxiv-euyze3g.svc.gcp-starter.pinecone.io"

print(pinecone.describe_index("arxiv"))

@app.route('/embeddings/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success", "message": "pong"}), 200

@app.route('/embeddings/insert', methods=['POST'])
def insert_vector():
    global loaded
    if loaded == True:
        return jsonify({"status": "error", "message": "Already loaded"}), 400
    
    content = request.json
    pdfId = content['pdfId']

    response = requests.get("https://ar5iv.org/" + pdfId)
    file = open("paper.html", "wb")
    file.write(response.content)
    file.close()

    elements = partition_html(filename="paper.html")
    for element in elements:
        element.apply(lambda x: replace_unicode_quotes(clean_non_ascii_chars(clean(x, extra_whitespace = True, dashes = True, bullets = True, trailing_punctuation = True, lowercase = True))))

    # Lambda function to replace \n with spaces and then collapse multiple whitespaces into a single space
    collapse_whitespace = lambda text: re.sub(r'\s+', ' ', text.replace('\n', ' '))

    docs = [collapse_whitespace(chunk.text) for chunk in chunk_by_title(elements, max_characters=500)]

    embeddings = embed_doc(docs)

    collection.add(embeddings=embeddings, documents=docs, ids=[str(x) for x in list(range(collection.count() + 1, collection.count() + len(embeddings) + 1))], metadatas=[{"pdfId": pdfId}] * len(embeddings))
    print(collection.count())
    loaded = True

    return jsonify({"status": "success"}), 200

@app.route('/embeddings/query', methods=['POST'])
def retrieve_vector():
    content = request.json
    pdfId = content['pdfId']
    query = content['query']
    N, K = 20, 5

    retrieved_docs = collection.query(
      query_embeddings=[query_vector],
      n_results=N,
      where={"pdfId": {"$eq": pdfId}}
    )["documents"][0]
    
    print(retrieved_docs)
    reranked_docs = rerank_retrievals(query, retrieved_docs, K)

    if retrieve_vector:
        return jsonify({"status": "success", "data": reranked_docs}), 200
    else:
        return jsonify({"status": "error", "message": "Vector not found"}), 404

if __name__ == '__main__':
    app.run(port=5328)