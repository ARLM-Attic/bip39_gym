"""Unit tests for bip39-entropy-mixin"""
#Python Standard Library 2.7
import unittest
import sys

import app #app.py
import bip39 #bip39.py

BITS_128 = "10" * 64
BITS_129 = BITS_128 + "1"
BITS_32 = "10" * 16
BITS_288 = "10" * 144

class FunctionTest(unittest.TestCase):
    """Test various helper functions"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_num_entropy_warnings(self):
        """"Provide weak entropy to generate warnings"""
        self.assertEqual(app.num_entropy_warnings("0", print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("1", print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("11",
                                                  print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("111",
                                                  print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("1111",
                                                  print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("11111",
                                                  print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("111111",
                                                  print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("1111111",
                                                  print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings("11111111",
                                                  print_warning=False), 1)
        self.assertEqual(app.num_entropy_warnings(bip39.dec2bin(sys.maxint),
                                                  print_warning=False), 1)


    def test_num_entropy_warnings_none(self):
        """Provide entropy that should not generate warnings"""
        self.assertEqual(app.num_entropy_warnings("10",
                                                  print_warning=False), 0)
        self.assertEqual(app.num_entropy_warnings(bip39.dec2bin(sys.maxint - 1),
                                                  print_warning=False), 0)

    def test_is_valid_entropy_valid(self):
        """Provide valid examples of entropy"""

        #Mod 32
        #Beween 128 bits and 256 (inclusive)
        assert len(BITS_128) == 128
        self.assertTrue(app.is_valid_entropy(BITS_128, print_error=False))

    def test_invalid_entropy(self):
        """Provide invalid examples of entropy"""
        #Not mod 32
        assert len(BITS_129) == 129
        self.assertFalse(app.is_valid_entropy(BITS_129, print_error=False))

        #Less than 128 bits
        assert len(BITS_32) == 32
        self.assertFalse(app.is_valid_entropy(BITS_32, print_error=False))

        #More than 256 bits
        assert len(BITS_288) == 288
        self.assertFalse(app.is_valid_entropy(BITS_288, print_error=False))
