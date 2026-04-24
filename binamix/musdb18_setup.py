import os
import sys
from binamix.file_utilities import *

# Check if MusDB18 exists in the current directory
# If not, download it from the URL
if not os.path.exists('./musdb18/'):
    url = 'https://zenodo.org/records/3338373/files/musdb18hq.zip'
    dest_folder = './musdb18/'
    downloaded_file = download_file(url, dest_folder)
    unzip_file(downloaded_file, dest_folder)
    os.remove(downloaded_file)
    print(f"Zip file removed: {downloaded_file}")
    print(f"Setup Complete")
else:
    print("You already have a '/musdb18' folder indicating that database in your current directory. If you still have problems, delete the '/dsd' folder and run this script again.")

