from __future__ import annotations

from pathlib import PurePath

from .converters import ensure_bytearray
from .enums import enums
from .types import InputType

if __import__("typing", fromlist=["TYPE_CHECKING"]).TYPE_CHECKING:
    from io import BufferedRandom, BufferedReader, BytesIO
    from typing import Union


class Pokecrypto(object):
    def __init__(self, data: InputType) -> None:
        self.data = ensure_bytearray(data) or bytearray()

    def __repr__(self) -> str:
        return "\n".join(
            [
                f"encrypted: {str(self.is_encrypted())}",
                f"ec: {str(self.ec())}",
                self.bytes().hex(),
            ]
        )

    def __crypt__(self, seed: int, start: int, end: int) -> None:
        i = start
        while i < end:
            seed = seed * 0x41C64E6D + 0x00006073
            self.data[i] ^= (seed >> 16) & 0xFF
            i += 1
            self.data[i] ^= (seed >> 24) & 0xFF
            i += 1

    def __cryptPKM__(self, seed: int) -> None:
        self.__crypt__(seed, 8, 0x148)
        if len(self.data) == 0x158:
            self.__crypt__(seed, 0x148, 0x158)

    def __shuffle__(self, sv: int) -> None:
        idx = 4 * sv
        sdata = bytearray(self.data[:])
        for block in range(4):
            ofs = enums["crypto"]["bp"][idx + block]
            self.data[8 + 0x50 * block : 8 + 0x50 * (block + 1)] = sdata[
                8 + 0x50 * ofs : 8 + 0x50 * (ofs + 1)
            ]

    def __setushort(self, offset: int, p: int) -> None:
        self.data[offset : offset + 2] = (p).to_bytes(2, byteorder="little")

    def __getushort(self, offset: int) -> int:
        return int.from_bytes(self.data[offset : offset + 2], byteorder="little")

    def __getuint(self, offset: int) -> int:
        return int.from_bytes(self.data[offset : offset + 4], byteorder="little")

    def __calChecksum(self) -> int:
        chk = 0
        for i in range(8, 0x148, 2):
            chk += self.__getushort(i)
            chk &= 0xFFFF
        return chk

    def is_encrypted(self) -> bool:
        return self.data[0x70] != 0 and self.data[0xC0] != 0

    def __refreshChecksum(self) -> None:
        self.__setushort(0x6, self.__calChecksum())

    def ec(self) -> int:
        return self.__getuint(0x0)

    def encrypt(self) -> Pokecrypto:
        if self.is_encrypted():
            return self
        self.__refreshChecksum()
        seed = self.ec()
        sv = (seed >> 13) & 0x1F
        self.__shuffle__(enums["crypto"]["bpi"][sv])
        self.__cryptPKM__(seed)
        return self

    def decrypt(self) -> Pokecrypto:
        if not self.is_encrypted():
            return self
        shuffle_order = (self.ec() >> 13) & 0x1F
        self.__cryptPKM__(self.ec())
        self.__shuffle__(shuffle_order)
        return self

    def save(self, path: str) -> None:
        with open(str(PurePath(path)), "wb+") as f:
            f.write(bytes(self.data))

    def bytes(self) -> bytes:
        return bytes(self.data)
