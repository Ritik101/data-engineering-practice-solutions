import os
import requests
import zipfile
import asyncio
import aiohttp
import aiofiles
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import unittest

# Setup logging directory and format
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
log_file_name = os.path.join(LOG_DIR,f"log_file_{timestamp}")

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_name),
        logging.StreamHandler()
    ]
)

# Download Target Folder
DOWNLOAD_DIR = "Downloaded_files"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# List of files to download
download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]

def get_file_name(uri):
    return uri.split('/')[-1][:-4]


def extract_zip(zip_path):
    try:
        with zipfile.ZipFile(zip_path,'r') as zip_ref:
            zip_ref.extractall(DOWNLOAD_DIR)
        os.remove(zip_path)
        logging.info(f"Extracted and deleted: {zip_path}")
    except zipfile.BadZipFile:
        logging.error(f"Invalid ZIP file: {zip_path}")


#--------- SYNC Download ------------
def sync_download(uri):
    file_name = get_file_name(uri)
    path = os.path.join(DOWNLOAD_DIR, file_name)
    try:
        response = requests.get(uri)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        logging.info(f"Downloaded (sync): {uri}")
        extract_zip(path)
    except Exception as e:
        logging.error(f"Sync download failed for: {uri}: e")
        

#--------- ASYNC Download ------------
async def async_download(session, uri):
    file_name = uri.split('/')[-1][:-4]
    path = os.path.join(DOWNLOAD_DIR, file_name)
    try:
        async with session.get(uri) as resp:
            resp.raise_for_status()
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await resp.read())
            logging.info(f"Downloaded {path} ")
            extract_zip(path)
    except Exception as e:
        logging.error(f"Async Download failed for {uri}: {e}")
        

async def async_run_download():
    async with aiohttp.ClientSession() as session:
        tasks = [async_download(session, uri) for uri in download_uris]
        await asyncio.gather(*tasks)
        

#--------- Threaded Download ------------
def run_threaded_download():
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(sync_download, download_uris)
    

def main():
    mode = input("Enter mode (sync / async / threaded):\n").strip().lower()

    if mode == 'sync':
        for uri in download_uris:
            sync_download(uri)
    elif mode == 'async':
        asyncio.run(async_run_download())
    elif mode == 'threaded':
        run_threaded_download()
    else:
        logging.warning("Invalid mode selected. Choose from sync, async or threaded.")
        
        
if __name__ == "__main__":
    main()
    # Uncomment the next line to run unit tests manually
    # unittest.main()
