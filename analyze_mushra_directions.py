# Import binaqual into main directory
import sys
sys.path.insert(0, './binaqual')

import librosa
import numpy as np
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
for mushra_index in range(7, 13):
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

    # For MUSHRA scenes 7 - 13, vary listener azimuth with fixed listener location.    
    
    # Vary listener azimuth
    listener_azimuths = list(range(0, 360, 5))

    # Fixed listener position
    listener_xy = listener_xys[mushra_index]

    # Append data to empty lists
    listener_azi_arr = []
    snr_arr = []
    locq_arr = []

    # Fixed levels because of fixed listener location
    drums_level = get_src_level(listener_xy, drums_xy)
    bass_level = get_src_level(listener_xy, bass_xy)
    vocals_level = get_src_level(listener_xy, vocals_xy)
    other_level = get_src_level(listener_xy, other_xy)
    speech_level = get_src_level(listener_xy, speech_xy)

    # Fixed TDOAs because of fixed listener location
    bass_tdoa = get_src_tdoa(listener_xy, bass_xy)
    drums_tdoa = get_src_tdoa(listener_xy, drums_xy)
    vocals_tdoa = get_src_tdoa(listener_xy, vocals_xy)
    other_tdoa = get_src_tdoa(listener_xy, other_xy)
    speech_tdoa = get_src_tdoa(listener_xy, speech_xy)

    # Pad zeroes according to TDOAs of sources
    max_length = len(bass) + int(sr * max(bass_tdoa, drums_tdoa, vocals_tdoa, other_tdoa, speech_tdoa))
    bass_padded = np.pad(bass, (int(sr * bass_tdoa), max_length - int(sr * bass_tdoa) - len(bass)), 'constant')
    drums_padded = np.pad(drums, (int(sr * drums_tdoa), max_length - int(sr * drums_tdoa) - len(drums)), 'constant')
    vocals_padded = np.pad(vocals, (int(sr * vocals_tdoa), max_length - int(sr * vocals_tdoa) - len(vocals)), 'constant')
    other_padded = np.pad(other, (int(sr * other_tdoa), max_length - int(sr * other_tdoa) - len(other)), 'constant')
    speech_padded = np.pad(speech, (int(sr * speech_tdoa), max_length - int(sr * speech_tdoa) - len(speech)), 'constant')

    # ## COMMENT THE LINES FROM HERE DOWN BELOW IF YOU WANT TO SKIP THE BINAURAL SYNTHESIS

    # for listener_azi in listener_azimuths:
    #     start_time = time.time()

    #     print(f'Synthesising audio for listener azimuth: {listener_azi} degrees...')

    #     drums_azi = get_src_azimuth(listener_xy, drums_xy, listener_azi)
    #     bass_azi = get_src_azimuth(listener_xy, bass_xy, listener_azi)
    #     vocals_azi = get_src_azimuth(listener_xy, vocals_xy, listener_azi)
    #     other_azi = get_src_azimuth(listener_xy, other_xy, listener_azi)
    #     speech_azi = get_src_azimuth(listener_xy, speech_xy, listener_azi)

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
    #     listener_azi_arr.append(listener_azi)
    #     snr_arr.append(snr)
    #     locq_arr.append(locq)

    #     print(f'Elapsed time: {time.time() - start_time:.04f} s')

    # num_entries = len(listener_azi_arr)

    # # create a data frame with the following columns
    # df = pd.DataFrame({
    #                 'song_name': [song_id] * num_entries,
    #                 'ir_type': [ir_type] * num_entries,
    #                 'motion_type': ['rotational'] * num_entries,
    #                 'speech_xy': [speech_xy] * num_entries,
    #                 'listener_azi': listener_azi_arr,
    #                 'listener_x': [listener_xy[0]] * num_entries, 'listener_y': [listener_xy[1]] * num_entries,
    #                 'snr': snr_arr,
    #                 'locq': locq_arr,
    #                 })
    # df.to_csv(f'{data_folder}{song_id}_{speech_id}_{ir_type.lower()}_s{speech_direction}_x{int((listener_xy[0]*10)+25)}y{int((listener_xy[1]*10)+25)}.csv')

    # ### COMMENT THE LINES FROM HERE UP ABOVE IF YOU WANT TO SKIP THE BINAURAL SYNTHESIS

    # Reload the data frame
    df = pd.read_csv(f'{data_folder}{song_id}_{speech_id}_{ir_type.lower()}_s{speech_direction}_x{int((listener_xy[0]*10)+25)}y{int((listener_xy[1]*10)+25)}.csv')

    # Get source angles
    bass_angle = get_src_azimuth(listener_xy, bass_xy, 0)
    drums_angle = get_src_azimuth(listener_xy, drums_xy, 0)
    vocals_angle = get_src_azimuth(listener_xy, vocals_xy, 0)
    other_angle = get_src_azimuth(listener_xy, other_xy, 0)
    speech_angle = get_src_azimuth(listener_xy, speech_xy, 0)

    # Get source distances
    bass_distance = math.dist(listener_xy, bass_xy)
    drums_distance = math.dist(listener_xy, drums_xy)
    vocals_distance = math.dist(listener_xy, vocals_xy)
    other_distance = math.dist(listener_xy, other_xy)
    speech_distance = math.dist(listener_xy, speech_xy)

    # Setup input and output variables
    response_name = 'locq'
    factor = df['listener_azi'].to_list()
    response = df[response_name].to_list()
    response2 = df['snr'].to_list()

    # Close the loop for plotting
    factor.append(factor[0])
    response.append(response[0])
    response2.append(response2[0])

    # Normalise the values from 0 to 1
    normalized_response = normalize_data(response)
    normalized_response2 = normalize_data(response2)

    # Get mushra scores
    mushra_df = pd.read_csv(f'./output/mushra_{ir_type.lower()}/mushra_files_with_scores.csv')
    part_mushra_df = mushra_df[(mushra_df['song_name'] == song_id) &
                            (mushra_df['ir_type'] == ir_type) &
                            (mushra_df['motion_type'] == 'rotational') &
                            (mushra_df['speech_xy'] == str(speech_xy)) &
                            (mushra_df['snr'] != float('inf')) & 
                            (mushra_df['snr'] != 0)]
    mushra_azi = part_mushra_df['listener_azi'].to_list()
    mushra_labels = part_mushra_df['data_point'].to_list()
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

    # Set up the plots
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(np.deg2rad(factor), normalized_response, label='normalised LQ', color='tab:blue')
    ax.plot(np.deg2rad(factor), normalized_response2, label='normalised SNR', color='tab:red')
    ax.set_rmax(1)
    ax.set_rticks([0, 0.50, 1.00]) # Less radial ticks
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_rlabel_position(135) # Move radial labels away from plotted line
    ax.set_theta_zero_location("N") # Set 0 degrees to the top
    ax.grid(True)

    # Annotate the source angles
    source_angles = [drums_angle, bass_angle, vocals_angle, other_angle, speech_angle]
    source_distances = np.array([drums_distance, bass_distance, vocals_distance, other_distance, speech_distance])
    normalised_distances = (source_distances - min(source_distances)) / (max(source_distances) - min(source_distances))
    scale_min, scale_max = (2, 10)
    source_scales = [scale_max + normalised * (scale_min - scale_max) for normalised in normalised_distances]
    source_names = ['drums', 'bass', 'vocals', 'other', 'speech']
    source_markers = ['x', 's', 'v', 'o', 'd']
    source_colors = ['b', 'g', 'c', 'm', 'r']
    for i in range(len(source_angles)):
        if 0 < source_angles[i] < 180:
            ha1, ha2 = 'left', 'right'
        else:
            ha1, ha2 = 'right', 'left'
        ax.scatter(np.deg2rad(source_angles[i]), 1.0, color=source_colors[i], s=50, marker=source_markers[i])
        ax.text(np.deg2rad(source_angles[i]), 0.9, f'{source_distances[i]:.1f}m', fontsize=10, va='center', ha=ha1, color=source_colors[i])
        ax.text(np.deg2rad(source_angles[i]), 1.1, source_names[i], fontsize=10, va='center', ha=ha2, color=source_colors[i])

    # Annotate mushra scores
    for i, azi in enumerate(mushra_azi):
        azi_index = factor.index(azi)
        if 0 < azi < 180:
            ha1 = 'right'
            ha2 = 'left'
        else:
            ha1 = 'left'
            ha2 = 'right'
        ax.scatter(np.deg2rad(azi), 1.0, color='k', s=50, marker='*')
        ax.text(np.deg2rad(azi), 1.1, f'{mushra_scores_average[i]} \u00B1 {mushra_scores_ci_error[i]}', fontsize=10, va='center', ha=ha1, color='k')
        ax.text(np.deg2rad(azi), 0.9, mushra_labels[i], fontsize=10, va='center', ha=ha2, color='k')

    # Save the plots
    ax.set_title(f"Naviqual Polar Map at Listener Location {listener_xy} for {genre} Song with {ir_type}", va='bottom')
    ax.legend(bbox_to_anchor=(0.5, -0.1), loc='lower center', ncols=2)
    plt.savefig(f'{plots_folder}{song_id}_{speech_id}_{ir_type.lower()}_s{speech_direction}_{response_name}_x{int((listener_xy[0]*10)+25)}y{int((listener_xy[1]*10)+25)}.png', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()