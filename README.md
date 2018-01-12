# bip39-gym

**!!!STOP: This tool isn't production ready, and hasn't undergone rigorous review.!!!**

This tool strengthens existing BIP39 mnemonic phrases for the english wordlist.

Example use case: You've generated a BIP39 mnemonic using a hardware wallet, and you want to have a mnemonic that is _at least_ as strong as the one provided by the hardware wallet.

This tool will mix in additional sources of entropy, including the operating system's `os.urandom` generator, and dice. Each additional source of entropy is XOR'd with the previous to ensure that entropy is not degraded.

This tool should be run on trusted equipment, preferably offline hardware that is physically isolated from typical methods of leaking (power, wifi/bluetooth, microphone/speakers, ethernet, TEMPEST, etc.)

## Example usage

```
$ python app.py
Enter your BIP39 mnemonic in using the canonical English dictionary: quantum act accuse view secret bounce shaft tag repair drive horror weekend wing attend grit
You entered: 'quantum act accuse view secret bounce shaft tag repair drive horror weekend wing attend grit'
Mnemonic as binary string: 1010111101000000010011000000011011111001111111000010100000110100111100010011111011101001101101101000100001101001101101101111110010001111101110100001110100011001
Note: The mnemonic passes a checksum test!
Re-deriving mnemonic from binary string for sanity check... PASSED!
The mnemonic appears to conform to a valid bip39 entropy format.
Enter the number of times entropy should be mixed in from /dev/urandom (0 to skip): 3
====
old: af404c06f9fc2834f13ee9b68869b6fc8fba1d19 quantum act accuse view secret bounce shaft tag repair drive horror weekend wing attend grit
new: f5f0dfdd0fa353367b1221868950117ac18bd709 vote manage warrior butter cry open unable during make enhance affair void board twist caution
xor: 5ab093dbf65f7b028a2cc8300139a7864e31ca10 follow loyal want uncover waste life chunk october copy antenna hazard arrive toast topic drama
Manually validate:
	1. Old hex and mnemonic match previous versions.
	2. Entering new and xor'd hex into alternative tool such as Ian Coleman bip39 tool derives to correct mnemonics.
	3. Confirm old XOR new = xor'd version hex char at a time.
====
old: 5ab093dbf65f7b028a2cc8300139a7864e31ca10 follow loyal want uncover waste life chunk october copy antenna hazard arrive toast topic drama
new: f8cb450e0b103b19c281524a2664a1304ec0ea9a web focus drum bike admit mind anxiety clean enforce creek choose gauge ugly inspire hamster
xor: a27bd6d5fd4f401b48ad9a7a275d06b600f1208a pen team rely whisper village asset cargo rebuild kick depend double hire audit motion close
Manually validate:
	1. Old hex and mnemonic match previous versions.
	2. Entering new and xor'd hex into alternative tool such as Ian Coleman bip39 tool derives to correct mnemonics.
	3. Confirm old XOR new = xor'd version hex char at a time.
====
old: a27bd6d5fd4f401b48ad9a7a275d06b600f1208a pen team rely whisper village asset cargo rebuild kick depend double hire audit motion close
new: a61704ff0391bdbd77188b3658eb4381df93488f plastic return divert already bridge team symbol badge curve shrug special admit weird picture disagree
xor: 46cd22afedefda63fb5114c7fb64537df626805 afford grief melt world used spread yard peasant erase world mule hurry wage cross bird
Manually validate:
	1. Old hex and mnemonic match previous versions.
	2. Entering new and xor'd hex into alternative tool such as Ian Coleman bip39 tool derives to correct mnemonics.
	3. Confirm old XOR new = xor'd version hex char at a time.
Roll a die at least 107 times to provide entropy to mix in, with each roll represented by 1 to 6 and a space separating each roll: 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 3 6 1 2 4 3
Dice rolls as bitstring: 0011100100111001001110010011100100111001001110010011100100111001001110010011100100111001001110010011100100111001001110010011100100111001001110010011100100111001
====
old: 46cd22afedefda63fb5114c7fb64537df626805 afford grief melt world used spread yard peasant erase world mule hurry wage cross bird
new: 3939393939393939393939393939393939393939 decrease six exact include near orient top cheese decrease six exact include near orient tone
xor: 3d55eb13c7e7c49f068c2875468f7c0ee65b513c diary quantum shaft more labor exhibit boss lunar inspire crucial tenant build grant possible veteran
```

## Notes on dice

This tool's method of deriving bits of entropy from dice roll differs from that of Ian Coleman's bip39 tool. Any base-6 number of m digits converted to a base-2 number of n bits will introduce modulo bias after the m'th bit, making it unsuitable as a source of entropy. Therefore, this tool ignores all dice rolls of 4 or 5 and treats rolls of 1, 2, 3 or 6 as base-4.

## Development

### Running tests

* Requires Python 2.7

```  
make test
python -m unittest discover -p "test*.py"
....Loaded vector data from data/random_vectors.json
.Loaded vector data from data/random_vectors.json
.Loaded vector data from data/random_vectors.json
.Loaded vector data from data/random_vectors.json
.Loaded vector data from data/vectors.json
..................................
----------------------------------------------------------------------
Ran 42 tests in 0.637s

OK
```

### Benchmarking entropy generator that uses `os.random` for per-index bias

```
$ python entropy.py
100% (10000 of 10000) |#########################################################################################################################| Elapsed Time: 0:00:00 Time: 0:00:00
Worst index was: 126 (0.514648535146)
```

### Benchmarking dice rolls-to-bit string conversion for per-index bias
```
$ python check_dice_entropy.py
Test #1: Checking entropic soundness of dice-to-bits conversion by generating 256 bits 10000 times...
100% (10000 of 10000) |#########################################################################################################################| Elapsed Time: 0:00:16 Time: 0:00:16
Worst index was: 196 (0.516348365163)
Test #2: Checking for uniformity of bits for bit lengths of 2 to 14 and beteween 1 roll and 7 rolls...
100% (98 of 98) |###############################################################################################################################| Elapsed Time: 0:00:39 Time: 0:00:39
Test #2: Passed. No failures.
```
