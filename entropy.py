"""Fetch new entropy and mix with existing entropy

########################################
# Notes for computer-generated entropy #
########################################

Just use /dev/urandom https://www.2uo.de/myths-about-urandom/

#################
# Notes on Dice #
#################

1. As with the Ian Coleman tool, roles of 6 are "filtered" to a value of 0.

2. Converting from the base-6 of dice to base-2 poses a modulo bias issue. When you
roll N dice, you start to get modulo bias after N+1 of the least significant
bits. Rather than making the user roll N dice to get N bits of unbiased entropy,
we will simply make the number of rolls non-deterministic and throw out all
rolls of 4 or 5 and query the user for more rolls. This produces two bits of
unbiased entropy per roll (00 through 11).

No, you can't just avoid ending on a 4 or a 5 -- including such values anywhere
will bias the binary conversion so that bits are no longer uniformly distributed.

Also consequent to this, bits can only be selected in multiples of 2.
"""
#Python Standard Library 2.7
import os
import math
from itertools import repeat

#PyPI modules
import progressbar #pip install progressbar2

#bip39_gym modules
import bip39 #bip39.py

TEST_ITERATIONS = 10000

ENABLE_DEBUG_PRINT = True

ENTROPY_TEST_FAILURE = 0.05

IGNORED_BIASED_VALUES = set([4, 5])

class InsufficientEntropyError(Exception):
    """Not enough entropy provided for requested bit length"""
    pass

class InvalidBitLengthError(Exception):
    """Dice entropy can only be converted in 2*n bits"""

'''
def round_up(num, multiple):
    """Round up to nearest multiple"""
    _assert_int(num, multiple)
    return num if num % multiple == 0 else (num + multiple) - (num % multiple)
'''

def bits_to_bytes(n_bits):
    """Get the number of bytes that has at least n_bits

    Raises: TypeError, ValueError
    """
    _assert_non_negative_int(n_bits)
    return int(math.ceil(n_bits / 8.0))

def raw_str_to_binstring(raw_str):
    """Convert raw string to bit string"""
    if not isinstance(raw_str, str):
        raise TypeError
    return ''.join(format(ord(char), 'b').zfill(8) for char in raw_str)

def get_entropy(n_bits):
    """Get some bytes of entropy and return specified number of bits as bit string

    Raises: TypeError, ValueError
    """
    _assert_int(n_bits)

    n_bytes = bits_to_bytes(n_bits)
    rand = os.urandom(n_bytes)
    return raw_str_to_binstring(rand)[0:n_bits]

def xor(bitstring1, bitstring2):
    """Xor two bit strings to produce combined bit string
    Raises: ValueError, TypeError
    """
    if len(bitstring1) != len(bitstring2):
        raise ValueError
    if not isinstance(bitstring1, str) or not isinstance(bitstring2, str):
        raise TypeError

    result = ''
    for index, bit in enumerate(bitstring1):
        result += str(int(bit) ^ int(bitstring2[index]))
    assert len(result) == len(bitstring1)
    return result

def die_rolls_per_bits(n_bits):
    """Returns absolute min # of die to rolls to generate n bits of entropy

    Since 4's and 5's are bad rolls, 2/6 rolls will not work. This is not
    accounted for. On average, it will take result * 4/3 rolls.

    Raises: TypeError, ValueError
    """
    _assert_positive_int(n_bits)
    if n_bits % 2 != 0:
        raise ValueError('n_bits must be a multiple of 2') #TODO: or is it 4?

    #return int(math.ceil(math.log(2**n_bits, 6)))
    return math.ceil(n_bits/2.0)

def die_rolls_to_bitstring(dice_vals, bitstring_len):
    """Convert dice rolls to a bit string of min length.

    Args:
        dice_vals (List[int]): List of dice values in range 1 to 6
        bitstring_len (int): Number of bits that should be in bit string
            returned. Must be a multiple of 2. (TODO: or 4?)

    Consistent with Ian Coleman tool during entropy "filtering"
    https://github.com/iancoleman/bip39/blob/434caecd96740bbec488429026830b5ad24f628a/src/js/entropy.js#L73-L74

    but not with zero padding
    https://github.com/iancoleman/bip39/blob/434caecd96740bbec488429026830b5ad24f628a/src/js/entropy.js#L113-L122

    Raises:
        TypeError if args are wrong type
        ValueError if args are invalid int values
        InsufficientEntropyError if not enough die rolls provided
    """
    if not isinstance(dice_vals, list):
        raise TypeError
    _assert_positive_int(bitstring_len)
    if bitstring_len % 2 != 0:
        raise ValueError("bitstring_len must be a multiple of 2")

    absolute_min_rolls = die_rolls_per_bits(bitstring_len)

    if len(dice_vals) < absolute_min_rolls:
        raise InsufficientEntropyError()

    total = 0
    roll_num = 0
    accepted_rolls = 0

    for roll_val in dice_vals:
        _assert_int(roll_val)
        if roll_val < 1 or roll_val > 6:
            raise ValueError

        #filter value of '6' a la Ian Coleman tool
        filtered_roll_val = 0 if roll_val == 6 else roll_val

        if roll_val in IGNORED_BIASED_VALUES:
            continue

        accepted_rolls += 1

        #cacluate new value of dice rolls so far in base 4
        total += ((4**roll_num) * filtered_roll_val)

        roll_num += 1

    if accepted_rolls < absolute_min_rolls:
        raise InsufficientEntropyError()

    bitstring = bip39.dec2bin(dec=total, zero_padding=bitstring_len)

    if len(bitstring) < bitstring_len:
        raise ValueError("This condition should not be reachable")

    return bitstring[-bitstring_len:] #take first n bits generated

def entropy_test(n_bits, entropy_func):
    """Test function for bias in specific locations or ranges

    Side-effects: Display progress bar in console.

    Args:
        n_bits (int): Bits of entropy to be produced
        entropy_func (function): Entropy generator that accepts n_bits as arg
            and produces a bit string.
    """
    _assert_non_negative_int(n_bits)

    num_0 = [0] * n_bits
    num_1 = [0] * n_bits
    with progressbar.ProgressBar(max_value=TEST_ITERATIONS) as prog_bar:
        for iteration in range(0, TEST_ITERATIONS + 1):
            bitstring = entropy_func(n_bits)
            assert len(bitstring) == n_bits
            for index, val in enumerate(bitstring):
                if val == "0":
                    num_0[index] += 1
                else:
                    num_1[index] += 1

            prog_bar.update(iteration)

    fail = False
    worst_index = -1
    worst_high = 0.5
    for index in range(n_bits):
        tot = num_0[index] + num_1[index]
        pct_0 = 1.0 * num_0[index] / tot
        pct_1 = 1.0 * num_1[index] / tot
        if (pct_0 < 0.5 - ENTROPY_TEST_FAILURE or
                pct_0 > 0.5 + ENTROPY_TEST_FAILURE or
                pct_1 < 0.5 - ENTROPY_TEST_FAILURE or
                pct_1 > 0.5 + ENTROPY_TEST_FAILURE):
            fail = True
            print "FAILURE: {index}:\t0: {num_0} ({pct_0})\t1: {num_1} ({pct_1})".format(
                index=index, num_0=num_0[index], pct_0=pct_0, num_1=num_1[index],
                pct_1=pct_1)
        max_pct = max(pct_0, pct_1)
        if  max_pct > worst_high:
            worst_index = index
            worst_high = max_pct

    if not fail:
        print "Worst index was: {index} ({pct})".format(
            index=worst_index, pct=worst_high)

def _test_uniformity_256_bits():
    """Test get_entropy() for per-bit-position bias"""
    entropy_test(n_bits=256, entropy_func=get_entropy)

def _assert_int(*args):
    for arg in args:
        if not isinstance(arg, (int, long)):
            raise TypeError

def _assert_positive_int(*args):
    _assert_int(*args)
    for arg in args:
        if arg < 1:
            raise ValueError

def _assert_non_negative_int(*args):
    _assert_int(*args)
    for arg in args:
        if arg < 0:
            raise ValueError

def _dprint(_str):
    if ENABLE_DEBUG_PRINT:
        print "DEBUG: {0}".format(_str)

if __name__ == '__main__':
    _test_uniformity_256_bits()
