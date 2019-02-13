from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
import math

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plan_system"

mongo = PyMongo(app)


@app.route('/event', methods=["DELETE"])
def clear_events():
    result = mongo.db.event.delete_many({})
    return jsonify({"result": "deleted {} items".format(result.deleted_count)})


@app.route('/event', methods=["POST"])
def event():
    item = request.json
    db_item = {k: v for k,v in item.items() if k != "date"}
    db_item["date"] = datetime.strptime(item["date"], "%Y-%m-%d %H:%M:%S.%f")
    mongo.db.event.insert_one(item)
    return jsonify({"result": item})


def make_shop_list(history_items):
    supply_for = 7
    shop_list = []
    for b, attr in history_items:
        cur_stock_for_days = attr["cur_units"] * attr["avg_days"]
        remain_to_stock_days = supply_for - cur_stock_for_days
        num_unit_to_buy = math.ceil(remain_to_stock_days / attr["avg_days"])
        if num_unit_to_buy:
            shop_list.append({"barcode": b, "units": num_unit_to_buy})
    return shop_list


@app.route('/plan/<user_id>', methods=["GET"])
def plan(user_id):

    products_history = mongo.db.history.find_one({"user_id": user_id})
    if not products_history:
        products_history = {"user_id": user_id, "last_event": datetime.utcnow() - timedelta(days=14), "items": {}}
    history_items = products_history["items"]
    last_event = products_history["last_event"]

    events = mongo.db.event.find({"user_id": user_id, "date": {"$gt": last_event}})
    for e in events:
        barcode = e["barcode"]
        if barcode not in history_items:
            history_items[barcode] = {
                "cur_units": 0,
                "total": 0,
                "avg_days": 0,
                "last": None
            }
        item_hist = history_items[barcode]

        thrown = e.get("thrown")
        if not thrown:
            item_hist["cur_units"] += 1
        else:
            item_hist["cur_units"] -= 1
            last = item_hist["last"]
            e_date = e["date"]
            if last is not None:
                _delta = e_date - last
                days = _delta.days
                days = max(days, 1)
            item_hist["total"] += 1
            item_hist["avg_days"] += (days-item_hist["avg_days"]) / item_hist["total"]

        item_hist["last"] = e["date"]
        products_history["last_event"] = e["date"]

    mongo.db.history.replace_one({"user_id": user_id}, products_history, upsert=True)

    shop_list = make_shop_list(history_items)

    return jsonify({"result": shop_list})


if __name__ == "__main__":
    app.run(debug=True)
