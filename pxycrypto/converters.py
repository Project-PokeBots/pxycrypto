from __future__ import annotations

from contextlib import suppress
from pathlib import PurePath
from re import compile, match

from .types import InputType

if __import__("typing", fromlist=["TYPE_CHECKING"]).TYPE_CHECKING:
    from io import BufferedRandom, BufferedReader, BytesIO
    from typing import Optional, Union

try:
    from httpx import get

    HTTPX_PRESENT = True
except ModuleNotFoundError:
    HTTPX_PRESENT = False

url_pattern = compile(
    r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def from_bytes(data: bytes) -> bytearray:
    return bytearray(data)


def from_io(data: Union[BytesIO, BufferedRandom, BufferedReader]) -> bytearray:
    data.seek(0)
    return bytearray(data.read())


def pass_bytearray(data: bytearray) -> bytearray:
    return data


def from_url(data: str) -> Optional[bytearray]:
    if not match(pattern=url_pattern, string=data):
        return None
    if not HTTPX_PRESENT:
        return None
    with suppress(Exception):
        return bytearray(get(data).content)
    return None


def from_path(data: str) -> Optional[bytearray]:
    with suppress(Exception):
        p = PurePath(data)
        with open(str(p), "rb") as f:
            return bytearray(f.read())
    return None


str_converters = [from_url, from_path]


def from_str(data: str) -> Optional[bytearray]:
    for fun in str_converters:
        if res := fun(data):
            return res
    return None


converters = {
    "bytes": from_bytes,
    "BufferedRandom": from_io,
    "BufferedReader": from_io,
    "BytesIO": from_io,
    "bytearray": pass_bytearray,
    "str": from_str,
}


def ensure_bytearray(data: InputType) -> Optional[bytearray]:
    return converters[data.__class__.__name__](data)
