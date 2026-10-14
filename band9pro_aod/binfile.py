"""Strict reader/writer for the two-page 0x800/4 BIN layout used here."""
import re
import struct

PAIRS = tuple(p for p in range(0xB0, 0x158, 8) if p != 0x100)

def lua_asset(name: str, content: bytes) -> bytes:
    encoded = name.encode('utf-8')
    if not encoded or len(encoded) >= 256 or len(content) >= 0x1000000:
        raise ValueError('Resource name or payload is too large')
    return struct.pack('<I', len(content) | len(encoded) << 24) + bytes(16) + encoded + content

def read_asset(resource: bytes) -> tuple[str, bytes]:
    if len(resource) < 20:
        raise ValueError('Truncated Lua/PNG resource')
    value = struct.unpack_from('<I', resource)[0]
    size, name_size = value & 0xFFFFFF, value >> 24
    if resource[4:20] != bytes(16) or len(resource) != 20 + name_size + size:
        raise ValueError('Invalid Lua/PNG resource lengths')
    return resource[20:20 + name_size].decode('utf-8'), resource[20 + name_size:]

class Watchface:
    def __init__(self, blob: bytes):
        if len(blob) < 0x158 or len(blob) > 64 * 1024 * 1024 or blob[:4] != bytes.fromhex('5aa53412'):
            raise ValueError('Unsupported or truncated watchface BIN')
        if struct.unpack_from('<I', blob, 0x10)[0] != 0x800 or struct.unpack_from('<HH', blob, 0x1C) != (2, 4):
            raise ValueError('Only the known two-page 0x800/4 layout is supported')
        preview = struct.unpack_from('<I', blob, 0x20)[0]
        if preview != struct.unpack_from('<I', blob, 0xAC)[0] or not 0x158 <= preview < len(blob):
            raise ValueError('Invalid preview location')
        self.header = bytes(blob[:0x158])
        self.sections: dict[int, list[tuple[int, bytes]]] = {}
        ranges, keys = [], set()
        for pair in PAIRS:
            count, table = struct.unpack_from('<II', blob, pair)
            if count > 4096 or not 0x158 <= table or table + 16 * count > preview:
                raise ValueError('Invalid resource index bounds')
            rows = []
            for index in range(count):
                key, zero, start, size = struct.unpack_from('<4I', blob, table + index * 16)
                if zero or start < preview or start + size > len(blob):
                    raise ValueError('Resource extends beyond BIN')
                if key >> 24:
                    if key in keys:
                        raise ValueError('Duplicate typed resource ID')
                    keys.add(key)
                ranges.append((start, start + size))
                rows.append((key, bytes(blob[start:start + size])))
            self.sections[pair] = rows
        if not ranges:
            raise ValueError('No resources')
        ranges.sort()
        if any(end > next_start for (_, end), (next_start, _) in zip(ranges, ranges[1:])):
            raise ValueError('Overlapping resource payloads')
        self.preview = bytes(blob[preview:ranges[0][0]])

    def pack(self, face_id: str, title: str) -> bytes:
        if not re.fullmatch(r'[0-9]{9}', face_id):
            raise ValueError('Use a new nine-digit face ID')
        name = title.encode('utf-8')
        if not name or len(name) > 63 or '\n' in title or '\0' in title:
            raise ValueError('Title must fit the 64-byte UTF-8 field')
        header = bytearray(self.header)
        header[0x28:0x60] = face_id.encode().ljust(0x38, b'\0')
        header[0x68:0xA8] = name.ljust(0x40, b'\0')
        preview_offset = 0x158 + 16 * sum(len(v) for v in self.sections.values())
        struct.pack_into('<I', header, 0x20, preview_offset)
        struct.pack_into('<I', header, 0xAC, preview_offset)
        indexes, data = bytearray(), bytearray(self.preview)
        for pair in PAIRS:
            section = self.sections[pair]
            struct.pack_into('<II', header, pair, len(section), 0x158 + len(indexes))
            for key, content in section:
                indexes.extend(struct.pack('<4I', key, 0, preview_offset + len(data), len(content)))
                data.extend(content)
        result = bytes(header + indexes + data)
        Watchface(result)
        return result
