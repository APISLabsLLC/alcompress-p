import asyncio
import os
import sys
import time
from alcompress import ALcompress

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_large_file>")
        return

    target_file = sys.argv[1]
    
    # print(f"Reading: {target_file}...")
    # FIX: Read as raw binary bytes instead of a text string
    with open(target_file, "rb") as f:
        payload = f.read()

    orig_size = len(payload)
    # print(f"📋 Original Data Size: {orig_size / (1024*1024):.2f} MB")

    alc = ALcompress(max_bits=16)

    # Time the engine processing speed
    start_time = time.perf_counter()
    
    # Offload execution entirely to the optimized C++ backend thread
    compressed_payload_bytes = await asyncio.to_thread(alc.compress_to_bytes, payload)
    
    duration = time.perf_counter() - start_time
    throughput = (orig_size / (1024 * 1024)) / duration

    # Write output stream directly (Rigid Head is already embedded inside the C++ bytes)
    output_archive = "production_data.alc"
    with open(output_archive, "wb") as f:
        f.write(compressed_payload_bytes)

    # comp_size = os.path.getsize(output_archive)
    # print(f"⚡ Compression Engine Speed: {throughput:.2f} MB/s (Processed in {duration:.4f}s)")
    # print(f"📦 Compressed Size: {comp_size / (1024*1024):.2f} MB")
    # print(f"📉 Total Space Reduction: {(1 - (comp_size / orig_size)) * 100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())