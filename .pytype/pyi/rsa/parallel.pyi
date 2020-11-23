# (generated with --quick)

import multiprocessing.connection
from typing import List, Type

Connection: Type[multiprocessing.connection.Connection]
__all__: List[str]
count: int
doctest: module
failures: int
mp: module
rsa: module
tests: int

def _find_prime(nbits: int, pipe: multiprocessing.connection.Connection) -> None: ...
def getprime(nbits: int, poolsize: int) -> int: ...
