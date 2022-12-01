from typing import Union
from io import BytesIO, BufferedRandom, BufferedReader


InputType = Union[bytearray, bytes, BytesIO, BufferedRandom, BufferedReader, str]
