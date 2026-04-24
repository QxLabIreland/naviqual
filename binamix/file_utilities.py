import os
import requests
import zipfile
import sys


# Function to Download a file from a URL with a loader
def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    short_name = url.split('/')[-1]    
    print(f"\nDownloading: {short_name}")
    
    response = requests.get(url, stream=True)
    file_name = os.path.join(dest_folder, url.split('/')[-1])
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    wrote = 0
    
    print(file_name)

    with open(file_name, 'wb') as file:
        for data in response.iter_content(block_size):
            wrote += len(data)
            file.write(data)
            done = int(50 * wrote / total_size)
            sys.stdout.write(f"\r[{'█' * done}{' ' * (50-done)}] {done * 2}%")
            sys.stdout.flush()
    
    print(f"\nDownload Complete {file_name}")
    return file_name

# Function to unzip a file
def unzip_file(file_name, dest_folder):
    
    print(f"Unzipping: {file_name}")
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)
    print(f"Unzip Complete: {file_name}")