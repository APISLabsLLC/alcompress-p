import mmap
import sys
import time
from alcompress import ALcompress

def run_benchmark():
    if len(sys.argv) < 2: 
        print("Usage: python main.py <file>")
        return
        
    target_file = sys.argv[1]
    alc = ALcompress(max_bits=16)
    
    with open(target_file, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY)
        
        # 1. HEAVY WARMUP: Run several batches to prime the C++ cache
        for _ in range(5):
            alc.compress_persistent_batched(mm, iterations=10)
            
        # 2. BENCHMARK: Now measure the performance on a "hot" engine
        start_time = time.perf_counter()
        iterations = 100 # Increase iterations for higher precision
        alc.compress_persistent_batched(mm, iterations=iterations)
        duration = (time.perf_counter() - start_time) / iterations
        
        print(f"Average pure C++ execution time: {duration*1000:.4f} ms")
        mm.close()

if __name__ == "__main__":
    run_benchmark()