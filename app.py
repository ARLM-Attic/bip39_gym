"""Given an initial BIP39 mnemonic, accept dice rolls and XOR for new mnemonic

https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

Derivation from entropy bits to mnemonic:
1. Entropy should be between 128 and 256 bits, else warning
2. Let ENT be the lenth of ENTROPY in bits. Calculate checksum by taking
    ENT / 32 bits of the SHA256(entropy). Let the length of the checksum be CS.
3. Append the checksum to the end of entropy.
4. Split result into 11 bit pieces to index (0-based) a word from wordlist. Let
    MS be the length of the mnemonic sentence in words.

The following table describes the relation between the initial entropy length
    (ENT), the checksum length (CS) and the length of the generated mnemonic
    sentence (MS) in words:

CS = ENT / 32
MS = (ENT + CS) / 11

|  ENT  | CS | ENT+CS |  MS  |
+-------+----+--------+------+
|  128  |  4 |   132  |  12  |
|  160  |  5 |   165  |  15  |
|  192  |  6 |   198  |  18  |
|  224  |  7 |   231  |  21  |
|  256  |  8 |   264  |  24  |
"""

#Python Standard Library 2.7
import sys
from itertools import repeat
import math

#bi39_gym modules
import bip39 #bip39.py
import entropy #entropy.py

NORMAL_MNEMONIC_LEN = set([12, 15, 18, 21, 24])

def num_entropy_warnings(entropy_binstring, print_warning=True):
    """Returns how many non-fatal warnings are generated for the given entropy"""
    assert isinstance(entropy_binstring, basestring)
    warnings = 0
    entropy_int = int(entropy_binstring, 2)
    if entropy_int == 0:
        warnings += 1
        if print_warning:
            print "WARNING: Entropy is equal to zero! Bad entropy."
    else:
        if entropy_int & (entropy_int + 1) == 0:
            warnings += 1
            if print_warning:
                print "WARNING: Entropy is all ones in binary! Bad entropy."

    return warnings

def is_valid_entropy(entropy_binstring, print_error=True):
    """Determines whether entropy is properly formatted for BIP39

    Args:
        entropy_binstring (str): The entropy as binary string
        print_error (bool): Whether to print about fatal errors. Default: True
    """
    num_entropy_warnings(entropy_binstring)

    bit_len = len(entropy_binstring)

    if bit_len % bip39.ENT_MOD != 0:
        if print_error:
            print "ERROR: Entropy is not a multiple of 32 bits: {0} bits".format(
                bit_len)
        return False

    if bit_len < bip39.ENT_MIN:
        if print_error:
            print "ERROR: Entropy cannot be less than 128 bits: {0} bits".format(
                bit_len)
        return False

    if bit_len > bip39.ENT_MAX:
        if print_error:
            print "ERROR: Entropy cannot be more than 256 bits: {0} bits".format(
                bit_len)
        return False
    return True

def _is_canonical_mnemonic(words, wordset, print_error=True):
    for index, word in enumerate(words):
        if word not in wordset:
            if print_error:
                print "ERROR: word #{0} '{1}' not in canonical wordset!".format(
                    index + 1, word)
            return False
    return True

def _main():
    wordlist = bip39.get_wordlist()
    wordset = set(wordlist)

    assert len(wordlist) == 2048
    mnemonic = str(raw_input('Enter your BIP39 mnemonic in using the '
                             'canonical English dictionary: '))
    print "You entered: '{0}'".format(mnemonic)
    words = [str(word) for word in mnemonic.split(' ')]

    if not _is_canonical_mnemonic(words, wordset):
        sys.exit(1)

    if len(words) not in NORMAL_MNEMONIC_LEN:
        print "WARNING: Length of menonic you provided ({0}) is atypical.".format(
            len(words))

    binstring = None
    try:
        binstring = bip39.mnemonic2binstring(mnemonic)
    except bip39.FailedCheckSumError:
        print("ERROR: Mnemonic failed checksum. It may be an invalid BIP39 "
              "mnemonic -- be careful!!! Stopping.")
        sys.exit(1)

    print "Mnemonic as binary string: {0}".format(binstring)
    print "Note: The mnemonic passes a checksum test!"
    buf = "Re-deriving mnemonic from binary string for sanity check... {result}"
    mnemonic_calc = bip39.binstring2mnemonic(binstring)
    if mnemonic == mnemonic_calc:
        print buf.format(result="PASSED!")
    else:
        print buf.format(result="FAILED! Stopping. Please report issue on GitHub.")
        sys.exit(1)

    if is_valid_entropy(binstring):
        print "The mnemonic appears to conform to a valid bip39 entropy format."
    else:
        print("ERROR: The mnemonic doesn't appear to conform to bip39 entropy "
              "format -- be careful!!! Stopping.")
        sys.exit(1)

    urandom_rounds = int(raw_input(
        ('Enter the number of times entropy should be mixed in from '
         '/dev/urandom (0 to skip): ')))

    latest_entropy_binstring = binstring
    latest_mnemonic = mnemonic
    n_bits = len(binstring)

    for _ in repeat(None, urandom_rounds):
        new_entropy = entropy.get_entropy(n_bits)
        combined_entropy = entropy.xor(latest_entropy_binstring, new_entropy)
        combined_mnemonic = bip39.binstring2mnemonic(combined_entropy)
        print "===="
        print "old: {old_hex} {old_mnemonic}".format(
            old_hex=bip39.bin2hex(latest_entropy_binstring),
            old_mnemonic=latest_mnemonic)
        print "new: {new_hex} {new_mnemonic}".format(
            new_hex=bip39.bin2hex(new_entropy),
            new_mnemonic=bip39.binstring2mnemonic(new_entropy))
        print "xor: {xor_hex} {xor_mnemonic}".format(
            xor_hex=bip39.bin2hex(combined_entropy),
            xor_mnemonic=combined_mnemonic)

        print("Manually validate:\n"
              "\t1. Old hex and mnemonic match previous versions.\n"
              "\t2. Entering new and xor'd hex into alternative tool such as "
              "Ian Coleman bip39 tool derives to correct mnemonics.\n"
              "\t3. Confirm old XOR new = xor'd version hex char at a time.")

        latest_entropy_binstring = combined_entropy
        latest_mnemonic = combined_mnemonic

    min_estimated_rolls = int(math.ceil(
        entropy.die_rolls_per_bits(n_bits=n_bits) * (4.0/3)))

    entropy_gathered = False
    rolls_str = ''
    rolls = []
    while True:
        rolls_str = str(raw_input(
            ('Roll a die at least {minimum} times to provide entropy to mix '
             'in, with each roll represented by 1 to 6 and a space separating '
             'each roll: ').format(minimum=min_estimated_rolls)))
        rolls = [int(roll) for roll in rolls_str.split()]
        if len(rolls) >= min_estimated_rolls:
            break
    dice_bitstring = None
    while True:
        try:
            dice_bitstring = entropy.die_rolls_to_bitstring(
                dice_vals=rolls, bitstring_len=n_bits)
            print "Dice rolls as bitstring: {0}".format(dice_bitstring)
            break
        except entropy.InsufficientEntropyError:
            more_rolls_str = str(raw_input(
                ("More entropy needed. {num} rolls saved so far. Please enter "
                 "another roll: ").format(num=len(rolls))))
            rolls.extend([int(roll) for roll in more_rolls_str.split()])

    combined_entropy = entropy.xor(latest_entropy_binstring, dice_bitstring)
    combined_mnemonic = bip39.binstring2mnemonic(combined_entropy)
    print "===="
    print "old: {old_hex} {old_mnemonic}".format(
        old_hex=bip39.bin2hex(latest_entropy_binstring),
        old_mnemonic=latest_mnemonic)
    print "new: {new_hex} {new_mnemonic}".format(
        new_hex=bip39.bin2hex(dice_bitstring),
        new_mnemonic=bip39.binstring2mnemonic(dice_bitstring))
    print "xor: {xor_hex} {xor_mnemonic}".format(
        xor_hex=bip39.bin2hex(combined_entropy),
        xor_mnemonic=combined_mnemonic)

if __name__ == '__main__':
    _main()
