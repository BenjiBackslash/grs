from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from id_engine import _impl

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/id_engine"

mongo = PyMongo(app)


@app.route('/data', methods=["DELETE"])
def clear_data():
    deleted_count = _impl.clear_data(mongo)
    return jsonify({"result": "deleted {} items".format(deleted_count)})


@app.route('/data', methods=["POST"])
def post_data():
    data = _impl.post_data(mongo, request.json)
    return jsonify({"result": data})


@app.route('/data/<barcode>', methods=["GET"])
def get_data(barcode):
    data = _impl.get_data(mongo, barcode)
    output = 'No Data Found'
    if data:
        output = data
    return jsonify({"result": output})


if __name__ == "__main__":
    app.run(debug=True)
