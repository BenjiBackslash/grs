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
        with open("plan_system/test/res/event2.json") as fdr:
            self.events2 = json.loads(fdr.read())
        with open("plan_system/test/res/event3.json") as fdr:
            self.events3 = json.loads(fdr.read())

    def test_clear(self):
        self._do_test_clear()

    def _do_test_clear(self):

        _impl.clear_event(self.mongo)
        _impl.clear_history(self.mongo)
        for e in self.events:
            _impl.event(self.mongo, e)
        products_history = _impl.update_history(self.mongo, 1)
        shop_list = _impl.make_shop_list(products_history["items"])
        self.assertEqual(shop_list[0]["barcode"], "5000189974579")
        self.assertEqual(shop_list[0]["units"], 2)

    def test_just_history(self):
        self._do_test_clear()
        products_history = _impl.update_history(self.mongo, 1)
        shop_list = _impl.make_shop_list(products_history["items"])
        self.assertEqual(shop_list[0]["barcode"], "5000189974579")
        self.assertEqual(shop_list[0]["units"], 2)

    def test_after_buy_1_unit(self):
        self._do_test_clear()
        for e in self.events2:
            _impl.event(self.mongo, e)
        products_history = _impl.update_history(self.mongo, 1)
        shop_list = _impl.make_shop_list(products_history["items"])
        self.assertEqual(shop_list[0]["barcode"], "5000189974579")
        self.assertEqual(shop_list[0]["units"], 1)

    def test_change_in_avg(self):
        self._do_test_clear()
        for e in self.events3:
            _impl.event(self.mongo, e)
        products_history = _impl.update_history(self.mongo, 1)
        shop_list = _impl.make_shop_list(products_history["items"])
        self.assertEqual(shop_list[0]["barcode"], "5000189974579")
        self.assertEqual(shop_list[0]["units"], 1)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
