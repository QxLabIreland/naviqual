# Import binaqual into main directory
import sys
sys.path.insert(0, './binaqual')

import librosa
import numpy as np
import itertools
import os
import matplotlib.pyplot as plt
import pandas as pd
import time
from scipy.stats import t
from binamix.sadie_utilities import *
from utils import * 
from binaqual import calculate_binaqual_sig

# Settings for every MUSHRA scene
speech_ids = ["clnsp0", "clnsp340", "clnsp1006", "clnsp544", "clnsp980", "clnsp453", "clnsp596", "clnsp52", "clnsp573", "clnsp242", "clnsp1086", "clnsp608", "clnsp362"]
songs = ["Matthew Entwistle - Dont You Ever", "Skelpolu - Together Alone", "Juliet's Rescue - Heartbeats", "Al James - Schoolboy Facination"]
genres = ['Jazz', 'Electronic', 'Pop Rock', 'Pop Rock']
song_indices = [3, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2]
speech_xys = [(0, -2), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0)]
listener_xys = [None, None, None, None, None, None, None, (1, 2), (-1, 2), (1, 2), (-1, 2), (1, 2), (-1, 2)]

# Configuration settings
ir_type = "HRIR"
subject_id = "D1"
speaker_layout = "none"
sr = 44100

# Iterate over every MUSHRA scene
for mushra_index in range(1,7):
    # Setup output folders
    mushra_folder = f'./output/mushra_{ir_type.lower()}/mushra{mushra_index}/'
    data_folder = f'./output/mushra_{ir_type.lower()}/mushra_data/'
    plots_folder = f'./output/mushra_{ir_type.lower()}/mushra_plots/'

    # Create folders if it does not exist
    if not os.path.exists(mushra_folder):
        os.makedirs(mushra_folder)
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)

    # Setting for current MUSHRA scene
    song_id = songs[song_indices[mushra_index]]
    genre = genres[song_indices[mushra_index]]
    speech_id = speech_ids[mushra_index]
    speech_xy = speech_xys[mushra_index]
    speech_direction = int(get_src_azimuth((0, 0), speech_xy, 0))

    # Setup paths
    music_path = "./audio/musdb18_samples/"
    speech_path = f"./audio/speech/{speech_id}.wav"
    bass_path = f"{music_path}{song_id}/bass.wav"
    drums_path = f"{music_path}{song_id}/drums.wav"
    vocals_path = f"{music_path}{song_id}/vocals.wav"
    other_path = f"{music_path}{song_id}/other.wav"
    audio_paths = [bass_path, drums_path, vocals_path, other_path, speech_path]

    # Load the audio files
    bass, _ = librosa.load(audio_paths[0], sr=sr, mono=True, duration=6.8)
    drums, _ = librosa.load(audio_paths[1], sr=sr, mono=True, duration=6.8)
    vocals, _ = librosa.load(audio_paths[2], sr=sr, mono=True, duration=6.8)
    other, _ = librosa.load(audio_paths[3], sr=sr, mono=True, duration=6.8)
    speech, _ = librosa.load(audio_paths[4], sr=sr, mono=True, duration=6.8)

    # Normalize the audio files
    bass = loudness_normalize(bass, sr, lufs=-30.0)
    drums = loudness_normalize(drums, sr, lufs=-30.0)
    vocals = loudness_normalize(vocals, sr, lufs=-30.0)
    other = loudness_normalize(other, sr, lufs=-30.0)
    speech = loudness_normalize(speech, sr, lufs=-30.0)

    # Fixed sound locations
    bass_xy = (-0.5, 3.0)
    drums_xy = (-1.5, 3.0)
    vocals_xy = (0.5, 3.0)
    other_xy = (1.5, 3.0)

    # For MUSHRA scenes 0 - 6, vary listener location with fixed listener azimuth.

    # Vary listener location
    x = np.arange(2.5, -2.6, -0.5)      # rows: 2.5 to -2.5 with increments of -0.5
    y = np.arange(-2.5, 2.6, 0.5)       # cols: -2.5 to 2.5 with increments of +0.5

    # Fixed listener azimuth for scenes 0 - 6
    listener_azi = 0

    # Append data to empty lists
    listener_xy_arr = []
    snr_arr = []
    locq_arr = []

    # ## COMMENT THE LINES FROM HERE DOWN BELOW IF YOU WANT TO SKIP THE BINAURAL SYNTHESIS

    # for (yi, xi) in itertools.product(x, y):
    #     start_time = time.time()
    #     listener_xy = (xi, yi)
    #     x_i = np.where(x == yi)[0][0]
    #     y_i = np.where(y == xi)[0][0]

    #     print(f'Synthesising audio for listener position: {listener_xy}...')

    #     drums_level = get_src_level(listener_xy, drums_xy)
    #     bass_level = get_src_level(listener_xy, bass_xy)
    #     vocals_level = get_src_level(listener_xy, vocals_xy)
    #     other_level = get_src_level(listener_xy, other_xy)
    #     speech_level = get_src_level(listener_xy, speech_xy)

    #     bass_tdoa = get_src_tdoa(listener_xy, bass_xy)
    #     drums_tdoa = get_src_tdoa(listener_xy, drums_xy)
    #     vocals_tdoa = get_src_tdoa(listener_xy, vocals_xy)
    #     other_tdoa = get_src_tdoa(listener_xy, other_xy)
    #     speech_tdoa = get_src_tdoa(listener_xy, speech_xy)

    #     drums_azi = get_src_azimuth(listener_xy, drums_xy, listener_azi)
    #     bass_azi = get_src_azimuth(listener_xy, bass_xy, listener_azi)
    #     vocals_azi = get_src_azimuth(listener_xy, vocals_xy, listener_azi)
    #     other_azi = get_src_azimuth(listener_xy, other_xy, listener_azi)
    #     speech_azi = get_src_azimuth(listener_xy, speech_xy, listener_azi)

    #     # Pad zeroes according to TDOAs of sources
    #     max_length = len(bass) + int(sr * max(bass_tdoa, drums_tdoa, vocals_tdoa, other_tdoa, speech_tdoa))
    #     bass_padded = np.pad(bass, (int(sr * bass_tdoa), max_length - int(sr * bass_tdoa) - len(bass)), 'constant')
    #     drums_padded = np.pad(drums, (int(sr * drums_tdoa), max_length - int(sr * drums_tdoa) - len(drums)), 'constant')
    #     vocals_padded = np.pad(vocals, (int(sr * vocals_tdoa), max_length - int(sr * vocals_tdoa) - len(vocals)), 'constant')
    #     other_padded = np.pad(other, (int(sr * other_tdoa), max_length - int(sr * other_tdoa) - len(other)), 'constant')
    #     speech_padded = np.pad(speech, (int(sr * speech_tdoa), max_length - int(sr * speech_tdoa) - len(speech)), 'constant')

    #     track1 = TrackObject(name="speech", azimuth=speech_azi, elevation=0, level=speech_level, reverb=0.0, audio=speech_padded)
    #     track2 = TrackObject(name="bass", azimuth=bass_azi, elevation=0, level=bass_level, reverb=0.0, audio=bass_padded)
    #     track3 = TrackObject(name="drums", azimuth=drums_azi, elevation=0, level=drums_level, reverb=0.0, audio=drums_padded)
    #     track4 = TrackObject(name="vocals", azimuth=vocals_azi, elevation=0, level=vocals_level, reverb=0.0, audio=vocals_padded)
    #     track5 = TrackObject(name="other", azimuth=other_azi, elevation=0, level=other_level, reverb=0.0, audio=other_padded)

    #     # Place all TrackObject tracks in an array for mixdown
    #     tracks = [track1, track2, track3, track4, track5]

    #     # Mix the tracks
    #     output, output_tracks = mix_tracks_binaural(tracks, subject_id, sr, ir_type, speaker_layout, mode="planar", reverb_type="1")

    #     # Truncate output to length of tracks
    #     output = output[:, 0:len(bass_padded)]
    #     output_tracks = output_tracks[:, :, 0:len(bass_padded)]
    #     music_tracks = output_tracks[1:]      

    #     # Signal-to-noise ratio
    #     desired = np.sum(music_tracks, axis=0)
    #     noise = output - desired

    #     desired_lufs = sig_to_lufs(desired.T, sr)
    #     noise_lufs = sig_to_lufs(noise.T, sr)
    #     snr = (desired_lufs - noise_lufs)

    #     # Localization similarity
    #     nsim_values, locq = calculate_binaqual_sig(desired.T, output.T, sr)

    #     # append to lists
    #     listener_xy_arr.append(listener_xy)
    #     snr_arr.append(snr)
    #     locq_arr.append(locq)

    #     print(f'Elapsed time: {time.time() - start_time:.04f} s')

    # num_entries = len(listener_xy_arr)

    # # create a data frame with the following columns
    # df = pd.DataFrame({
    #                 'song_name': [song_id] * num_entries,
    #                 'ir_type': [ir_type] * num_entries,
    #                 'motion_type': ['translational'] * num_entries,
    #                 'speech_xy': [speech_xy] * num_entries,
    #                 'listener_azi': [listener_azi] * num_entries,
    #                 'listener_x': [xy[0] for xy in listener_xy_arr], 'listener_y': [xy[1] for xy in listener_xy_arr],
    #                 'snr': snr_arr,
    #                 'locq': locq_arr,
    #                 })
    # df.to_csv(f'{data_folder}{song_id}_{speech_id}_{ir_type.lower()}_s{speech_direction}.csv')

    # ## COMMENT THE LINES FROM HERE UP ABOVE IF YOU WANT TO SKIP THE BINAURAL SYNTHESIS

    # Reload the data frame
    df = pd.read_csv(f'{data_folder}{song_id}_{speech_id}_{ir_type.lower()}_s{speech_direction}.csv')
    response_name = 'locq'

    df_pivot = df.pivot_table(index='listener_y', columns='listener_x', values=response_name)
    X = df_pivot.index.values
    Y = df_pivot.columns.values
    Z = df_pivot.values

    # Get mushra scores
    mushra_df = pd.read_csv(f'./output/mushra_{ir_type.lower()}/mushra_files_with_scores.csv')
    part_mushra_df = mushra_df[(mushra_df['song_name'] == song_id) &
                            (mushra_df['motion_type'] == 'translational') &
                            (mushra_df['ir_type'] == ir_type) &
                            (mushra_df['speech_xy'] == str(speech_xy)) &
                            (mushra_df['snr'] != float('inf')) & 
                            (mushra_df['snr'] != 0)]

    # Listener position for second block
    listener_xy_b2 = listener_xys[mushra_index + 6]
    listener_xy_b2 = tuple(map(float, listener_xy_b2))

    # Get columns with mushra scores
    mushra_score_cols = [col for i, col in enumerate(part_mushra_df.columns) if "mushra_score" in col]
    mushra_scores = part_mushra_df[mushra_score_cols].to_numpy()
    mushra_scores = mushra_scores.astype(int)

    # Calculate average and confidence intervals
    mushra_scores_average = np.empty(len(mushra_scores))
    mushra_scores_ci_error = np.empty(len(mushra_scores))
    for index, mushra_scores_sample in enumerate(mushra_scores):
        num_samples = len(mushra_scores_sample)
        average = np.mean(mushra_scores_sample)
        stdev = np.std(mushra_scores_sample, ddof=1)
        error = t.ppf(0.975, df=num_samples-1) * (stdev / np.sqrt(num_samples))
        mushra_scores_average[index] = np.round(average, decimals=1)
        mushra_scores_ci_error[index] = np.round(error, decimals=1)

    # Plot
    # Annotate the band and speaker locations
    source_locs = [drums_xy, bass_xy, vocals_xy, other_xy, speech_xy]
    source_names = ['drums', 'bass', 'vocals', 'other', 'speech']
    source_markers = ['x', 's', 'v', 'o', 'd']
    source_colors = ['b', 'g', 'c', 'm', 'r']

    # Plot quivers
    x_coords = np.array([x for x, y in source_locs])
    y_coords = np.array([y for x, y in source_locs])
    u = -x_coords
    v = -y_coords
    norm = np.sqrt(u**2 + v**2)
    u_norm = u / norm
    v_norm = v / norm

    # Annotate the mushra scores
    listener_x_arr = part_mushra_df['listener_x'].to_list()
    listener_y_arr = part_mushra_df['listener_y'].to_list()
    mushra_locs = [(x, y) for x, y in zip(listener_x_arr, listener_y_arr)]
    mushra_labels = part_mushra_df['data_point'].to_list()
    
    # Set up the plots
    plt.contourf(X, Y, Z, cmap='viridis')
    plt.axis('scaled')
    plt.colorbar(label = response_name)
    plt.title(f'Naviqual Map for {genre} Song with {ir_type}.')
    plt.xlim([-3.0, 3.0])
    plt.ylim([-3.0, 3.0])
    plt.xlabel("x (meters)")
    plt.ylabel("y (meters)")
    # Annotate band and speech locations
    for i in range(len(source_locs)):
        if source_names[i] == 'speech':
            plt.scatter(source_locs[i][0], source_locs[i][1], color=source_colors[i], s=50, marker=source_markers[i], label=source_names[i]) 
        else:
            plt.scatter(source_locs[i][0], source_locs[i][1], color=source_colors[i], s=50, marker=source_markers[i])
            if i - 2 < 0:
                plt.text(source_locs[i][0] - 0.1, source_locs[i][1] - 0.2, source_names[i], fontsize=10, ha='right', va='center', color='black') 
            else:
                plt.text(source_locs[i][0] + 0.1, source_locs[i][1] - 0.2, source_names[i], fontsize=10, ha='left', va='center', color='black') 

    # Annotate mushra scores
    plt.scatter([x for x,y in mushra_locs], [y for x,y in mushra_locs], color='black', s=50, marker='*', label='mushra')
    for i, loc in enumerate(mushra_locs):
        plt.text(loc[0], loc[1] + 0.2, f'{mushra_scores_average[i]} \u00B1 {mushra_scores_ci_error[i]}', fontsize=10, ha='center', va='center', color='black')
        plt.text(loc[0], loc[1] - 0.25, mushra_labels[i], fontsize=10, ha='center', va='center', color='black')
        # Annotate a circle for the listener position in second block
        if loc == listener_xy_b2:
            plt.plot(loc[0], loc[1], marker='o', ms=10, mec='black', mfc='none', mew=1)
    plt.legend(loc='lower center', ncol=2, fontsize=10)
    plt.savefig(f'{plots_folder}{song_id}_{speech_id}_{ir_type.lower()}_s{speech_direction}_{response_name}.png', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()