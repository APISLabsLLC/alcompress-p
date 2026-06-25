import ctypes
import os
import sys

class ALcompress:
    def __init__(self, max_bits=16):
        self.max_bits = max_bits
        self.max_output_size = 10 * 1024 * 1024 
        self.output_buffer = (ctypes.c_uint8 * self.max_output_size)()
        self.load_cpp_backend()

    def load_cpp_backend(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(dir_path, "alcompress_core.dll" if sys.platform.startswith("win") else "alcompress_core.so")
        
        try:
            self.cpp_lib = ctypes.CDLL(lib_path)
            self.cpp_lib.compress_enterprise.argtypes = [
                ctypes.c_void_p,             # input_data
                ctypes.c_int,                # input_length
                ctypes.c_int,                # max_bits
                ctypes.POINTER(ctypes.c_uint8) # output_buffer
            ]
            self.cpp_lib.compress_enterprise.restype = ctypes.c_int
            self.has_cpp = True
        except Exception as e:
            self.has_cpp = False
            raise RuntimeError(f"C++ engine failed to load: {e}")

    def compress_persistent(self, data_buffer) -> bytes:
        if not self.has_cpp:
            raise RuntimeError("Enterprise mode requires the compiled C++ binary.")

        in_len = len(data_buffer)
        
        if in_len + 64 > self.max_output_size:
            self.max_output_size = in_len + 64
            self.output_buffer = (ctypes.c_uint8 * self.max_output_size)()

        # Use buffer_info() to get the raw memory address, bypassing Python's buffer checks
        addr, _ = data_buffer.buffer_info()
        data_ptr = ctypes.c_void_p(addr)
        
        compressed_size = self.cpp_lib.compress_enterprise(
            data_ptr, in_len, self.max_bits, self.output_buffer
        )
        
        return bytes(self.output_buffer[:compressed_size])