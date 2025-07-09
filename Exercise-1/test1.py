import requests
import os
import zipfile

download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]

DOWNLOAD_DIR = os.path.join("downloaded_files")

def ensure_directory():
    ##Create the download directory if it doesn't exist  
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
def get_file_name(uri):
    ## Extract Filename from uri
    return uri.split('/')[-1][:-4]

def download_zip(uri, dest_path):
    ## Download a file and save it to disk.
    try:
        response = requests.get(uri)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"File Downloaded: {dest_path}")
        return True
    except requests.exceptions.HTTPError as http_error:
        print(f"HTTP Error: {http_error}\n")
    except requests.exceptions.RequestException as req_error:
        print(f"Request failed: -> {req_error}")
        return False

def extract_and_cleanup(zip_path, extract_to):
    ## Extract zip file contents and delete the zip
    try:
        with zipfile.ZipFile(zip_path,'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)
        print(f"Extracted zip file to: {extract_to}\nDeleted: {zip_path}\n")
    except zipfile.BadZipFile:
        print(f"Not a valid zip File: {zip_path}")
            

def main():
    ensure_directory()
    
    for uri in download_uris:
        file_name = get_file_name(uri)
        zip_path = os.path.join(DOWNLOAD_DIR, file_name)
        
        if download_zip(uri, zip_path):
            extract_and_cleanup(zip_path,DOWNLOAD_DIR)


if __name__ == "__main__":
    main()

