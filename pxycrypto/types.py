from io import BufferedRandom, BufferedReader, BytesIO
from typing import Union

InputType = Union[bytearray, bytes, BytesIO, BufferedRandom, BufferedReader, str]
