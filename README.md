# NAVIQUAL: Creating Spatial Audio Quality Maps for Virtual Live Music Environments
Python Implementation of the NAVIQUAL paper published in the 160th AES Convention

## Setup
* Create a virtual environment with Python >= 3.10
* Install the required packages by running `pip install -r requirements.txt`
* Download the SADIE II Database by running `python -m binamix.sadie_db_setup`

## Synthesise Audio Files for MUSHRA Tests
* Run `python create_mushra.py` to synthesise the binaural signals used for the listening tests.
* Listen to the audio signals in the `output/mushra_{ir_type}/` directory to assess the listening quality.
* Inspect the CSV file `mushra_files_objective.csv` to check the objective metric values for each audio signal.

## Post-process the Listening Test Results
* After running the listening tests in the [GoListen](https://golisten.ucd.ie) platform , you should obtain a CSV file of the scores. Place this inside the `output/mushra_{ir_type}/` directory.
* Run `python mushra_scores_to_df.py` to append the subjective scores on the `mushra_files_objective.csv` data frame. This creates a new file called `mushra_files_with_scores.csv`.

## Assessing Quality Across Listener Locations
* Run `python analyze_mushra_locations.py` to create the Naviqual contour maps along with the MUSHRA scores.
* By default, the binaural synthesis is commented out. You can uncomment these lines if you want to synthesise the binaural signals.
* Change the parameter `ir_type` if you want anechoic (HRIR) or reverberant (BRIR) conditions.
* Change the parameter `response_name` to select the objective metric you want to use, i.e. `locq` or `snr`.
* Here are the Naviqual contour maps for the HRIR listening test trials using the `locq` objective metric:

<img width="407" height="340.25" alt="Matthew Entwistle - Dont You Ever_clnsp340_hrir_s180_locq" src="https://github.com/user-attachments/assets/8cb20baa-f011-4e6d-8b59-63172b033181" />

<img width="407" height="340.25" alt="Matthew Entwistle - Dont You Ever_clnsp1006_hrir_s270_locq" src="https://github.com/user-attachments/assets/98e12587-f7ff-4154-9989-1f26a6a84786" />

<img width="407" height="340.25" alt="Skelpolu - Together Alone_clnsp544_hrir_s180_locq" src="https://github.com/user-attachments/assets/872276e9-9591-4a53-8ca3-508eb18b0284" />

<img width="407" height="340.25" alt="Skelpolu - Together Alone_clnsp980_hrir_s270_locq" src="https://github.com/user-attachments/assets/02b5f51d-d6cb-48cd-9fdc-e98ca944d7da" />

<img width="407" height="340.25" alt="Juliet&#39;s Rescue - Heartbeats_clnsp453_hrir_s180_locq" src="https://github.com/user-attachments/assets/8dc99a2d-67dd-495a-ae03-5eea72d05e06" />

<img width="407" height="340.25" alt="Juliet&#39;s Rescue - Heartbeats_clnsp596_hrir_s270_locq" src="https://github.com/user-attachments/assets/1148ef2f-3a15-4350-a5f8-ec7df0946251" />

## Assessing Quality Across Listener Directions
* Run `python analyze_mushra_directions.py` to create the Naviqual polar maps along with the MUSHRA scores.
* Similarly, change the parameter `ir_type` depending on your needs.
* Here are the Naviqual polar maps for the HRIR listening test trials:

<img width="360.2" height="266.2" alt="Matthew Entwistle - Dont You Ever_clnsp52_hrir_s180_locq_x35y45" src="https://github.com/user-attachments/assets/38379b91-8bb3-42e4-b30d-ed14bb1aab55" />

<img width="363.8" height="266.2" alt="Matthew Entwistle - Dont You Ever_clnsp573_hrir_s270_locq_x15y45" src="https://github.com/user-attachments/assets/b0f84635-0b35-4a45-86eb-74a596652b1d" />

<img width="390" height="266.2" alt="Skelpolu - Together Alone_clnsp242_hrir_s180_locq_x35y45" src="https://github.com/user-attachments/assets/afa67c29-b5a4-47ff-a96d-386d76d92b5b" />

<img width="393.5" height="266.2" alt="Skelpolu - Together Alone_clnsp1086_hrir_s270_locq_x15y45" src="https://github.com/user-attachments/assets/873ed870-8947-4c6d-b5cf-8f9d45aed6d0" />

<img width="385.8" height="266.2" alt="Juliet&#39;s Rescue - Heartbeats_clnsp608_hrir_s180_locq_x35y45" src="https://github.com/user-attachments/assets/74fdefa0-36e3-4f91-9506-609816107a8f" />

<img width="389.4" height="266.2" alt="Juliet&#39;s Rescue - Heartbeats_clnsp362_hrir_s270_locq_x15y45" src="https://github.com/user-attachments/assets/aa143bf8-09f1-4ec9-bfe8-dba291b6e204" />
