from flask import Flask, request, jsonify
from vectordb import embed_paper, retrieve_context

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping_route():
    return jsonify({"message": "Service is up and running"}), 200

@app.route('/insert', methods=['POST'])
def insert_vector_route():
    content = request.json
    paper_id = content['paper_id']
    return jsonify(embed_paper(paper_id))

@app.route('/query', methods=['POST'])
def retrieve_vector_route():
    content = request.json
    paper_id = content['paper_id']
    query = content['query']
    return jsonify(retrieve_context(query, paper_id))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5328)
