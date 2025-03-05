import struct
import numpy as np
from pathlib import Path

class GGUFWriter:
    HEADER_FORMAT = [
        ("magic", "I", 0x46554747),  # GGUF
        ("version", "I", 1),
        ("tensor_count", "Q", 0),
        ("kv_count", "Q", 0)
    ]
    
    def __init__(self, output_path: str):
        self.file = open(output_path, "wb")
        self.tensor_offset = 0
        self._write_header_placeholder()
        
    def _write_header_placeholder(self):
        header_size = sum(
            struct.calcsize(fmt) for _, fmt, _ in self.HEADER_FORMAT
        )
        self.file.write(b"\x00" * header_size)
        self.tensor_offset = header_size
        
    def add_tensor(self, name: str, tensor: np.ndarray, dtype: str, shape: tuple):
        # Convert tensor to bytes
        if dtype == "F32":
            data = tensor.astype(np.float32).tobytes()
        elif dtype.startswith("Q"):
            data = tensor.tobytes()
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")
        
        # Write tensor metadata
        self._write_string(name)
        self._write_uint32(len(shape))
        for dim in reversed(shape):
            self._write_uint64(dim)
        self._write_string(dtype)
        self._write_uint64(self.tensor_offset + self.file.tell() + 8)
        self._write_uint64(len(data))
        
        # Write tensor data
        self.file.write(data)
        
    def finalize(self, metadata: dict):
        # Seek back and write final header
        self.file.seek(0)
        for name, fmt, value in self.HEADER_FORMAT:
            if name == "tensor_count":
                value = self.tensor_count
            elif name == "kv_count":
                value = len(metadata)
            self.file.write(struct.pack(f"<{fmt}", value))
        
        # Write metadata
        for key, value in metadata.items():
            self._write_string(key)
            self._write_string(str(value))
            
    def _write_string(self, s: str):
        self.file.write(struct.pack("<Q", len(s)))
        self.file.write(s.encode("utf-8"))
        
    def _write_uint32(self, n: int):
        self.file.write(struct.pack("<I", n))
        
    def _write_uint64(self, n: int):
        self.file.write(struct.pack("<Q", n))
        
    def close(self):
        self.file.close()