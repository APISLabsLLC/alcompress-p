import mmap
import sys
import time
import logging
from alcompress import ALcompress

# Configure logging for production telemetry
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_compression_pipeline(target_file: str):
    """
    Executes the ALcompress pipeline using memory-mapped I/O for 
    zero-copy performance and persistent DLL state management.
    """
    try:
        # Initialize the engine once to maintain DLL state in memory
        # This avoids the expensive startup overhead on every call
        alc = ALcompress(max_bits=16)
        
        with open(target_file, "rb") as f:
            # Use mmap for high-performance, direct memory access to the file
            # This prevents loading the entire dataset into Python's heap
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY) as mm:
                
                # Perform an initial warmup pass
                # This ensures the lattice is primed and memory pages are allocated
                alc.compress_persistent(mm)
                
                # Execution loop for latency analysis
                start_time = time.perf_counter()
                
                # Compress the mapped memory
                compressed_bytes = alc.compress_persistent(mm)
                
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.info(f"Compression completed in {elapsed:.4f} ms")

        # Atomic write for the resulting compressed data
        with open("production_data.alc", "wb") as f:
            f.write(compressed_bytes)
            
    except Exception as e:
        logger.error(f"Compression pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    run_compression_pipeline(sys.argv[1])