from flask import Flask, request, jsonify
from embeddings import insert_vector, retrieve_vector, ping

app = Flask(__name__)

@app.route('/embeddings/ping', methods=['GET'])
def ping_route():
    return ping()

@app.route('/embeddings/insert', methods=['POST'])
def insert_vector_route():
    return insert_vector(request)

@app.route('/embeddings/query', methods=['POST'])
def retrieve_vector_route():
    return retrieve_vector(request)

if __name__ == '__main__':
    app.run(port=5328)
