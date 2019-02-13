import unittest
from id_engine import _impl
from flask_pymongo import PyMongo
from id_engine.app import app
import json

class TestImpl(unittest.TestCase):
    def setUp(self):
        self.mongo = PyMongo(app)
        with open("id_engine/test/res/1.json") as fdr:
            self.data = json.loads(fdr.read())

    def test_insert_products(self):
        #clean
        _impl.clear_data(self.mongo)

        #insert products
        for d in self.data:
            _impl.post_data(self.mongo, d)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()