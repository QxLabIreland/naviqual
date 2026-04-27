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
* Here are the Naviqual contour maps for all the listening test trials using the `locq` objective metric:

## Assessing Quality Across Listener Directions
* Run `python analyze_mushra_directions.py` to create the Naviqual polar maps along with the MUSHRA scores.
* Similarly, change the parameter `ir_type` depending on your needs.
* Here are the Naviqual polar maps for all the listening test trials:
