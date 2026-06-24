import ctypes
import os
import sys

class ALcompress:
    def __init__(self, max_bits=16):
        self.max_bits = max_bits
        self.load_cpp_backend()

    def load_cpp_backend(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(dir_path, "alcompress_core.dll" if sys.platform.startswith("win") else "alcompress_core.so")
        
        try:
            self.cpp_lib = ctypes.CDLL(lib_path)
            self.cpp_lib.compress_enterprise.argtypes = [
                ctypes.c_char_p,          # input_data
                ctypes.c_int,             # input_length
                ctypes.c_int,             # max_bits
                ctypes.POINTER(ctypes.c_uint8) # output_bytes (Pre-allocated)
            ]
            self.cpp_lib.compress_enterprise.restype = ctypes.c_int
            self.has_cpp = True
        except Exception as e:
            print(f"⚠️ C++ failed to load: {e}")
            self.has_cpp = False

    def compress_to_bytes(self, raw_bytes: bytes) -> bytes:
        # FIX: Remove the .encode() allocation completely. 
        # Python passes the direct underlying C-pointer of the bytes object safely.
        in_len = len(raw_bytes)
        
        if not self.has_cpp:
            raise RuntimeError("Enterprise mode requires the compiled C++ binary.")

        # Rigid Head safety margin allocation
        output_buffer = (ctypes.c_uint8 * (in_len + 64))()
        
        # C++ crunches text AND packs bits concurrently
        compressed_size = self.cpp_lib.compress_enterprise(
            raw_bytes, in_len, self.max_bits, output_buffer
        )
        
        # Slice out the exact resulting compressed bytes
        return bytes(output_buffer[:compressed_size])