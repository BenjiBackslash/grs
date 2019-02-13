from datetime import datetime, timedelta
import math


def clear_event(mongo):
    result = mongo.db.event.delete_many({})
    return result.deleted_count

def clear_history(mongo):
    result = mongo.db.history.delete_many({})
    return result.deleted_count


def event(mongo, item):
    db_item = {k: v for k, v in item.items() if k != "date"}
    db_item["date"] = datetime.strptime(item["date"], "%Y-%m-%d %H:%M:%S")
    db_item["user_id"] = str(db_item["user_id"])
    mongo.db.event.insert_one(db_item)
    return db_item


def update_history(mongo, user_id):
    products_history = mongo.db.history.find_one({"user_id": user_id})
    if not products_history:
        products_history = {"user_id": str(user_id), "last_event": datetime.utcnow() - timedelta(days=30), "items": {}}
    history_items = products_history["items"]
    last_event = products_history["last_event"]

    events = mongo.db.event.find({"user_id": str(user_id), "date": {"$gt": last_event}})
    for e in events:
        barcode = str(e["barcode"])
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
            item_hist["avg_days"] += (days - item_hist["avg_days"]) / item_hist["total"]

        item_hist["last"] = e["date"]
        products_history["last_event"] = e["date"]

    products_history["items"] = history_items
    mongo.db.history.replace_one({"user_id": str(user_id)}, products_history, upsert=True)
    return products_history


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
