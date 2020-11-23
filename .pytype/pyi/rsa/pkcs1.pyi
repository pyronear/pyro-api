# (generated with --quick)

import rsa.key
from typing import BinaryIO, Dict, Iterator, List, Type, Union

HASH_ASN1: Dict[str, bytes]
HASH_METHODS: Dict[str, Type[hashlib._Hash]]
__all__: List[str]
common: module
core: module
count: int
doctest: module
failures: int
hashlib: module
key: module
os: module
sys: module
tests: int
transform: module
typing: module

class CryptoError(Exception):
    __doc__: str

class DecryptionError(CryptoError):
    __doc__: str

class VerificationError(CryptoError):
    __doc__: str

def _find_method_hash(clearsig: bytes) -> str: ...
def _pad_for_encryption(message: bytes, target_length: int) -> bytes: ...
def _pad_for_signing(message: bytes, target_length: int) -> bytes: ...
def compute_hash(message: Union[bytes, BinaryIO], method_name: str) -> bytes: ...
def decrypt(crypto: bytes, priv_key: rsa.key.PrivateKey) -> bytes: ...
def encrypt(message: bytes, pub_key: rsa.key.PublicKey) -> bytes: ...
def find_signature_hash(signature: bytes, pub_key: rsa.key.PublicKey) -> str: ...
def sign(message: bytes, priv_key: rsa.key.PrivateKey, hash_method: str) -> bytes: ...
def sign_hash(hash_value: bytes, priv_key: rsa.key.PrivateKey, hash_method: str) -> bytes: ...
def verify(message: bytes, signature: bytes, pub_key: rsa.key.PublicKey) -> str: ...
def yield_fixedblocks(infile: BinaryIO, blocksize: int) -> Iterator[bytes]: ...
