# Copyright (c) 2018 Cobus Nel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import sys
import os
sys.path.insert(0, "..")  # noqa
from dkit.data.containers import (
    FlexShelve,
    JSONShelve,
    OrderedSet,
    RangeCounter,
    ReusableStack,
    SizedMap,
    SortedCollection,
)
from random import shuffle
from pathlib import Path


class TestJsonShelve(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.filename = "output/jsonshelve_test_db.json"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.filename):
            os.remove(cls.filename)

    def test_a_write(self):
        with JSONShelve.open(self.filename) as db:
            db["int"] = 1
            db["float"] = 1.0
            db["str"] = "str"

    def test_b_read(self):
        with JSONShelve.open(self.filename) as db:
            self.assertEqual(db["int"], 1)
            self.assertEqual(db["float"], 1.0)
            self.assertEqual(db["str"], "str")

    def test_c_len(self):
        with JSONShelve.open(self.filename) as db:
            self.assertEqual(len(db), 3)

    def test_d_del_item(self):
        with JSONShelve.open(self.filename) as db:
            db["delme"] = True
            del db["delme"]
            self.assertTrue("delme" not in db)

    def test_e_iter(self):
        with JSONShelve.open(self.filename) as db:
            keys = list(db.keys())
            self.assertEqual(
                keys,
                ["int", "float", "str"]
            )

    def test_f_del(self):
        """test that sync occur when an object is deleted"""
        with JSONShelve.open(self.filename) as db:
            db["exit"] = True
        with JSONShelve.open(self.filename) as db1:
            self.assertEqual(db1["exit"], True)
            db1.close()


class TestSizedMap(unittest.TestCase):

    def setUp(self):
        self.sample = {
            i: i for i in range(5)
        }

    def test_specified_callback(self):
        """
        test class with specified callback
        """
        stack = []

        def callback(key, value):
            stack.append((key, value))

        sm = SizedMap(3, callback)
        sm.update(**self.sample)

        self.assertEqual(
            stack,
            [(0, 0), (1, 1)]
        )

    def test_classmethod_callback(self):
        """
        test class with class method callback
        """
        class Cb:

            def __init__(self):
                self.stack = []

            def callback(self, key, value):
                self.stack.append((key, value))

        cb = Cb()

        sm = SizedMap(3, cb.callback)
        sm.update(**self.sample)

        self.assertEqual(
            cb.stack,
            [(0, 0), (1, 1)]
        )

    def test_derived_callback(self):

        stack = []

        class Deriv(SizedMap):

            def on_discard(self, k, v):
                stack.append((k, v))

        sm = Deriv(3)
        sm.update(**self.sample)

        self.assertEqual(
            stack,
            [(0, 0), (1, 1)]
        )


class TestRangeCounter(unittest.TestCase):

    def test_init(self):
        c = RangeCounter(0, 5, 10, 15)
        # print(c.store.get(2))
        c.store.__init_subclass__


class TestReusableStack(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.the_list = [1, 2, 3, 4]

    def setUp(self):
        self.stack = ReusableStack(self.the_list)

    def test_pop(self):
        """test removing items"""
        for item in self.the_list[::-1]:
            self.assertEqual(item, self.stack.pop())

    def test_reset(self):
        """test resetting the stack"""
        self.stack.pop()
        self.stack.reset()
        self.assertEqual(self.the_list[-1], self.stack.pop())

    def test_len(self):
        """test len function"""
        self.stack.pop()
        self.assertEqual(len(self.stack), len(self.the_list))

    def test_overflow(self):
        """test for error when pop is called on empty stack"""
        with self.assertRaises(IndexError) as _:
            for i in range(len(self.the_list) + 1):
                self.stack.pop()


class TestSortedCollection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.n = 100
        cls.lst = (list(range(cls.n)))
        shuffle(cls.lst)
        cls.c = SortedCollection(cls.lst)

    def test_len(self):
        self.assertEqual(len(self.c), self.n)

    def test_min(self):
        self.assertEqual(self.c.min_value, 0)

    def test_max(self):
        self.assertEqual(self.c.max_value, self.n-1)

    def test_contains(self):
        self.assertEqual(0 in self.c, True)
        self.assertEqual(self.n-1 in self.c, True)

    def test_count(self):
        self.assertEqual(self.c.count(0), 1)

    def test_find_functions(self):
        self.assertEqual(self.c.find_gt(10), 11)
        self.assertEqual(self.c.find_ge(10), 10)
        self.assertEqual(self.c.find_lt(10), 9)
        self.assertEqual(self.c.find_le(10), 10)

    def test_index(self):
        self.assertEqual(self.c.index(0), 0)
        self.assertEqual(self.c.index(10), 10)


class TestFlexShelf(unittest.TestCase):

    def test_reusable(self):
        path = Path.cwd() / "data" / "flexible_shelve.db"
        s = FlexShelve(str(path))
        for i in range(1000):
            s[(i, "a")] = i
        self.assertEqual(len(list(s.items())), 1000)
        self.assertEqual(s[(100, "a")], 100)
        path.unlink()


class TestOrderedSet(unittest.TestCase):

    def setUp(self):
        self.s = OrderedSet('abracadaba')
        self.t = OrderedSet('simsalabim')

    def test_sequence(self):
        """Test that sequence is preserved"""
        self.assertEqual(
            ['a', 'b', 'r', 'c', 'd'],
            list(self.s)
        )

    def test_op_or(self):
        self.assertEqual(
            self.s | self.t,
            OrderedSet(['a', 'b', 'r', 'c', 'd', 's', 'i', 'm', 'l'])
        )

    def test_op_and(self):
        self.assertEqual(
            self.s & self.t,
            OrderedSet(['a', 'b'])
        )

    def test_op_minus(self):
        self.assertEqual(
            self.s - self.t,
            OrderedSet(['r', 'c', 'd'])
        )

    def test_contains(self):
        self.assertEqual(
            "a" in self.s,
            True
        )
        self.assertEqual(
            "z" in self.s,
            False
        )

    def test_equal(self):
        self.assertEqual(
            self.s == OrderedSet("abracadaba"),
            True
        )
        self.assertEqual(
            self.s == OrderedSet("ab"),
            False
        )

    def test_pop(self):
        self.assertEqual(
            self.s.pop(),
            "d"
        )
        self.assertEqual(
            self.s,
            OrderedSet(['a', 'b', 'r', 'c'])
        )


if __name__ == "__main__":
    unittest.main()
