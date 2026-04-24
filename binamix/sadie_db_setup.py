import os
import sys
from binamix.file_utilities import *


# Set paths relative to script's own location
script_dir = os.path.dirname(os.path.abspath(__file__))
sadie_dir = os.path.join(script_dir, "..", "sadie")

# Check/create sadie folder if necessary
if not os.path.exists(sadie_base_path := os.path.join(script_dir, "..", "sadie")):
    os.makedirs(sadie_base_path)
else:
    print("You already have the SADIE Database in your directory.")

# Check and download if Database-Master_2-1 doesn't exist
sadie_dataset_path = os.path.join(sadie_base_path, "Database-Master_V2-1")
if not os.path.exists(sadie_dataset_path := os.path.join(sadie_base_path, "Database-Master_2-1")):
    url = 'https://zenodo.org/records/12092466/files/Database-Master_V2-2.zip'
    downloaded_file = download_file(url=url, dest_folder=sadie_base_path)
    unzip_file(downloaded_file, sadie_base_path)
    os.remove(downloaded_file)
    print(f"Zip file removed: {downloaded_file}")
    print("Setup Complete")
else:
    print("Database already exists, no download needed.")