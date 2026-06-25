import ctypes
import os

class ALcompress:
    def __init__(self, max_bits=16):
        self.max_bits = max_bits
        self.max_output_size = 10 * 1024 * 1024
        self.output_buffer = (ctypes.c_uint8 * self.max_output_size)()
        self.load_cpp_backend()
        self.ctx = self.cpp_lib.create_context()

    def load_cpp_backend(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(dir_path, "alcompress_core.dll")
        self.cpp_lib = ctypes.CDLL(lib_path)
        
        # Explicit definitions to prevent pointer overflow
        self.cpp_lib.create_context.restype = ctypes.c_void_p
        self.cpp_lib.destroy_context.argtypes = [ctypes.c_void_p]
        
        # Add batched interface
        self.cpp_lib.compress_enterprise_batched.argtypes = [
            ctypes.c_char_p, 
            ctypes.c_int, 
            ctypes.c_int, 
            ctypes.POINTER(ctypes.c_uint8), 
            ctypes.c_void_p,
            ctypes.c_int
        ]
        self.cpp_lib.compress_enterprise_batched.restype = ctypes.c_int

    def compress_persistent_batched(self, data_buffer, iterations=10) -> bytes:
        mv = memoryview(data_buffer)
        in_len = len(data_buffer)
        input_ptr = (ctypes.c_char * in_len).from_buffer(mv)
        
        # Single C++ call for all iterations
        size = self.cpp_lib.compress_enterprise_batched(
            input_ptr, in_len, self.max_bits, self.output_buffer, self.ctx, iterations
        )
        return bytes(self.output_buffer[:size])

    def __del__(self):
        if hasattr(self, 'cpp_lib') and hasattr(self, 'ctx') and self.ctx:
            self.cpp_lib.destroy_context(self.ctx)