import pandas as pd
import numpy as np
import ast
import re
import os
import csv
from utils import *

# Settings
sr = 44100
ir_type = "BRIR"
mushra_folder = f'./output/mushra_{ir_type.lower()}/'
string_pattern = re.compile(r'mushra_Test-.*\.csv')
for fname in os.listdir(mushra_folder):
    if string_pattern.match(fname):
        mushra_results_csv = fname

# CSV file of the mushra scores from Go Listen
mushra_csv_path = f'{mushra_folder}{mushra_results_csv}'
mushra_scores = []
with open(mushra_csv_path) as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for i, row in enumerate(spamreader):
        if i == 1:
            first_index = row.index('reference.wav')
            mushra_filenames = row[first_index:]
            mushra_filenames = [filename.replace('"', '') for filename in mushra_filenames if filename.endswith('.wav')]
        elif i >= 3:
            scores = row[first_index:]
            scores_int = [int(score) for score in scores if score.isdigit()]
            mushra_scores.append(scores_int)

mushra_scores = np.array(mushra_scores)

reference_scores = np.array([mushra_scores[:, i] for i, filename in enumerate(mushra_filenames) if filename == 'reference.wav'])
anchor_scores = np.array([mushra_scores[:, i] for i, filename in enumerate(mushra_filenames) if filename == 'anchor.wav'])

# Exclude scores if N(reference < 80) > 1 or if N(anchor >= 40) > 1
screening_failed = ((reference_scores < 80).sum(axis=0) > 1) | ((anchor_scores >= 40).sum(axis=0) > 1)
screened_mushra_scores = np.array([mushra_scores[i, :] for i, val in enumerate(screening_failed) if val == False])

# CSV file of the data frame without mushra scores
df = pd.read_csv(f'{mushra_folder}mushra_files_objective.csv')

# Iterate over data frame
mushra_scores_arr = []
for index, row in df.iterrows():
    # Check if reference or anchor
    snr = row['snr']
    if snr == float('inf') or snr == 0:
        # No scores for reference and anchor for rotational motion types
        if index >= 42:
            song_mushra_scores = [None] * len(screened_mushra_scores)
        else:
            song_mushra_scores = screened_mushra_scores[:,index].tolist()
        mushra_scores_arr.append(song_mushra_scores)
    else:
        song_id = row['song_name']
        speech_id = row['speech_name']
        ir_type = row['ir_type']
        speech_xy = row['speech_xy']
        speech_xy = ast.literal_eval(speech_xy)     # convert string to tuple
        speech_direction = int(get_src_azimuth((0, 0), speech_xy, 0))
        listener_xy = (row['listener_x'], row['listener_y'])
        listener_azi = int(row['listener_azi'])
        filename = f'{song_id}_{speech_id}_{ir_type}_s{speech_direction}_uazi{listener_azi}_x{int(10*(listener_xy[0]+2.5)):02d}_y{int(10*(listener_xy[1]+2.5)):02d}.wav'

        # Find mushra score of the given filename
        mushra_index = mushra_filenames.index(filename)
        song_mushra_scores = screened_mushra_scores[:,mushra_index].tolist()
        mushra_scores_arr.append(song_mushra_scores)

# Append mushra scores in new data frame
mushra_scores_arr = np.array(mushra_scores_arr)
for i in range(np.shape(mushra_scores_arr)[1]):
    df[f'mushra_score{i+1}'] = mushra_scores_arr[:, i]

df.to_csv(f'{mushra_folder}mushra_files_with_scores.csv')