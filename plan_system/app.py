from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from plan_system import _impl

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plan_system"

mongo = PyMongo(app)


@app.route('/event', methods=["DELETE"])
def clear():
    deleted_count = _impl.clear_event(mongo)
    return jsonify({"result": "deleted {} items".format(deleted_count)})


@app.route('/event', methods=["POST"])
def event():
    db_item = _impl.event(mongo, request.json)
    return jsonify({"result": db_item})


@app.route('/plan/<user_id>', methods=["GET"])
def plan(user_id):
    products_history = _impl.update_history(mongo, user_id)
    shop_list = _impl.make_shop_list(products_history["items"])
    return jsonify({"result": shop_list})


if __name__ == "__main__":
    app.run(debug=True)
