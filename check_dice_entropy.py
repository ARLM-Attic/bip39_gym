"""Roll dice to tell if dice-to-binstring conversion is entropy biased

The tested function is: entropy.die_rolls_to_bitstring

There are 2 tests to run:

##########
# TEST 1 #
##########

Generate many random numbers and look for position-specific bias.

Uses random.SystemRandom:
https://docs.python.org/2/library/random.html#random.SystemRandom
"Class that uses the os.urandom() function for generating random numbers from
sources provided by the operating system."

##########
# TEST 2 #
##########

Try all possible dice rolls for various numbers of rolls and bit lengths and
ensure that the frequency of every bit position is equal.

"""
#Python Standard Library 2.7
from itertools import repeat
import random
import math

#PyPI modules
import progressbar #pip install progressbar2

#bip39_gym modules
import entropy #entropy.py

TEST2_MAX_BITS = 14
TEST2_MAX_ROLL_NUM = 7

ENABLE_DEBUG_PRINT = False

def rand_wrapper(n_bits):
    """Wrapper for randint and die_rolls_to_bitstring"""
    #doubled rolls to account for the average number of rolls dropped as 4 or 5
    n_rolls = int(math.ceil(entropy.die_rolls_per_bits(n_bits) * 2))
    enough_rolls = False
    rolls = []
    rand = random.SystemRandom()
    for _ in repeat(None, n_rolls):
        rolls.append(rand.randint(1, 6))
    while not enough_rolls:
        try:
            bitstring = entropy.die_rolls_to_bitstring(rolls, bitstring_len=n_bits)
            enough_rolls = True
        except entropy.InsufficientEntropyError:
            print "INFO: {0} rolls was insufficient. Adding another roll.".format(
                len(rolls))
            rolls.append(rand.randint(1, 6))
    return bitstring

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

def test_die_rolls_to_bitstring_entropy_uniformity():
    """Demonstrate uniformity of bits for all possible die rolls"""
    failures = []
    with progressbar.ProgressBar(max_value=TEST2_MAX_BITS * TEST2_MAX_ROLL_NUM) as prog_bar:
        for bitstring_len in range(2, TEST2_MAX_BITS + 1, 2):
            for rolls_num in range(1, TEST2_MAX_ROLL_NUM + 1):
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
                    if frequency != val:
                        msg = (("Failure for {0} bits and {1} rolls: Bit "
                                "results not uniform: {2} != {3}").format(
                                    bitstring_len, rolls_num, results_0, results_1))
                        print msg
                        failures.append(msg)
                for index, val in enumerate(results_1):
                    if frequency != val:
                        msg = (("Failure for {0} bits and {1} rolls: Bit results "
                                "not uniform: {2} != {3}").format(
                                    bitstring_len, rolls_num, results_0, results_1))
                        print msg
                        failures.append(msg)

                prog_bar.update(bitstring_len * rolls_num)
    if len(failures) == 0:
        print "Test #2: Passed. No failures."
    else:
        print "Test #2: Failed:"
        for failure in failures:
            print failure

def _dprint(msg):
    if ENABLE_DEBUG_PRINT:
        print "DEBUG: {0}".format(msg)

def _main():
    if not ENABLE_DEBUG_PRINT:
        entropy.ENABLE_DEBUG_PRINT = False
    n_bits = 256
    print("Test #1: Checking entropic soundness of dice-to-bits conversion by "
          "generating {n} bits {k} times...").format(
              n=n_bits, k=entropy.TEST_ITERATIONS)
    entropy.entropy_test(n_bits, rand_wrapper)

    print(("Test #2: Checking for uniformity of bits for bit lengths of 2 to "
           "{0} and beteween 1 roll and {1} rolls...").format(
               TEST2_MAX_BITS, TEST2_MAX_ROLL_NUM))
    test_die_rolls_to_bitstring_entropy_uniformity()

if __name__ == '__main__':
    _main()
