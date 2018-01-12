"""Unit tests for entropy.py"""
#Python Standard Library 2.7
import unittest

#bip39_gym modules
import entropy #entropy.py

ENABLE_DEBUG_PRINT = False

class FunctionTest(unittest.TestCase):
    """Test various helper functions"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_entropy(self):
        """Test valid bit lengths for entropy"""
        self.assertEqual(len(entropy.get_entropy(n_bits=0)), 0)
        self.assertEqual(len(entropy.get_entropy(n_bits=1)), 1)
        self.assertEqual(len(entropy.get_entropy(n_bits=2)), 2)
        self.assertEqual(len(entropy.get_entropy(n_bits=7)), 7)
        self.assertEqual(len(entropy.get_entropy(n_bits=8)), 8)
        self.assertEqual(len(entropy.get_entropy(n_bits=9)), 9)
        self.assertEqual(len(entropy.get_entropy(n_bits=128)), 128)
        self.assertEqual(len(entropy.get_entropy(n_bits=256)), 256)

    def test_get_entropy_invalid(self):
        """Test invalid values for entropy"""

        with self.assertRaises(ValueError):
            entropy.get_entropy(-1)

        with self.assertRaises(TypeError):
            entropy.get_entropy('')

        with self.assertRaises(TypeError):
            entropy.get_entropy('a')

    def test_xor_valid(self):
        """Test xor with valid values"""
        self.assertEqual(entropy.xor('0', '0'), '0')
        self.assertEqual(entropy.xor('0', '1'), '1')
        self.assertEqual(entropy.xor('1', '0'), '1')
        self.assertEqual(entropy.xor('1', '1'), '0')
        self.assertEqual(entropy.xor(
            '10101010110101010001101010101010111010101010101010111010000010101',
            '10101010110101010001101010101010111010101010101010111010000010101'),
            '00000000000000000000000000000000000000000000000000000000000000000')
        self.assertEqual(entropy.xor(
            '10101010110101010001101010101010111010101010101010111010000010101',
            '00101011010101010101010111101010010001011010010101010001010000111'),
            '10000001100000000100111101000000101011110000111111101011010010010')
        self.assertEqual(entropy.xor('0' * 256, '1' * 256), '1' * 256)

    def test_xor_invalid(self):
        """Test function with invalid values"""

        #length mismatch
        with self.assertRaises(ValueError):
            entropy.xor('1', '11')

        #type is wrong
        with self.assertRaises(TypeError):
            entropy.xor('1', 1)

    def test_die_rolls_per_bits_valid(self):
        """Test function with valid numbers of die rolls"""

        #1 roll encodes [0, 3]
        self.assertEqual(entropy.die_rolls_per_bits(2), 1) # 2 bits = values [0, 3]

        #2 rolls encodes [0, 15]
        self.assertEqual(entropy.die_rolls_per_bits(4), 2) #[0, 15]

        #3 rolls encodes [0, 63]
        self.assertEqual(entropy.die_rolls_per_bits(6), 3) #[0, 63]

        #4 rolls encodes [0, 255]
        self.assertEqual(entropy.die_rolls_per_bits(8), 4) #[0, 255]

        #5 rolls encodes [0, 1023]
        self.assertEqual(entropy.die_rolls_per_bits(10), 5) #[0, 1023]

        #higher values are omitted as they are not likely to disprove the trend

    def test_die_rolls_per_bits_invalid(self):
        """Test function with invalid args"""
        with self.assertRaises(ValueError):
            entropy.die_rolls_per_bits(0)

        with self.assertRaises(ValueError):
            entropy.die_rolls_per_bits(-1)

        with self.assertRaises(TypeError):
            entropy.die_rolls_per_bits('1')

        with self.assertRaises(TypeError):
            entropy.die_rolls_per_bits('')

        #number of bits must be a multiple of 2
        with self.assertRaises(ValueError):
            entropy.die_rolls_per_bits(1)
        with self.assertRaises(ValueError):
            entropy.die_rolls_per_bits(3)
        with self.assertRaises(ValueError):
            entropy.die_rolls_per_bits(5)

    def test_die_rolls_to_bitstring_valid_2bit(self):
        """Test function with various roll and 2-bit lenth, result manually computed"""

        #2 bits
        self.assertEqual(
            entropy.die_rolls_to_bitstring(
                dice_vals=[1],
                bitstring_len=2),
            '01')

        self.assertEqual(
            entropy.die_rolls_to_bitstring(
                dice_vals=[2],
                bitstring_len=2),
            '10')

        self.assertEqual(
            entropy.die_rolls_to_bitstring(
                dice_vals=[3],
                bitstring_len=2),
            '11')

        self.assertEqual(
            entropy.die_rolls_to_bitstring(
                dice_vals=[6],
                bitstring_len=2),
            '00')

        #a second roll for 2 bits won't impact those 2 bits
        for roll2 in [1, 2, 3, 6]:
            self.assertEqual(
                entropy.die_rolls_to_bitstring(
                    dice_vals=[1, roll2],
                    bitstring_len=2),
                '01') # "xxx01"[-2:] = "01"

            self.assertEqual(
                entropy.die_rolls_to_bitstring(
                    dice_vals=[2, roll2],
                    bitstring_len=2),
                '10') # "xxx10"[-2:] = "10"

            self.assertEqual(
                entropy.die_rolls_to_bitstring(
                    dice_vals=[3, roll2],
                    bitstring_len=2),
                '11') # "xxx11"[-2:] = "11"

            self.assertEqual(
                entropy.die_rolls_to_bitstring(
                    dice_vals=[6, roll2],
                    bitstring_len=2),
                '00') # "xxx00"[-2:] = "00"

        for roll2 in [1, 2, 3, 6]:
            for roll3 in [1, 2, 3, 6]:
                self.assertEqual(
                    entropy.die_rolls_to_bitstring(
                        dice_vals=[1, roll2, roll3],
                        bitstring_len=2),
                    '01') # "xxx01"[-2:] = "01"

                self.assertEqual(
                    entropy.die_rolls_to_bitstring(
                        dice_vals=[2, roll2, roll3],
                        bitstring_len=2),
                    '10') # "xxx10"[-2:] = "10"

                self.assertEqual(
                    entropy.die_rolls_to_bitstring(
                        dice_vals=[3, roll2, roll3],
                        bitstring_len=2),
                    '11') # "xxx11"[-2:] = "11"

                self.assertEqual(
                    entropy.die_rolls_to_bitstring(
                        dice_vals=[6, roll2, roll3],
                        bitstring_len=2),
                    '00') # "xxx00"[-2:] = "00"

    def test_die_rolls_to_bitstring_entropy_uniformity(self):
        """Demonstrate uniformity of bits for all possible die rolls"""

        #Note: This is repeated for bigger ranges in check_dice_entropy.py
        for bitstring_len in [2, 4, 6]:
            for rolls_num in [1, 2, 3, 4, 5]:
                roll_sequences = _get_dice_rolls_of_len(rolls_num)
                results_0 = [0] * bitstring_len
                results_1 = [0] * bitstring_len
                for roll_sequence in roll_sequences:
                    #count up the results for bistrings generated from each roll combo
                    _dprint("Testing bit len {0} roll sequence {1}".format(
                        bitstring_len, roll_sequence))

                    try:
                        bits = entropy.die_rolls_to_bitstring(roll_sequence, bitstring_len)
                        _dprint("bitlen = {0} sequence = {1} bits = {2}".format(
                            bitstring_len, roll_sequence, bits))
                        for index, bit in enumerate(bits):
                            assert bit in ("0", "1")
                            if bit == "0":
                                results_0[index] += 1
                            else:
                                results_1[index] += 1
                    except entropy.InsufficientEntropyError:
                        _dprint(("Not enough dice rolls ({0}) for {1} bits of "
                                 "entropy. Omiting from frequency count.").format(
                                     rolls_num, bitstring_len))

                #all bits in results arrays should be equally distributed
                frequency = results_0[0]
                for index, val in enumerate(results_0):
                    self.assertEqual(
                        frequency,
                        val,
                        ("Failure for {0} bits and {1} rolls: Bit results not "
                         "uniform: {2} != {3}".format(bitstring_len, rolls_num,
                                                      results_0, results_1)))
                for index, val in enumerate(results_1):
                    self.assertEqual(
                        frequency,
                        val,
                        ("Failure for {0} bits and {1} rolls: Bit results not "
                         "uniform: {2} != {3}".format(bitstring_len, rolls_num,
                                                      results_0, results_1)))

    def test_die_rolls_to_bitstring_longer(self):
        """Test function with some longer strings, binary output manually computed"""
        self.assertEqual(
            entropy.die_rolls_to_bitstring(dice_vals=[6] * 32, bitstring_len=64),
            "0" * 64)

        self.assertEqual(
            entropy.die_rolls_to_bitstring(dice_vals=[3] * 32, bitstring_len=64),
            "1" * 64)

        self.assertEqual(
            entropy.die_rolls_to_bitstring(
                dice_vals=[1, 2, 3, 6] * 16, bitstring_len=128),
            "00111001" * 16)

        self.assertEqual(
            entropy.die_rolls_to_bitstring(
                dice_vals=[6] * 63 + [2], bitstring_len=128),
            "1" + "0" * 127)

        self.assertEqual(
            entropy.die_rolls_to_bitstring(
                dice_vals=[1] + [6] * 63, bitstring_len=128),
            "0" * 127 + "1")

    def test_die_rolls_to_bitstring_insufficient_entropy(self):
        """Try to get bitstring but with not enough die rolls"""
        with self.assertRaises(entropy.InsufficientEntropyError):
            entropy.die_rolls_to_bitstring(dice_vals=[1], bitstring_len=4)

        with self.assertRaises(entropy.InsufficientEntropyError):
            entropy.die_rolls_to_bitstring(dice_vals=[1, 2], bitstring_len=6)

    def test_die_rolls_to_bitstring_invalid(self):
        """Invoke function with invalid args"""
        #bad die rolls
        with self.assertRaises(ValueError):
            entropy.die_rolls_to_bitstring(dice_vals=[0, 1, 1], bitstring_len=2)
        with self.assertRaises(ValueError):
            entropy.die_rolls_to_bitstring(dice_vals=[7, 1, 1], bitstring_len=2)

        #rolls not a list or not int
        with self.assertRaises(TypeError):
            entropy.die_rolls_to_bitstring(dice_vals='1', bitstring_len=2)
        with self.assertRaises(TypeError):
            entropy.die_rolls_to_bitstring(dice_vals=['1'], bitstring_len=2)
        with self.assertRaises(TypeError):
            entropy.die_rolls_to_bitstring(dice_vals=[1], bitstring_len='2')

        #invalid length
        with self.assertRaises(ValueError):
            entropy.die_rolls_to_bitstring(dice_vals=[0], bitstring_len=0)
        with self.assertRaises(entropy.InsufficientEntropyError):
            entropy.die_rolls_to_bitstring(dice_vals=[], bitstring_len=2)

        #bitstring length should be a multiple of 2
        with self.assertRaises(ValueError):
            entropy.die_rolls_to_bitstring(dice_vals=[1], bitstring_len=1)

    def test_raw_str_to_binstring_valid(self):
        """Test valid conversion of raw strings to binary strings"""
        self.assertEqual(entropy.raw_str_to_binstring('\x00'), '00000000')
        self.assertEqual(entropy.raw_str_to_binstring('\x01'), '00000001')
        self.assertEqual(entropy.raw_str_to_binstring('\xff'), '11111111')
        self.assertEqual(entropy.raw_str_to_binstring('\xfe'), '11111110')

    def test_raw_str_to_binstring_invalid(self):
        """Test invalid args to function"""
        with self.assertRaises(TypeError):
            entropy.raw_str_to_binstring(1)

    def test_bits_to_bytes(self):
        self.assertEqual(entropy.bits_to_bytes(0), 0)
        for i in range(1, 9):
            self.assertEqual(entropy.bits_to_bytes(i), 1)
        self.assertEqual(entropy.bits_to_bytes(9), 2)

def _get_dice_rolls_of_len(n_dice_rolls):
    """Helper: Return all possible dice sequences for specified # of rolls"""
    if n_dice_rolls == 1:
        return [[1], [2], [3], [4], [5], [6]]
    roll_sequences = []
    for roll_val in [1, 2, 3, 4, 5, 6]:
        for recursive_dice_val in _get_dice_rolls_of_len(n_dice_rolls - 1):
            roll_series = [roll_val]
            roll_series.extend(recursive_dice_val)
            roll_sequences.append(roll_series)
    assert len(roll_sequences) == 6 ** n_dice_rolls
    return roll_sequences

def _dprint(msg):
    if ENABLE_DEBUG_PRINT:
        print "DEBUG: {0}".format(msg)
