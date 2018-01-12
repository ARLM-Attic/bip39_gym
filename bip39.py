"""BIP39 functions"""

#Python Standard Library 2.7
import hashlib

#BIP 39: "The mnemonic must encode entropy in a multiple of 32 bits"
ENT_MOD = 32

#BIP 39: "The allowed size of ENT is 128-256 bits"
ENT_MIN = 128
ENT_MAX = 256

WORDLIST_PIECE_BITS = 11

WORDLIST_FILE = 'data/english.txt'

class WordNotDefinedAtIndexError(Exception):
    """There is no English word defined at specified index"""
    pass

class InvalidWordError(Exception):
    """A word does not match the English BIP39 dictionary"""
    pass

class InvalidIntValueError(Exception):
    """An expected int argument has wrong value or type"""
    pass

class FailedCheckSumError(Exception):
    """While decoding a mnemonic, the checksum failed"""
    pass

def get_wordlist():
    """Get BIP39 English wordlist"""
    with open(WORDLIST_FILE) as english:
        wordlist = english.readlines()
        return [word.strip() for word in wordlist]

def dec2bin(dec, zero_padding=0):
    """Convert zero or positive integer to binary string

    Reference: https://stackoverflow.com/a/699891
    """
    if not isinstance(dec, (int, long)):
        raise InvalidIntValueError()
    if dec < 0:
        raise InvalidIntValueError()
    binstring = "{0:b}".format(dec)
    if zero_padding > 0:
        binstring = binstring.zfill(zero_padding)
    return binstring

def hex2bin(hex_str):
    """Convert hex representation of entropy to binary string representation

    Reference: https://stackoverflow.com/a/8445492
    """
    assert isinstance(hex_str, basestring)
    return '{0:b}'.format(int(hex_str, 16)).zfill(len(hex_str) * 4)

def bin2hex(binstring):
    """Convert binary string to hex string.

    If the binstring provided is not length mod 4, 0 left padding is assumed.

    Reference: https://stackoverflow.com/a/2072366
    """
    if not isinstance(binstring, basestring):
        raise ValueError
    #return n_bits / 8 if n_bits % 8 == 0 else (n_bits / 8) + 1
    n_bits = len(binstring)
    hexlen = n_bits / 4 if n_bits % 4 == 0 else (n_bits / 4) + 1
    hex_str = hex(int(binstring, 2))[2:].zfill(hexlen) #remove leading 0x
    return hex_str[:-1] if hex_str.endswith('L') else hex_str #trailing "L"

def decode_binary_string(binstring):
    """Convert binary string to raw data string

    Reference: https://stackoverflow.com/a/40559005
    """
    return ''.join(chr(int(binstring[i*8:i*8+8], 2)) for i in range(len(binstring)//8))

def checksum(entropy_binstring):
    """Compute BIP39 checksum from entropy expressed as binary string"""
    hasher = hashlib.sha256()
    data = decode_binary_string(entropy_binstring)
    hasher.update(data)
    checksum_hex = hasher.hexdigest()
    checksum_bin = hex2bin(checksum_hex)

    ent = len(entropy_binstring) / ENT_MOD
    return checksum_bin[0:ent]

def binstring2word_index(binstring):
    """Obtain indices in wordlist from binary string

    BIP39: Next, these concatenated bits are split into groups of 11 bits, each
    encoding a number from 0-2047, serving as an index into a wordlist
    """
    indices = [int( #interpret chunk as binary string and covert to int
        binstring[i*WORDLIST_PIECE_BITS: #take chunk of 11 bits
                  (i+1)*WORDLIST_PIECE_BITS],
        2) for i in range(len(binstring)//WORDLIST_PIECE_BITS)]
    return indices

def word_index2binstring(index):
    """Obtain 11-bit string from word index in [0, 2047]

    Raises: WordNotDefinedAtIndexError
    """
    if index < 0 or index > 2047:
        raise WordNotDefinedAtIndexError()
    return dec2bin(index, zero_padding=11)

def get_word_from_index(index):
    """Get the BIP39 word from the English wordlist at specified 0-based index

    Raises: WordNotDefinedAtIndexError
    """
    if index < 0 or index > 2047:
        raise WordNotDefinedAtIndexError()
    return get_wordlist()[index]

def get_index_from_word(word, wordlist=None):
    """Get the 0-based index of a word in English wordlist

    Raises: InvalidWordError
    """
    if wordlist is None:
        wordlist = get_wordlist()
    for index, word_comp in enumerate(wordlist):
        if word_comp == word:
            return index
    raise InvalidWordError()

def get_mnemonic(indices):
    """Given a list of word indices, get full mnemonic from English wordlist

    Raises:
        ValueError: if empty list
        WordNotDefinedAtIndexError: If index in list is out of range
    """
    if len(indices) == 0:
        raise ValueError
    return " ".join([get_word_from_index(index) for index in indices])

def get_indices(mnemonic):
    """Given a mnemonic sentence, get the word indices for the English wordlist

    Raises:
        ValueError: If empty bin_string
        InvalidWordError: If a word is not found in the dictionary
    """
    if len(mnemonic) == 0:
        raise ValueError
    return [get_index_from_word(word) for word in mnemonic.split()]

def mnemonic2binstring(mnemonic, print_warning=True):
    """Convert complete mnemonic setence to binstring and verify checksum.

    The returned value will not include the checksum.

    Raises:
    ValueError: If empty mnemonic or malformatted word
    InvalidWordError: If a word is not found in the dictionary
    FailedCheckSumError
    """
    if mnemonic == '':
        raise ValueError
    binstring = ''
    wordlist = get_wordlist()
    for word in mnemonic.split():
        index = get_index_from_word(word, wordlist=wordlist)
        binstring += word_index2binstring(index)

    if len(binstring) % 1.03125 != 0:
        if print_warning:
            print "WARNING: Length of decoded mnemonic inconsistent with proper length!"

    ent = int(len(binstring) / 1.03125)
    raw_entropy = binstring[0:ent]
    checksum_val = binstring[ent:]
    computed_checksum = checksum(raw_entropy)
    if checksum_val != computed_checksum:
        raise FailedCheckSumError()

    return raw_entropy

def binstring2mnemonic(entropy_bin):
    """Convert raw entropy as binary string (sans checksum) to bip39 mnemonic"""
    checksum_bin = checksum(entropy_bin)
    combined_bin = "{0}{1}".format(entropy_bin, checksum_bin)
    indices = binstring2word_index(combined_bin)
    mnemonic = get_mnemonic(indices)
    return mnemonic
