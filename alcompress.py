import ctypes
import os
import sys

class ALcompress:
    def __init__(self, max_bits=16):
        self.max_bits = max_bits
        # Pre-allocate a 10MB buffer for compression output (expandable if needed)
        self.max_output_size = 10 * 1024 * 1024 
        self.output_buffer = (ctypes.c_uint8 * self.max_output_size)()
        self.load_cpp_backend()

    def load_cpp_backend(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(dir_path, "alcompress_core.dll" if sys.platform.startswith("win") else "alcompress_core.so")
        
        try:
            self.cpp_lib = ctypes.CDLL(lib_path)
            self.cpp_lib.compress_enterprise.argtypes = [
                ctypes.c_char_p,              # input_data
                ctypes.c_int,                 # input_length
                ctypes.c_int,                 # max_bits
                ctypes.POINTER(ctypes.c_uint8) # output_buffer
            ]
            self.cpp_lib.compress_enterprise.restype = ctypes.c_int
            self.has_cpp = True
        except Exception as e:
            print(f"⚠️ C++ failed to load: {e}")
            self.has_cpp = False

    def compress_persistent(self, data_buffer) -> bytes:
        """
        Processes memory-mapped data using a persistent, pre-allocated buffer.
        """
        if not self.has_cpp:
            raise RuntimeError("Enterprise mode requires the compiled C++ binary.")

        in_len = len(data_buffer)
        
        # Ensure our persistent buffer is large enough; if not, reallocate
        if in_len + 64 > self.max_output_size:
            self.max_output_size = in_len + 64
            self.output_buffer = (ctypes.c_uint8 * self.max_output_size)()

        # Get the direct memory pointer from the mmap object
        data_ptr = (ctypes.c_char * in_len).from_buffer(data_buffer)
        
        # Execute C++ core
        compressed_size = self.cpp_lib.compress_enterprise(
            data_ptr, in_len, self.max_bits, self.output_buffer
        )
        
        # Return a copy of the slice (or memoryview if you want zero-copy return)
        return bytes(self.output_buffer[:compressed_size])