from flask_pymongo import PyMongo


def clear_data(mongo):
    result = mongo.db.data.delete_many({})
    return result.deleted_count


def post_data(mongo, data):
    barcode = data["barcode"]
    mongo.db.data.replace_one({"barcode": barcode}, data, upsert=True)
    return data


def get_data(mongo, barcode):
    data = mongo.db.data.find_one({"barcode": int(barcode)})
    if data:
        data = {k: v for k, v in data.items() if k != "_id"}
    return data
