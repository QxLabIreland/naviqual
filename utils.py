import math
import numpy as np
import librosa
import pyloudnorm as pyln

def get_src_level(user_xy, src_xy):
    # Get the level of the sound source given user location and source location

    distance = math.dist(user_xy, src_xy)
    min_distance = 1
    max_distance = 500

    if distance < min_distance:
        level = 1
    elif distance > max_distance:
        level = 0
    else:
        level = 1/distance
    return level

def get_src_tdoa(user_xy, src_xy, vs=343):
    # Get the time delay of arrival of the sound source given user location and source location

    distance = math.dist(user_xy, src_xy)
    tdoa = distance / vs
    return tdoa

def get_src_azimuth(user_xy, src_xy, user_azi):
    # Get the direction of the sound source with respect to the user given user location, source location, and user direction.
    
    # put source in front if listener is at the source spot
    if user_xy == src_xy:
        azimuth = 0
    else:
        angle = np.arctan2(src_xy[1] - user_xy[1], src_xy[0] - user_xy[0]) * 180 / np.pi
        azimuth = angle - 90 - user_azi
        azimuth = (azimuth + 360) % 360
    return azimuth

def sig_to_dbfs(sig, frame_length=2048, hop_length=512):
    # convert the signal values to dbfs

    rms = librosa.feature.rms(y=sig, frame_length=frame_length, hop_length=hop_length)      # take the rms for each frame
    dbfs = 20 * np.log10(rms * np.sqrt(2))      # convert to dBFS
    dbfs = np.clip(dbfs, a_max = 0, a_min=-96)     # possible dbFS value from 0 to -96 dbFS
    dbfs = dbfs.squeeze()     # convert from (2, 1, N) to (2, N)
    return dbfs

def sig_to_lufs(sig, sr):
    # convert the signal values to LUFS

    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(sig)
    return loudness

def loudness_normalize(sig, sr, lufs=-23.0):
    # apply loudness normalization to the signal

    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(sig)
    loudness_normalized_audio = pyln.normalize.loudness(sig, loudness, lufs)
    return loudness_normalized_audio

def normalize_data(data):
    # Normalize data between 0 and 1

    return (data - np.min(data)) / (np.max(data) - np.min(data))