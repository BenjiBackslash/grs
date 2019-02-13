import unittest
from plan_system import _impl
from flask_pymongo import PyMongo
from plan_system.app import app
import json


class TestImpl(unittest.TestCase):
    def setUp(self):
        self.mongo = PyMongo(app)
        with open("plan_system/test/res/event.json") as fdr:
            self.events = json.loads(fdr.read())
        _impl.clear_event(self.mongo)
        _impl.clear_history(self.mongo)
        for e in self.events:
            _impl.event(self.mongo, e)
        self.products_history = _impl.update_history(self.mongo, 1)

    # def test_insert_events(self):
    #     #clean
    #     _impl.clear_event(self.mongo)
    #
    #     #insert products
    #     for e in self.events:
    #         _impl.event(self.mongo, e)

    def test_history(self):
        last_event = self.products_history["last_event"]
        # self.assertEquals(last_event,)
        items = self.products_history["items"]
        self.assertEqual(len(items), 1)




    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
