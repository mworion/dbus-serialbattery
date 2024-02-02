# -*- coding: utf-8 -*-
from seplos_utils import logger


def int_from_ascii(data: bytes, offset: int, signed=False, size=2) -> int:
    """
    converts a byte array to an integer
    """
    try:
        byte_chunk = bytes.fromhex(data.decode('ascii'))
        int_chunk = int.from_bytes(byte_chunk[offset: offset + size],
                                   byteorder='big', signed=signed)
    except Exception as e:
        logger.error(f'Error {e}')
        return 0

    return int_chunk


def is_valid_hex_string(data) -> bool:
    """
    check if ascii data is hex only
    """
    try:
        bytes.fromhex(data.decode('ascii'))
        return True
    except ValueError:
        return False


def is_valid_length(data, expected_length: int) -> bool:
    """
    check data has requested length (alarm: 98, stats: 168)
    """
    data_length = len(data)
    return data_length == expected_length


def is_valid_frame(self, data: bytes) -> bool:
    """
    checks if data contains a valid frame
    * minimum length is 18 Byte
    * checksum needs to be valid
    * also checks for error code as return code in cid2
    * not checked: lchksum
    """
    if len(data) < 18:
        return False

    checksum = self.get_checksum(data[1:-5])
    if checksum != self.int_from_2byte_hex_ascii(data, -5):
        return False

    cid2 = data[7:9]
    if cid2 != b"00":
        return False

    return True


def get_checksum(frame: bytes) -> int:
    """
    implements the Seplos checksum algorithm, returns 4 bytes
    """
    checksum = 0
    for b in frame:
        checksum += b
    checksum %= 0xFFFF
    checksum ^= 0xFFFF
    checksum += 1
    return checksum


def get_info_length(info: bytes) -> int:
    """
    implements the Seplos checksum for the info length
    """
    lenid = len(info)
    if lenid == 0:
        return 0

    lchksum = (lenid & 0xF) + ((lenid >> 4) & 0xF) + ((lenid >> 8) & 0xF)
    lchksum %= 16
    lchksum ^= 0xF
    lchksum += 1

    return (lchksum << 12) + lenid


def encode_cmd(address: int, cid2: int, info: bytes = b"01") -> bytes:
    """encodes a command sent to a battery (cid1=0x46)"""
    cid1 = 0x46
    info_length = get_info_length(info)
    frame = f'20{address:02X}{cid1:02X}{cid2:02X}{info_length:04X}'.encode()
    frame += info
    checksum = get_checksum(frame)
    encoded = b"~" + frame + "{:04X}".format(checksum).encode() + b"\r"
    return encoded
