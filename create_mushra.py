# Import binaqual into main directory
import sys
sys.path.insert(0, './binaqual')

import librosa
import soundfile as sf
import pandas as pd
from binamix.sadie_utilities import *
from utils import * 
from binaqual import calculate_binaqual_sig

songs = ["Matthew Entwistle - Dont You Ever", "Skelpolu - Together Alone", "Juliet's Rescue - Heartbeats", "Al James - Schoolboy Facination"]
ir_type = 'HRIR'

# 1 training + 12 MUSHRA pages
mushra_folders = [f'./output/mushra_{ir_type.lower()}/mushra{index}/' for index in range(13)]
song_indices = [3, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 2, 2]
speech_ids = ["clnsp0", "clnsp340", "clnsp1006", "clnsp544", "clnsp980", "clnsp453", "clnsp596", "clnsp52", "clnsp573", "clnsp242", "clnsp1086", "clnsp608", "clnsp362"]
speech_xys = [(0, -2), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0), (0, -2), (2, 0)]
data_points = [['L1', 'L2', 'L3', 'L4'],
               ['L1', 'L2', 'L3', 'L4'],
               ['L1', 'L2', 'L3', 'L4'],
               ['L1', 'L2', 'L3', 'L4'],
               ['L1', 'L2', 'L3', 'L4'],
               ['L1', 'L2', 'L3', 'L4'],
               ['L1', 'L2', 'L3', 'L4'],
               ['D1', 'D2', 'D3', 'D4'],
               ['D1', 'D2', 'D3', 'D4'],
               ['D1', 'D2', 'D3', 'D4'],
               ['D1', 'D2', 'D3', 'D4'],
               ['D1', 'D2', 'D3', 'D4'],
               ['D1', 'D2', 'D3', 'D4']]
listener_xys = [[(0, 0.5), (1, -0.5), (-1, 1.5), (1, 2)],
            [(0, 0.5), (1, -0.5), (-1, 1.5), (1, 2)],
            [(0, 0), (-1, 0.5), (1, 2), (-1, 2)],
            [(0, 0.5), (1, -0.5), (-1, 1.5), (1, 2)],
            [(0, 0), (-1, 0.5), (1, 2), (-1, 2)],
            [(0, 0.5), (1, -0.5), (-1, 1.5), (1, 2)],
            [(0, 0), (-1, 0.5), (1, 2), (-1, 2)],
            [(1, 2), (1, 2), (1, 2), (1, 2)], 
            [(-1, 2), (-1, 2), (-1, 2), (-1, 2)], 
            [(1, 2), (1, 2), (1, 2), (1, 2)], 
            [(-1, 2), (-1, 2), (-1, 2), (-1, 2)], 
            [(1, 2), (1, 2), (1, 2), (1, 2)], 
            [(-1, 2), (-1, 2), (-1, 2), (-1, 2)]] 
listener_azis = [[0, 0, 0, 0],
             [0, 0, 0, 0], 
             [0, 0, 0, 0],  
             [0, 0, 0, 0],  
             [0, 0, 0, 0],  
             [0, 0, 0, 0], 
             [0, 0, 0, 0], 
             [85, 300, 200, 20],
             [255, 50, 195, 15],
             [120, 300, 205, 25],
             [270, 50, 195, 15],
             [85, 305, 200, 20],
             [265, 50, 175, 355]]

# Configuration settings
subject_id = 'D1'
speaker_layout = 'none'
sr = 44100
music_path = './audio/musdb18_samples/'

# Band locations
drums_xy = (-1.5, 3.0)
bass_xy = (-0.5, 3.0)
vocals_xy = (0.5, 3.0)
other_xy = (1.5, 3.0)

# Append data to empty lists
song_id_arr = []
speech_id_arr = []
motion_type_arr = []
speech_xy_arr = []
data_points_arr = []
listener_azi_arr = []
listener_xy_arr = []
snr_arr = []
locq_arr = []

for mushra_index, mushra_folder in enumerate(mushra_folders):

    if mushra_index < 7:
        motion_type = 'translational'
    else:
        motion_type = 'rotational'

    # Create mushra folder if it does not exists
    if not os.path.exists(mushra_folder):
        os.makedirs(mushra_folder)

    song_index = song_indices[mushra_index]
    song_id = songs[song_index]
    speech_id = speech_ids[mushra_index]
    speech_xy = speech_xys[mushra_index]
    speech_direction = int(get_src_azimuth((0, 0), speech_xy, 0))

    # Load audio files
    bass_path = f"{music_path}{song_id}/bass.wav"
    drums_path = f"{music_path}{song_id}/drums.wav"
    vocals_path = f"{music_path}{song_id}/vocals.wav"
    other_path = f"{music_path}{song_id}/other.wav"
    speech_path = f"./audio/speech/{speech_id}.wav"
    reference_path = f"{music_path}{song_id}/mixture.wav"
    audio_paths = [bass_path, drums_path, vocals_path, other_path, speech_path, reference_path]

    bass, _ = librosa.load(audio_paths[0], sr=sr, mono=True, duration=6.8)
    drums, _ = librosa.load(audio_paths[1], sr=sr, mono=True, duration=6.8)
    vocals, _ = librosa.load(audio_paths[2], sr=sr, mono=True, duration=6.8)
    other, _ = librosa.load(audio_paths[3], sr=sr, mono=True, duration=6.8)
    speech, _ = librosa.load(audio_paths[4], sr=sr, mono=True, duration=6.8)
    reference, _ = librosa.load(audio_paths[5], sr=sr, mono=False, duration=6.8)

    # Normalize the audio files
    bass = loudness_normalize(bass, sr, lufs=-30.0)
    drums = loudness_normalize(drums, sr, lufs=-30.0)
    vocals = loudness_normalize(vocals, sr, lufs=-30.0)
    other = loudness_normalize(other, sr, lufs=-30.0)
    speech = loudness_normalize(speech, sr, lufs=-30.0)
    reference = loudness_normalize(reference.T, sr, lufs=-30.0)
    speech_stereo = np.array([speech, speech])
    speech_anchor = loudness_normalize(speech_stereo.T, sr, lufs=-20.0)
    anchor = reference + speech_anchor
    anchor = loudness_normalize(anchor, sr, lufs=-30.0)

    # Save reference and anchor files
    sf.write(f'{mushra_folder}reference.wav', reference, sr)
    sf.write(f'{mushra_folder}anchor.wav', anchor, sr)

    # Create training data for 0-th mushra
    if mushra_index == 0:
        speech_20 = loudness_normalize(speech_stereo.T, sr, lufs=-30.0)
        speech_40 = loudness_normalize(speech_stereo.T, sr, lufs=-35.0)
        speech_60 = loudness_normalize(speech_stereo.T, sr, lufs=-40.0)
        speech_80 = loudness_normalize(speech_stereo.T, sr, lufs=-45.0)

        train_20 = reference + speech_20
        train_40 = reference + speech_40
        train_60 = reference + speech_60
        train_80 = reference + speech_80

        train_20 = loudness_normalize(train_20, sr, lufs=-30.0)
        train_40 = loudness_normalize(train_40, sr, lufs=-30.0)
        train_60 = loudness_normalize(train_60, sr, lufs=-30.0)
        train_80 = loudness_normalize(train_80, sr, lufs=-30.0)

        sf.write(f'{mushra_folder}train_20.wav', train_20, sr)
        sf.write(f'{mushra_folder}train_40.wav', train_40, sr)
        sf.write(f'{mushra_folder}train_60.wav', train_60, sr)
        sf.write(f'{mushra_folder}train_80.wav', train_80, sr)

    # Reference data
    song_id_arr.append(song_id)
    speech_id_arr.append(speech_id)
    motion_type_arr.append(motion_type)
    speech_xy_arr.append(speech_xy)
    data_points_arr.append(None)
    listener_xy_arr.append((None, None))
    listener_azi_arr.append(None)
    snr_arr.append(float('inf'))
    locq_arr.append(1)

    # Anchor data
    nsim_values, locq = calculate_binaqual_sig(reference, anchor, sr)
    song_id_arr.append(song_id)
    speech_id_arr.append(speech_id)
    motion_type_arr.append(motion_type)
    speech_xy_arr.append(speech_xy)
    data_points_arr.append(None)
    listener_xy_arr.append((None, None))
    listener_azi_arr.append(None)
    snr_arr.append(0)
    locq_arr.append(locq)

    for data_point, listener_xy, listener_azi in zip(data_points[mushra_index], listener_xys[mushra_index], listener_azis[mushra_index]):

        # set mix parameters
        bass_level = get_src_level(listener_xy, bass_xy)
        drums_level = get_src_level(listener_xy, drums_xy)
        vocals_level = get_src_level(listener_xy, vocals_xy)
        other_level = get_src_level(listener_xy, other_xy)
        speech_level = get_src_level(listener_xy, speech_xy)

        bass_tdoa = get_src_tdoa(listener_xy, bass_xy)
        drums_tdoa = get_src_tdoa(listener_xy, drums_xy)
        vocals_tdoa = get_src_tdoa(listener_xy, vocals_xy)
        other_tdoa = get_src_tdoa(listener_xy, other_xy)
        speech_tdoa = get_src_tdoa(listener_xy, speech_xy)

        bass_azi = get_src_azimuth(listener_xy, bass_xy, listener_azi)
        drums_azi = get_src_azimuth(listener_xy, drums_xy, listener_azi)
        vocals_azi = get_src_azimuth(listener_xy, vocals_xy, listener_azi)
        other_azi = get_src_azimuth(listener_xy, other_xy, listener_azi)
        speech_azi = get_src_azimuth(listener_xy, speech_xy, listener_azi)
    
        # Pad zeroes according to TDOAs of sources
        max_length = len(bass) + int(sr * max(bass_tdoa, drums_tdoa, vocals_tdoa, other_tdoa, speech_tdoa))
        bass_padded = np.pad(bass, (int(sr * bass_tdoa), max_length - int(sr * bass_tdoa) - len(bass)), 'constant')
        drums_padded = np.pad(drums, (int(sr * drums_tdoa), max_length - int(sr * drums_tdoa) - len(drums)), 'constant')
        vocals_padded = np.pad(vocals, (int(sr * vocals_tdoa), max_length - int(sr * vocals_tdoa) - len(vocals)), 'constant')
        other_padded = np.pad(other, (int(sr * other_tdoa), max_length - int(sr * other_tdoa) - len(other)), 'constant')
        speech_padded = np.pad(speech, (int(sr * speech_tdoa), max_length - int(sr * speech_tdoa) - len(speech)), 'constant')

        # mix
        track1 = TrackObject(name="speech", azimuth=speech_azi, elevation=0, level=speech_level, reverb=0.0, audio=speech_padded)
        track2 = TrackObject(name="bass", azimuth=bass_azi, elevation=0, level=bass_level, reverb=0.0, audio=bass_padded)
        track3 = TrackObject(name="drums", azimuth=drums_azi, elevation=0, level=drums_level, reverb=0.0, audio=drums_padded)
        track4 = TrackObject(name="vocals", azimuth=vocals_azi, elevation=0, level=vocals_level, reverb=0.0, audio=vocals_padded)
        track5 = TrackObject(name="other", azimuth=other_azi, elevation=0, level=other_level, reverb=0.0, audio=other_padded)

        # Place all TrackObject tracks in an array for mixdown
        tracks = [track1, track2, track3, track4, track5]

        # Mix the tracks
        output, output_tracks = mix_tracks_binaural(tracks, subject_id, sr, ir_type, speaker_layout, mode="planar", reverb_type="1")

        # Truncate output to length of reference
        output = output[:, 0:len(bass_padded)]
        output_tracks = output_tracks[:, :, 0:len(bass_padded)]
        music_tracks = output_tracks[1:]

        # Signal-to-noise ratio
        desired = np.sum(music_tracks, axis=0)
        noise = output - desired
        desired_lufs = sig_to_lufs(desired.T, sr)
        noise_lufs = sig_to_lufs(noise.T, sr)
        snr = (desired_lufs - noise_lufs)

        # Localization similarity
        nsim_values, locq = calculate_binaqual_sig(desired.T, output.T, sr)

        # append to lists
        song_id_arr.append(song_id)
        speech_id_arr.append(speech_id)
        motion_type_arr.append(motion_type)
        speech_xy_arr.append(speech_xy)
        data_points_arr.append(data_point)
        listener_xy_arr.append(listener_xy)
        listener_azi_arr.append(listener_azi)
        snr_arr.append(snr)
        locq_arr.append(locq)

        # Normalize output and write to wavfile
        output = loudness_normalize(output.T, sr, lufs=-30.0)
        sf.write(f'{mushra_folder}{song_id}_{speech_id}_{ir_type}_s{speech_direction}_uazi{listener_azi}_x{int(10*(listener_xy[0]+2.5)):02d}_y{int(10*(listener_xy[1]+2.5)):02d}.wav', output, sr)

num_entries = len(song_id_arr)

# create a data frame with the following columns
df = pd.DataFrame({
                'song_name': song_id_arr,
                'speech_name': speech_id_arr,
                'motion_type': motion_type_arr,
                'ir_type': [ir_type] * num_entries,
                'speech_xy': speech_xy_arr,
                'data_point': data_points_arr,
                'listener_x': [xy[0] for xy in listener_xy_arr], 'listener_y': [xy[1] for xy in listener_xy_arr],
                'listener_azi': listener_azi_arr,
                'snr': snr_arr, 
                'locq': locq_arr,
                })
df.to_csv(f'./output/mushra_{ir_type.lower()}/mushra_files_objective.csv')