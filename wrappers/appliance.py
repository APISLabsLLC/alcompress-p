import time
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from alcompress import compress_enterprise 

# Setup: Limit log to 1MB, keep 2 backups (Max ~2MB total footprint)
handler = RotatingFileHandler('appliance.log', maxBytes=1*1024*1024, backupCount=2)
logging.basicConfig(handlers=[handler], level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

class CompressionHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            file_name = os.path.basename(event.src_path)
            out_path = os.path.join("..", "outbox", f"{file_name}.alc")
            
            logging.info(f"Processing: {file_name}")
            
            try:
                # 1. Compress the data
                compress_enterprise(event.src_path, out_path)
                
                # 2. Cleanup: Move processed file to a 'processed' subfolder
                # This prevents it from sitting in the inbox forever
                if not os.path.exists("processed"):
                    os.makedirs("processed")
                shutil.move(event.src_path, os.path.join("processed", file_name))
                
                logging.info(f"Successfully compressed: {file_name}")
            except Exception as e:
                logging.error(f"Error processing {file_name}: {e}")

if __name__ == "__main__":
    # Ensure directories exist
    for d in ["../inbox", "../outbox", "processed"]:
        if not os.path.exists(d): os.makedirs(d)

    observer = Observer()
    observer.schedule(CompressionHandler(), path='../inbox', recursive=False)
    observer.start()
    
    logging.info("AlCompress Appliance Service Active.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()