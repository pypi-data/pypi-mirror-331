#
# Copyright (C) 2016  Cobus Nel
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#

'''
Created on 19 January 2016
'''
import sys; sys.path.insert(0, "..") # noqa
from dkit.doc.lorem import Lorem
import unittest
from dkit.utilities.security import (
    FernetBytes, Vigenere, Pie, Fernet, EncryptedStore, EncryptedIO,
    gen_password
)


class TestVigenere(unittest.TestCase):
    """Test Vigenere simple obfuscation"""

    test_case = [
        "b;asdurjvb893498udkxcm,adk",
        "0002",
        "2309u82234502",
        "SAA2345s@##$%dASF",
        "asdafasdfas",
    ]

    @classmethod
    def setUpClass(cls):
        cls.key = "12345"
        cls.C = Vigenere

    def test_vigenere(self):
        "Test encrypt - decrypt"
        for m in self.test_case:
            o = self.C(self.key)
            e = o.encrypt(m)
            self.assertEqual(m, o.decrypt(e))

    def test_invalid_key_type(self):
        "Test raise on invalid type"
        with self.assertRaises(TypeError):
            self.C(0)

    def test_invalid_msg_type(self):
        "Test raise on invalid message type"
        with self.assertRaises(TypeError):
            o = self.C(self.key)
            o.encrypt(0)

    def test_invalid_encrypted_type(self):
        "Test raise on invalid encrypted type"
        with self.assertRaises(TypeError):
            o = self.C(self.key)
            o.decrypt(0)

    def test_zero_key_length(self):
        "Test for error with zero key length"
        with self.assertRaises(ValueError):
            self.C("")


class TestFernet(TestVigenere):
    """Test Fernet encryption"""

    @classmethod
    def setUpClass(cls):
        cls.C = Fernet
        cls.key = Fernet.generate_key()

    def test_from_password(self):
        a = Fernet.from_password("password")
        b = Fernet.from_password("password")
        enc = a.encrypt("text")
        dec = b.decrypt(enc)
        self.assertEqual("text", dec)


class TestPie(unittest.TestCase):

    def test_pie(self):
        text = "as;dlfjasld;asdf@@"
        o = Pie()
        e = o.encrypt(text)
        self.assertEqual(text, o.decrypt(e))


class TestEncStore(unittest.TestCase):
    """encrypted store"""

    @classmethod
    def setUpClass(cls):
        cls.store = EncryptedStore.from_json_file(
            None, "output/test_enc_store.json"
        )

    @classmethod
    def tearDownClass(cls):
        if cls.store:
            del cls.store

    def do_test(self, key, value):
        self.store[key] = value
        self.assertEqual(self.store[key], value)

    def test_set_int(self):
        self.do_test("int", 1)

    def test_set_float(self):
        self.do_test("float", 1.0)

    def test_set_str(self):
        self.do_test("str", "string")

    def test_del(self):
        self.store["key"] = 1
        del self.store["key"]
        self.assertEqual(
            "key" in self.store,
            False
        )

    def test_x_iter_keys(self):
        self.assertEqual(
            len(list(self.store.keys())),
            3
        )


class TestEncryptedIO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        lorem = Lorem()
        cls.fernet = FernetBytes(None)
        cls.data = lorem.txt_paragraph(max=10)
        cls.fname = "output/encrypted_data.txt"

    def test_0_write(self):
        e = EncryptedIO(self.fernet)
        e.write(self.fname, self.data.encode())

    def test_1_read(self):
        e = EncryptedIO(self.fernet)
        text = e.read(self.fname)
        self.assertEqual(
            text.decode(),
            self.data
        )


class TestFunctions(unittest.TestCase):

    def test_gen_password_len(self):
        pwd = gen_password(20)
        self.assertEqual(
            len(pwd), 20
        )


if __name__ == '__main__':
    unittest.main()
