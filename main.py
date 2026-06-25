import mmap
import asyncio
import sys
import time
from alcompress import ALcompress

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_large_file>")
        return

    target_file = sys.argv[1]
    
    # Pre-initialize the ALcompress engine once to keep the DLL in memory
alc = ALcompress(max_bits=16)
with open(target_file, "rb") as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        # Warmup
        alc.compress_persistent(mm)
        
        # Benchmark 10 iterations
        start_time = time.perf_counter()
        for _ in range(10):
            compressed = alc.compress_persistent(mm)
        duration = (time.perf_counter() - start_time) / 10
        print(f"Average C++ pure execution time: {duration*1000:.4f} ms")

    with open("production_data.alc", "wb") as f:
        f.write(compressed_bytes)

if __name__ == "__main__":
    asyncio.run(main())