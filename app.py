from flask import Flask, request, jsonify
from vectordb import embed_paper, retrieve_context
from pdf import ping
from flask_cors import CORS
from openai_api import converse
import docker

client = docker.from_env()

if len(client.containers.list()) == 0:
  client.containers.run("lfoppiano/grobid:0.8.0", detach=True, ports={'8070/tcp': 8070})

app = Flask(__name__)
CORS(app, origins=["https://www.talk2arxiv.org", "https://talk2arxiv.com", "http://localhost:3000", "https://localhost:3000"])

@app.route('/ping', methods=['GET'])
def ping_route():
    return jsonify({"message": "Service is up and running"}), 200

@app.route('/ping_grobid', methods=['GET'])
def ping_grobid_route():
    return (jsonify({"message": "Grobid is up and running"}), 200) if ping() else (jsonify({"message": "Grobid is down"}), 500)

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

@app.route('/chat', methods=['POST'])
def chat_route():
    content = request.json
    prompt = content['prompt']
    return jsonify(converse(prompt))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3001)
