from flask import Flask, request, jsonify
from vectordb import embed_paper, retrieve_context

app = Flask(__name__)

@app.route('/embeddings/ping', methods=['GET'])
def ping_route():
    return jsonify({"message": "Service is up and running"}), 200

@app.route('/embeddings/insert', methods=['POST'])
def insert_vector_route():
    content = request.json
    paper_id = content['pdfId']
    return jsonify(embed_paper(paper_id))

@app.route('/embeddings/query', methods=['POST'])
def retrieve_vector_route():
    content = request.json
    paper_id = content['pdfId']
    query = content['query']
    return jsonify(retrieve_context(query, paper_id))

if __name__ == '__main__':
    app.run(port=5328)
