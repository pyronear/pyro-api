# (generated with --quick)

import toml.decoder
import toml.encoder
from typing import Any, Type

TomlArraySeparatorEncoder: Type[toml.encoder.TomlArraySeparatorEncoder]
TomlDecodeError: Type[toml.decoder.TomlDecodeError]
TomlDecoder: Type[toml.decoder.TomlDecoder]
TomlEncoder: Type[toml.encoder.TomlEncoder]
TomlNumpyEncoder: Type[toml.encoder.TomlNumpyEncoder]
TomlPathlibEncoder: Type[toml.encoder.TomlPathlibEncoder]
TomlPreserveCommentDecoder: Type[toml.decoder.TomlPreserveCommentDecoder]
TomlPreserveCommentEncoder: Type[toml.encoder.TomlPreserveCommentEncoder]
TomlPreserveInlineDictEncoder: Type[toml.encoder.TomlPreserveInlineDictEncoder]
__version__: str
_spec_: str
decoder: module
encoder: module

def dump(o, f, encoder = ...) -> Any: ...
def dumps(o, encoder = ...) -> str: ...
def load(f, _dict = ..., decoder = ...) -> Any: ...
def loads(s, _dict = ..., decoder = ...) -> Any: ...
