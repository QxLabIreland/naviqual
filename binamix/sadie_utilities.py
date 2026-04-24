
import librosa
import os
import numpy as np
import binamix.surround_utilities as surround
from scipy.spatial import Delaunay
from scipy.signal import oaconvolve
import matplotlib.pyplot as plot

script_dir = os.path.dirname(os.path.abspath(__file__))
sadie_base_path = os.path.join(script_dir, "..", "sadie", "Database-Master_V2-1")
reverb_base_path = os.path.join(script_dir, "..", "reverb_IRs")

if not os.path.exists(sadie_base_path):
    raise FileNotFoundError(
        "SADIE II dataset not found. "
        "Please run 'binamix/sadie_db_setup.py' from the root directory to download the dataset."
    )


# Defining Path Structure of SADIE II dataset
brir_path_slug = "_BRIR_SOFA/"  # Slug for the BRIR subdirectory
hrir_path_slug = "_HRIR_SOFA/"  # Slug for the HRIR subdirectory
hrir_slug_44k = "_44K_16bit_256tap_FIR_SOFA.sofa"  # Slug for the 44.1 kHz 16-bit 256-tap FIR SOFA file
hrir_slug_48k = "_48K_24bit_256tap_FIR_SOFA.sofa"  # Slug for the 48 kHz 24-bit 256-tap FIR SOFA file
hrir_slug_96k = "_96K_24bit_512tap_FIR_SOFA.sofa"  # Slug for the 96 kHz 24-bit 512-tap FIR SOFA file
brir_slug_44k = "_44K_16bit_0.3s_FIR_SOFA.sofa"  # Slug for the 44.1 kHz 16-bit 256-tap FIR SOFA file
brir_slug_48k = "_48K_24bit_0.3s_FIR_SOFA.sofa"  # Slug for the 48 kHz 24-bit 256-tap FIR SOFA file
brir_slug_96k = "_96K_24bit_0.3s_FIR_SOFA.sofa"  # Slug for the 96 kHz 24-bit 512-tap FIR SOFA file

# If using WAV folder instead
brir_wav_path_slug = "_BRIR_WAV/"  # Folder slug for the WAV BRIR subdirectory
hrir_wav_path_slug = "_HRIR_WAV/"  # Folder slug for the WAV HRIR subdirectory
wav_slug_44k = "44K_16bit/"  # Folder slug for the 44.1 kHz 16-bit wav files
wav_slug_48k = "48K_24bit/"  # Folder slug for the 48 kHz 24-bit wav files
wav_slug_96k = "96K_24bit/"  # Folder slug for the 96 kHz 24-bit wav files

# Function to select the correct folder for the wav files based on Subject ID, sample rate and type (HRIR/BRIR)
def select_sadie_wav_subject(subject_id, sample_rate, file_type):
    # Check if subject_id is valid
    valid_subject_ids = ['D1', 'D2'] + [f'H{i}' for i in range(3, 21)]
    if subject_id not in valid_subject_ids:
        raise ValueError(f"Invalid subject_id: {subject_id} - Valid subject_ids are D1, D2, and H3 to H20")
    
    sub_folder = "/" + subject_id + "/"

    if file_type == "HRIR":
        if sample_rate == 44100:
            return sadie_base_path + sub_folder + subject_id + hrir_wav_path_slug + wav_slug_44k
        elif sample_rate == 48000:
            return sadie_base_path + sub_folder + subject_id + hrir_wav_path_slug + wav_slug_48k
        elif sample_rate == 96000:
            return sadie_base_path + sub_folder + subject_id + hrir_wav_path_slug + wav_slug_96k
        else:
            raise ValueError(f"Unsupported sample rate: {sample_rate} - Valid rates are 44100, 48000, 96000") 
    elif file_type == "BRIR":
        if sample_rate == 44100:
            return sadie_base_path + sub_folder + subject_id + brir_wav_path_slug + wav_slug_44k
        elif sample_rate == 48000:
            return sadie_base_path + sub_folder + subject_id + brir_wav_path_slug + wav_slug_48k
        elif sample_rate == 96000:
            return sadie_base_path + sub_folder + subject_id + brir_wav_path_slug + wav_slug_96k
        else:
            raise ValueError(f"Unsupported sample rate: {sample_rate} - Valid rates are 44100, 48000, 96000")
    else:
        raise ValueError(f"Unsupported IR type: {file_type} - Valid types are HRIR and BRIR")

# Function to select the correct SOFA file based on the subject ID, sample rate and type (HRIR/BRIR)
def select_sadie_sofa_subject(subject_id, sample_rate, file_type):
    # Check if subject_id is valid
    valid_subject_ids = ['D1', 'D2'] + [f'H{i}' for i in range(3, 21)]
    if subject_id not in valid_subject_ids:
        raise ValueError(f"Invalid subject_id: {subject_id} - Valid subject_ids are D1, D2, and H3 to H20")
    
    sub_folder = subject_id + "/"

    if file_type == "HRIR":
        if sample_rate == 44100:
            return sadie_base_path + sub_folder + subject_id + hrir_path_slug + subject_id + hrir_slug_44k
        elif sample_rate == 48000:
            return sadie_base_path + sub_folder + subject_id + hrir_path_slug + subject_id + hrir_slug_48k
        elif sample_rate == 96000:
            return sadie_base_path + sub_folder + subject_id + hrir_path_slug + subject_id + hrir_slug_96k
        else:
            raise ValueError(f"Unsupported sample rate: {sample_rate} - Valid rates are 44100, 48000, 96000") 
    elif file_type == "BRIR":
        if sample_rate == 44100:
            return sadie_base_path + sub_folder + subject_id + brir_path_slug + subject_id + brir_slug_44k
        elif sample_rate == 48000:
            return sadie_base_path + sub_folder + subject_id + brir_path_slug + subject_id + brir_slug_48k
        elif sample_rate == 96000:
            return sadie_base_path + sub_folder + subject_id + brir_path_slug + subject_id + brir_slug_96k
        else:
            raise ValueError(f"Unsupported sample rate: {sample_rate} - Valid rates are 44100, 48000, 96000")
    else:
        raise ValueError(f"Unsupported IR type: {file_type} - Valid types are HRIR and BRIR")

# Function to generate a SADIE II filename for a binaural audio file based on azimuth and elevation
def construct_wav_filename(azimuth, elevation):
    # Generates the correct SADIE II filename for a binaural audio file based on azimuth and elevation
    # Ensure both azimuth and elevation are represented with a decimal point,
    # converting to string with one decimal place, and replacing '.' with ','
    azimuth_str = f"{azimuth:.1f}".replace('.', ',')
    elevation_str = f"{elevation:.1f}".replace('.', ',')

    # Construct the filename using the specified format
    filename = f"azi_{azimuth_str}_ele_{elevation_str}.wav"
    return filename

# Function to load the WAV HRIR/BRIR data for a given subject, sample rate, type, azimuth and elevation
def load_sadie_ir(subject_id, sample_rate, ir_type, azimuth, elevation):
    # Load the HRIR/BRIR data for the specified subject, sample rate, type, azimuth and elevation
    
    # Select the correct file path based on the subject ID, sample rate and type 
    wav_file_path = select_sadie_wav_subject(subject_id, sample_rate, ir_type)

    # Construct the filename for the WAV file based on the azimuth and elevation
    wav_filename = construct_wav_filename(azimuth, elevation)
    
    # Combine the file path and filename to get the full file path
    filename = wav_file_path + wav_filename

    try:
        # Load the WAV file using the correct file path and filename
        y, sr = librosa.load(filename, sr=None, mono=False)
    except FileNotFoundError:
        raise FileNotFoundError(f"Try using ir_type: 'HRIR' instead because the subject_id: '{subject_id}', ir_type: '{ir_type}' does not have the necessary IR angles for the speaker_layout chosen")
    except Exception as e:
        raise RuntimeError(f"An error occurred while loading the file: {e}")

    return y

# Function to extract azimuth and elevation from a SADIE II filename
def extract_azimuth_elevation(filename):
    # Extract the azimuth and elevation from a SADIE II filename
    # Extract the azimuth and elevation from the filename
    filename = filename.replace('.wav', '')
    azimuth_str = filename.split('_')[1]
    elevation_str = filename.split('_')[3]

    # Convert the azimuth and elevation to float values
    azimuth = float(azimuth_str.replace(',', '.'))
    elevation = float(elevation_str.replace(',', '.'))

    return azimuth, elevation

# Function to return all available angles for a given subject and IR type
def get_available_angles(subject_id, sample_rate, ir_type, speaker_layout):
    # Get all available angles for a given subject and IR type
    # error handling
    if ir_type not in ['HRIR', 'BRIR']:
        raise ValueError(f"Invalid IR type: {ir_type} - Valid types are HRIR and BRIR")
    
    if sample_rate not in [44100, 48000, 96000]:
        raise ValueError(f"Invalid sample rate: {sample_rate} - Valid rates are 44100, 48000, 96000")

    if subject_id not in ['D1', 'D2'] + [f'H{i}' for i in range(3, 21)]:
        raise ValueError(f"Invalid subject ID: {subject_id} - Valid IDs are D1, D2, and H3 to H20")
    
    # Select the correct file path based on the subject ID, sample rate and type 
    wav_file_path = select_sadie_wav_subject(subject_id, sample_rate, ir_type)

    # Get a list of all the WAV files in the directory
    wav_files = [file for file in os.listdir(wav_file_path) if file.endswith('.wav')]

    # Extract the azimuth and elevation from each filename
    angles = [extract_azimuth_elevation(file) for file in wav_files]

    # Filter the angles based on the speaker layout and return the filtered list
    if speaker_layout in surround.supported_layouts():    
        channels = surround.get_channel_angles(speaker_layout)
        
        # remove the Lfe channel as it is not relevant for binaural rendering other than direct binarual renders of channel encoded surround
        channels = [channel for channel in channels if channel.name != 'Lfe']
        
        angles = [(channel.azi, channel.ele) for channel in channels]

    elif speaker_layout == "none":
        angles = angles
    else:
        print(f"Invalid speaker layout: '{speaker_layout}' - Using all available angles")

    return angles

# Function to return the nearest available angle to a given azimuth and elevation
def get_nearest_angle(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation):
    # Get the nearest available angle to a given azimuth and elevation

    # Get all available angles for the specified subject and IR type
    available_angles = get_available_angles(subject_id, sample_rate, ir_type, speaker_layout)

    # Calculate the difference between the specified azimuth and elevation and each available angle using cartesian coordinates
    differences = [get_angle_distance(azimuth, elevation, angle[0], angle[1]) for angle in available_angles]

    # Find the index of the angle with the smallest difference
    nearest_index = differences.index(min(differences))

    # Return the nearest angle
    return available_angles[nearest_index]

# Function to get nearest angle with elevation
def get_nearest_elevation_angle(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation):
    # Get the nearest available angle to a given azimuth and elevation

    # Get all available angles for the specified subject and IR type
    available_angles = get_available_angles(subject_id, sample_rate, ir_type, speaker_layout)

    # Filter the available angles to only include those with elevation
    available_elevation_angles = [angle for angle in available_angles if angle[1] != 0]

    # If there is no elevation angle, return null
    if len(available_elevation_angles) == 0:
        return 'null', 'null'
    
    # Calculate the difference between the specified azimuth and elevation and each available angle using cartesian coordinates
    differences = [get_angle_distance(azimuth, elevation, angle[0], angle[1]) for angle in available_elevation_angles]

    # Find the index of the angle with the smallest difference
    nearest_index = differences.index(min(differences))

    # Return the nearest angle
    return available_elevation_angles[nearest_index], min(differences)

# Function to convert azimuth and elevation to cartesian coordinates
def spherical_to_cartesian(azimuth, elevation):
    # Convert azimuth and elevation to cartesian coordinates
    x = np.cos(np.radians(azimuth)) * np.cos(np.radians(elevation))
    y = np.sin(np.radians(azimuth)) * np.cos(np.radians(elevation))
    z = np.sin(np.radians(elevation))

    # Format the coordinates to standard float notation
    x = float(f"{x:.6f}")
    y = float(f"{y:.6f}")
    z = float(f"{z:.6f}")

    point = np.array([x, y, z])
    return point

def cartesian_to_spherical(x, y, z):
    azimuth = np.degrees(np.arctan2(y, x))
    elevation = np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2)))

    azimuth = (azimuth + 360) % 360
    elevation = ((elevation + 360) % 360)
    return np.array([azimuth, elevation])

# Function to get the difference between two angles specified in azimuth and elevation
def get_angle_distance(azimuth1, elevation1, azimuth2, elevation2):
    # Get the difference between two angles specified in azimuth and elevation
    # Convert to cartesian coordinates first
    point1 = spherical_to_cartesian(azimuth1, elevation1)
    point2 = spherical_to_cartesian(azimuth2, elevation2)

    # Calculate the difference between the two xyz coordinates
    dist = np.linalg.norm(point1 - point2)

    return dist

# Function to check if a specified angle exists for a given subject, sample rate and IR type
def angle_exists(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation):
    # Check if the specified angle exists for the given subject, sample rate and IR type

    # Get all available angles for the specified subject and IR type
    available_angles = get_available_angles(subject_id, sample_rate, ir_type, speaker_layout)

    # Check if the specified angle is in the list of available angles
    if (azimuth, elevation) in available_angles:
        return True
    else:
        return False

# Function to check if the speaker layout has elevation speakers
def has_elevation_speakers(speaker_layout):
    # Check if the speaker layout has elevation speakers
    
    # First check if the speaker layout is "none". This means we are using a full set of SADIE IRs
    if speaker_layout == "none":
        return True      
    
    angles = surround.get_channel_angles(speaker_layout)
    
    elevations = [angle.ele for angle in angles]
    
    if any(elevation != 0 for elevation in elevations):
        return True
    else:
        return False

# Function to get azimuth neighbours on nearest plane
def get_planar_neighbours(available_angles, azimuth, elevation, verbose=True):
    # Get the 'nearest plane' azimuth neighbours of a given angle.
    
    # convert desired angle to range 0-360
    azimuth = (azimuth + 360) % 360
   
    # put all unique elavation angles in a list
    elevation_angles = list(set([angle[1] for angle in available_angles]))

    # find the nearest elevation angle in the list to our desired elavation
    nearest_elevation = min(elevation_angles, key=lambda x:abs(x-elevation))
    print(f"Using nearest planar neighbours on elevation plane {nearest_elevation}°")

    # filter only nearest elevation angles
    available_angles = [angle for angle in available_angles if angle[1] == nearest_elevation]

    # find angle with smallest and largest azimuth
    min_azimuth = min([angle[0] for angle in available_angles])
    max_azimuth = max([angle[0] for angle in available_angles])

    # account for circular wrapping
    available_angles.append((min_azimuth + 360, nearest_elevation))
    available_angles.append((max_azimuth - 360, nearest_elevation))

    differences = [angle[0] - azimuth for angle in available_angles]

    # find index of smallest negative difference
    left_index = differences.index(max([diff for diff in differences if diff <= 0]))
   
    # find index of smallest positive difference
    right_index = differences.index(min([diff for diff in differences if diff > 0]))
    
    if azimuth <= 180:
        angle1 = available_angles[left_index]
        angle2 = available_angles[right_index]
        angle3 = available_angles[right_index]
    else:
        angle1 = available_angles[right_index]
        angle2 = available_angles[left_index]
        angle3 = available_angles[left_index]

    three_angles = [angle1, angle2, angle3]

    # convert back to range 0-360
    three_angles = [((angle[0] + 360) % 360, angle[1]) for angle in three_angles]

    if verbose:
        print(available_angles)
        print("difference", differences)
        print(azimuth)
        print(three_angles)
       

    return three_angles


# Function to get max and min elevation from a speaker layout
def get_elevation_range(available_angles):
    # Get the maximum and minimum elevation from a speaker layout
    
    angles = available_angles
    elevations = [angle[1] for angle in angles]
    max_elevation = max(elevations)
    min_elevation = min(elevations)
    
    return min_elevation, max_elevation

# Function to generate an interpolated HRIR/BRIR for a given subject, sample rate, IR type, speaker layout, azimuth and elevation
def generate_sadie_ir(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation, mode="auto", verbose=True):
    
    if mode not in ["auto", "nearest", "planar", "two_point", "three_point"]:
        raise ValueError(f"Invalid mode: {mode} - Valid modes are 'auto', 'nearest', 'planar', 'two_point', 'three_point'")

    nearest_angle = get_nearest_angle(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation)
    distance_threshold = .035              # Distance = 2 degrees to approximate JND for frontal auditory localisation
    use_2_point_interp = False                # Initialise 2 point interpolation flag
    use_3_point_interp = False                # Initialise 3 point interpolation flag

    # Get all available angles for the specified subject, IR type AND speaker layout
    available_angles = get_available_angles(subject_id, sample_rate, ir_type, speaker_layout)

    # test1 = get_planar_neighbours(available_angles, azimuth, elevation, verbose=False)
    # print("Planar Neighbours", test1)



    # Convert minus angles to positive
    azimuth = (azimuth + 360) % 360
    
    # Check if the speaker layout has elevation speakers - if not, set elevation to 0
    if not has_elevation_speakers(speaker_layout):
        azimuth = azimuth
        elevation = 0
        print("Destination speaker layout has no elevation speakers. Setting elevation to 0")

    # -----------------------------------------------------

    # Interpolation Mode Conditions

    print(f"Interpolation Mode: '{mode.capitalize()}'")

    if mode == "nearest":
        # Use the nearest angle
        print(f"Desired Angle: ({azimuth}, {elevation})")
        print(f"Using Nearest Angle: ({nearest_angle[0]}, {nearest_angle[1]})")
        ir = load_sadie_ir(subject_id, sample_rate, ir_type, nearest_angle[0], nearest_angle[1])
        return ir
    
    if mode == "planar":
        # Use the nearest angle on the same elevation plane
        use_2_point_interp = True
    
    if mode == "two_point":
        # Use 2 point interpolation
        use_2_point_interp = True

    if mode == "three_point":
        # Use 3 point interpolation
        use_3_point_interp = True

    # Check if the specified angle exists for the given subject, sample rate and IR type
    if angle_exists(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation):
        # If the desired angle exists, load the HRIR/BRIR data for that angle
        print("Using Actual Angle to achieve angle: az", azimuth, "ele", elevation)
        ir = load_sadie_ir(subject_id, sample_rate, ir_type, azimuth, elevation)

    elif get_angle_distance(azimuth, elevation, nearest_angle[0], nearest_angle[1]) < distance_threshold:
        # If the desired angle does not exist, but is within the distance threshold, use the nearest angle
        print("Using Nearest Angle", nearest_angle, "to achieve angle: az", azimuth, "ele", elevation)
        ir = load_sadie_ir(subject_id, sample_rate, ir_type, nearest_angle[0], nearest_angle[1])

    else:
        # If angle does not exist and there is no close proxy, 
        # generate an interpolated HRIR/BRIR using the nearest available angles based on the mode selected
       
        if has_elevation_speakers(speaker_layout):
            # Get the 3 points surrounding the desired angle using modified delaunay triangulation
            three_points = delaunay_triangulation(available_angles, azimuth, elevation, speaker_layout, plots=False)
        
        if not has_elevation_speakers(speaker_layout) or mode == "planar":
            # If there are no elevation speakers in the speaker layout, use 2 neighbouring angles on the 0 elevation plane.
            # *returns 3 angles for consistency with the later methods but only 2 are used
            three_points = get_planar_neighbours(available_angles, azimuth, elevation, verbose=False)
                
        # ----------------------------------------------------- 
        # Calculate the difference between the specified azimuth and elevation and each angle by converting each to cartesian first

        differences = [get_angle_distance(azimuth, elevation, angle[0], angle[1]) for angle in three_points]

        # Order the angles by difference - closest first
        nearest_indices = sorted(range(len(differences)), key=lambda i: differences[i])
        
        angle1 = three_points[nearest_indices[0]]
        angle1_diff = differences[nearest_indices[0]]
        inv_angle1_diff = 1 / angle1_diff if angle1_diff != 0 else float('inf')
        # print("Angle 1 ", angle1, "{:.3f}".format(angle1_diff))

        angle2 = three_points[nearest_indices[1]]
        angle2_diff = differences[nearest_indices[1]]
        inv_angle2_diff = 1 / angle2_diff if angle2_diff != 0 else float('inf')
        # print("Angle 2 ", angle2, "{:.3f}".format(angle2_diff))

        angle3 = three_points[nearest_indices[2]]
        angle3_diff = differences[nearest_indices[2]]
        inv_angle3_diff = 1 / angle3_diff if angle3_diff != 0 else float('inf')
        # print("Angle 3 ", angle3, "{:.3f}".format(angle3_diff))
        
        # -----------------------------------------------------

        # convert to cartesian
        angle1_cart = spherical_to_cartesian(angle1[0], angle1[1])
        angle2_cart = spherical_to_cartesian(angle2[0], angle2[1])
        angle3_cart = spherical_to_cartesian(angle3[0], angle3[1])

        # -----------------------------------------------------
        
        # Try all 2 point interpolation combinations cartesian
       
        # Point 1 to Point 2
        sum_p1p2_inv_diffs = inv_angle1_diff + inv_angle2_diff
        w1_p1p2 = inv_angle1_diff / sum_p1p2_inv_diffs
        w2_p1p2 = inv_angle2_diff / sum_p1p2_inv_diffs

        angle_p1p2 = (w1_p1p2 * angle1_cart) + (w2_p1p2 * angle2_cart)
        angle_p1p2 = cartesian_to_spherical(angle_p1p2[0], angle_p1p2[1], angle_p1p2[2]) 
        angle_p1p2_diff = get_angle_distance(azimuth, elevation, angle_p1p2[0], angle_p1p2[1])
        
        # Point 1 to Point 3
        sum_p1p3_inv_diffs = inv_angle1_diff + inv_angle3_diff
        w1_p1p3 = inv_angle1_diff / sum_p1p3_inv_diffs
        w2_p1p3 = inv_angle3_diff / sum_p1p3_inv_diffs

        angle_p1p3 = (w1_p1p3 * angle1_cart) + (w2_p1p3 * angle3_cart)
        angle_p1p3 = cartesian_to_spherical(angle_p1p3[0], angle_p1p3[1], angle_p1p3[2])
        angle_p1p3_diff = get_angle_distance(azimuth, elevation, angle_p1p3[0], angle_p1p3[1])

        # check which 2 point interpolation is better
        min_diff_index, min_diff = min(enumerate([angle_p1p2_diff, angle_p1p3_diff]), key=lambda x: x[1])

        if min_diff_index == 0:
            # Point 1 to Point 2
            w1_2p = w1_p1p2
            w2_2p = w2_p1p2
            best_angle1 = angle1
            best_angle2 = angle2
            angle_diff_2_point_interp = angle_p1p2_diff
            interp_with_two = angle_p1p2
        else:
            # Point 1 to Point 3
            w1_2p = w1_p1p3
            w2_2p = w2_p1p3
            best_angle1 = angle1
            best_angle2 = angle3
            angle_diff_2_point_interp = angle_p1p3_diff
            interp_with_two = angle_p1p3

        # -----------------------------------------------------

        # Try 3 point interpolation cartesian
        sum_3_inv_diffs = inv_angle1_diff + inv_angle2_diff + inv_angle3_diff
        w1_3p = inv_angle1_diff / sum_3_inv_diffs
        w2_3p = inv_angle2_diff / sum_3_inv_diffs
        w3_3p = inv_angle3_diff / sum_3_inv_diffs
       
        w3_sum = (w1_3p * angle1_cart) + (w2_3p * angle2_cart) + (w3_3p * angle3_cart) 
        interp_with_three = cartesian_to_spherical(w3_sum[0], w3_sum[1], w3_sum[2])
        angle_diff_3_point_interp = get_angle_distance(azimuth, elevation, interp_with_three[0], interp_with_three[1])

        # -----------------------------------------------------

        if verbose:
            print("Speaker Layout:", speaker_layout)
            print(f"Desired Angle: ({azimuth}, {elevation})")
            print("")
            print("Nearest angle p1:" , angle1, "| Difference:", "{:.2f}".format(angle1_diff))
            print("Nearest angle p2:" , angle2, "| Difference:", "{:.2f}".format(angle2_diff))
            print("Nearest angle p3:" , angle3, "| Difference:", "{:.2f}".format(angle3_diff))

            
            print("\nChecking Angle Options...")
            print("Angle difference to nearest actual angle ->", "({:.2f}, {:.2f})".format(angle1[0], angle1[1]), "Difference | {:.3f}".format(angle1_diff))
            print("Interpolated Angle using 2pts [p1 & p2] ->", "({:.2f}, {:.2f})".format(angle_p1p2[0], angle_p1p2[1]), " Difference |", "{:.3f}".format(angle_p1p2_diff), "  Weights |", "{:.3f}".format(w1_p1p2), "{:.3f}".format(w2_p1p2))
            print("Interpolated Angle using 2pts [p1 & p3] ->", "({:.2f}, {:.2f})".format(angle_p1p3[0], angle_p1p3[1]), " Difference |","{:.3f}".format(angle_p1p3_diff), "  Weights |", "{:.3f}".format(w1_p1p3), "{:.3f}".format(w2_p1p3))
            print("Interpolated Angle using 3pts [p1 p2 p3] ->", "({:.2f},".format(interp_with_three[0]), "{:.2f})".format(interp_with_three[1]), " Difference |","{:.3f}".format(angle_diff_3_point_interp))
           
            
        print(f"\nDesired Angle: ({azimuth}, {elevation})")

        # -------------REMOVED AT TIME OF MODE ADDITION--Reconsider later----------------------
        # -----------------------------------------------------
        # # Check if the desired point is on the same elevation plane as the nearest angles
        # # This assumes uniform sampling on that plane but not uniform sampling overall
        # if angle1[1] == angle2[1] == elevation:
        #     use_2_point_interp = True   

        # # Check if 2 point interpolation is better than or within a trade off difference of 3 point interpolation because 3 point interpolation colours the sound too much
        # trade_off = 0.06
        # if np.abs(angle_diff_2_point_interp - angle_diff_3_point_interp) < trade_off:
        #     print("3 point and 2 point interpolation are within trade off difference of", trade_off, "therefore")
        #     use_2_point_interp = True
        # -----------------------------------------------------
        
        # With all above conditions met, decide which interpolation to use
        if (angle_diff_2_point_interp <= angle_diff_3_point_interp and not use_3_point_interp) or use_2_point_interp:
                
            if np.abs(angle_diff_2_point_interp - angle1_diff) > 0.0005:
                # If 2 point interpolation is better, or it is the user specified interpolation use 2 point
                print("Using 2 Point Interpolation to achieve cartesian angle estimate: ({:.2f}, {:.2f})".format(interp_with_two[0], interp_with_two[1]))
                print("Angles used:", best_angle1, best_angle2)

                angle1_ir = load_sadie_ir(subject_id, sample_rate, ir_type, best_angle1[0], best_angle1[1])
                angle2_ir = load_sadie_ir(subject_id, sample_rate, ir_type, best_angle2[0], best_angle2[1])

                ir = angle1_ir * w1_2p + angle2_ir * w2_2p
            
            else:
                # If 2 point interpolation is not better, use the nearest angle
                print("Using Nearest Angle to achieve angle: ({:.2f}, {:.2f})".format(nearest_angle[0], nearest_angle[1]))
                ir = load_sadie_ir(subject_id, sample_rate, ir_type, nearest_angle[0], nearest_angle[1])
        
        elif (angle_diff_3_point_interp < angle_diff_2_point_interp) or use_3_point_interp:
            # If 3 point interpolation is better, or it is the user specified interpolation use 3 point
            print("Using 3 Point Interpolation to achieve cartesian angle estimate: ({:.2f}, {:.2f})".format(interp_with_three[0], interp_with_three[1]))
            print(angle1, angle2, angle3)

            angle1_ir = load_sadie_ir(subject_id, sample_rate, ir_type, angle1[0], angle1[1])
            angle2_ir = load_sadie_ir(subject_id, sample_rate, ir_type, angle2[0], angle2[1])
            angle3_ir = load_sadie_ir(subject_id, sample_rate, ir_type, angle3[0], angle3[1])

            ir = angle1_ir * w1_3p + angle2_ir * w2_3p + angle3_ir * w3_3p

        else:
            # If none of the conditions are met, use the nearest angle
            print("Something went wrong: ussing nearest angle to achieve angle: ({:.2f}, {:.2f})".format(nearest_angle[0], nearest_angle[1]))
            ir = load_sadie_ir(subject_id, sample_rate, ir_type, nearest_angle[0], nearest_angle[1])

    
    print("-----------------------------------")
    

    return ir


def vbap_3d(pan_az_el, spk1_az_el, spk2_az_el, spk3_az_el, degrees=True):
    def azel_to_unit(az, el):
        if degrees:
            az = np.deg2rad(az)
            el = np.deg2rad(el)
        ce = np.cos(el)
        return np.array([ce * np.cos(az), ce * np.sin(az), np.sin(el)], dtype=float)

    p  = azel_to_unit(*pan_az_el)
    s1 = azel_to_unit(*spk1_az_el)
    s2 = azel_to_unit(*spk2_az_el)
    s3 = azel_to_unit(*spk3_az_el)

    M = np.column_stack((s1, s2, s3))  # 3x3

    # Solve M g = p
    try:
        g = np.linalg.solve(M, p)
    except np.linalg.LinAlgError:
        return np.array([0.0, 0.0, 0.0])

    # Clamp negatives (safety; ideally triangle selection avoids this)
    g = np.maximum(g, 0.0)

    # Constant power normalization
    norm = np.linalg.norm(g)
    if norm > 1e-12:
        g /= norm

    return g


def vbap_2d(pan_az_el, spk1_az_el, spk2_az_el, degrees=True):
    def azel_to_unit_xy(az, el):
        if degrees:
            az = np.deg2rad(az)
            # el is intentionally ignored in 2D
        return np.array([np.cos(az), np.sin(az)], dtype=float)

    p  = azel_to_unit_xy(*pan_az_el)
    s1 = azel_to_unit_xy(*spk1_az_el)
    s2 = azel_to_unit_xy(*spk2_az_el)

    M = np.column_stack((s1, s2))  # 2x2

    # Solve M g = p
    try:
        g = np.linalg.solve(M, p)
    except np.linalg.LinAlgError:
        return np.array([0.0, 0.0])

    # Clamp negatives (safety; ideally pair selection avoids this)
    g = np.maximum(g, 0.0)

    # Constant power normalization
    norm = np.linalg.norm(g)
    if norm > 1e-12:
        g /= norm
    else:
        return np.array([0.0, 0.0])

    return g


def generate_surround_channel_gains(azimuth, elevation, speaker_layout, verbose=True):

    # Check speaker layout validity
    if speaker_layout not in surround.supported_layouts():
        raise ValueError("Unsupported Speaker Layout")

    # Get channel angles for the specified speaker layout (will include LFE at 0 degrees - channel 3)
    channels = surround.get_channel_angles(speaker_layout)

    # Extract channel angles
    available_angles = [(channel.azi, channel.ele) for channel in channels]
    # print("Channel Angles:", available_angles)

    
    # Check if the speaker layout has elevation speakers - if not, set elevation to 0
    if not has_elevation_speakers(speaker_layout):
        elevation = 0
        if verbose:
            print("Destination speaker layout has no elevation speakers. Setting elevation to 0")

        bounding_points = get_planar_neighbours(available_angles, azimuth, elevation, verbose=False)
        bounding_points = bounding_points[:-1]  # remove the duplicate point used for other functions
        if verbose:
            print("Bounding points shape:", bounding_points)

        gains = vbap_2d((azimuth, elevation), bounding_points[0], bounding_points[1], degrees=True)

        if verbose:
            print("VBAP Gains:", gains)   

    else:
        # Get 3 bounding channel angles for desired pan location
        bounding_points = delaunay_triangulation(available_angles, azimuth, elevation, speaker_layout, plots=False)
        if verbose:
            print("Bounding Speaker Angles:", bounding_points)

         # Calculate VBAP gains
        gains = vbap_3d((azimuth, elevation), bounding_points[0], bounding_points[1], bounding_points[2], degrees=True)
        if verbose:
            print("VBAP Gains:", gains)
        
    

    # for each angle in bounding points, find the corresponding speakerchannel index
    channel_indices = []
    for point in bounding_points:
        index = next((i for i, channel in enumerate(channels) if (channel.azi, channel.ele) == point), None)
        if index is not None:
            channel_indices.append(index)

    if verbose:
        print("Channel Indices:", channel_indices)
    # Print channel names
    channel_names = [channels[i].name for i in channel_indices]
    if verbose:
        print("Channel Names:", channel_names)

    # Create channel weights
    channel_gains = np.zeros(len(channels))
    channel_gains[channel_indices] = gains

    # print("Channel Gain Array:", np.array2string(channel_gains, formatter={'float_kind':lambda x: f"{x:.2f}"}))
    # Print all channel names highlighting the ones from bounding, including channel number and gain
    if verbose:
        print("Channel Gain Array:")
        for i, channel in enumerate(channels):
            gain = float(channel_gains[i]) if i < len(channel_gains) else 0.0
        
            if i in channel_indices:
                print(f"  * [{i}] {channel.name}: {gain:.2f}")
            else:
                print(f"    [{i}] {channel.name}: {gain:.2f}")

    return channel_gains



# Function to calculate Delaunay triangulation for a given set of points on a 2D plane
def delaunay_triangulation(available_angles, azimuth, elevation, speaker_layout, plots=True):
    
    # Delaunay triangulation is normally used 2D and 3D triangulation in cartesian coordinates.
    # This function considers the angles and elevations to be an equirectangular projection of the sphere 
    # which is valid to find the bounding triangle for the desired angle but not valid to calculate distances.
    # The distances are calculated elsewhere using cartesian conversion and euclidean distance.

    # check elevation range and adjust out of bounds if needed
    min_elevation, max_elevation = get_elevation_range(available_angles)
    if speaker_layout != "none":
        if elevation < min_elevation:
            elevation = min_elevation
            print("Desired elevation is not possible with this speaker layout, setting elevation to :", elevation)
        if elevation > max_elevation:
            elevation = max_elevation
            print("Desired elevation is not possible with this speaker layout, setting elevation to :", elevation)
    
    # Exit if max elvation is 0 indicating no elevation speakers. Delauneay triangulation is not needed
    if max_elevation == 0:
        raise ValueError("Speaker layout has no elevation speakers. Use an alternative method to find the nearest angle.")
    
    # Convert desired angle to 0 - 360 range
    azimuth = (azimuth + 360) % 360
    elevation = (elevation + 360) % 360
    
    # Keep a copy of all angles in unrotated form
    unrotated_angles = np.array(available_angles)

    # convert all angles greater than 180 to negative for symetrical plotting and for to deal with wrap around
    available_angles = [(angle[0] - 360, angle[1]) if angle[0] > 180 else angle for angle in available_angles]
    azimuth = azimuth - 360 if azimuth > 180 else azimuth
    elevation = elevation - 360 if elevation > 180 else elevation


    # Perform Delaunay triangulation
    points = (np.array(available_angles))
    tri = Delaunay(points)
    desired_point = np.array([[azimuth, elevation]])    # Input query point
    triangle_index = tri.find_simplex(desired_point)    # Find the triangle containing the query point

    if triangle_index == -1:
        print("The query point is outside the triangulation range. Trying 360 azimuth rotation...")

        # convert all minus angles to 0 -360 range
        available_angles = [(angle[0] + 360, angle[1]) if angle[0] < 0 else angle for angle in available_angles]
        azimuth = azimuth + 360 if azimuth < 0 else azimuth
        elevation = elevation - 360 if elevation > 180 else elevation # elevation is always + / - range so keep as was

        # Perform Delaunay triangulation
        points = (np.array(available_angles))
        tri = Delaunay(points)
        desired_point = np.array([[azimuth, elevation]])    # Input query point
        triangle_index = tri.find_simplex(desired_point)    # Find the triangle containing the query point

    if triangle_index == -1:
        print("The query point is still outside the triangulation range. Trying 180 elevation rotation...")

        # convert all minus angles to 0 -360 range
        available_angles = [(angle[0], angle[1]+360) if angle[1] < 0 else angle for angle in available_angles]
        # azimuth = azimuth + 360 if azimuth < 0 else azimuth
        elevation = elevation + 360 if elevation < 0 else elevation # elevation is always + / - range so keep as was

        # Perform Delaunay triangulation
        points = (np.array(available_angles))
        tri = Delaunay(points)
        desired_point = np.array([[azimuth, elevation]])    # Input query point
        triangle_index = tri.find_simplex(desired_point)    # Find the triangle containing the query point

    vertices = tri.simplices[triangle_index]
    triangle_points = unrotated_angles[vertices]
    plot_points = points[vertices]

    print("")
    
    if plots:   
        # Plot the triangulation and highlight the query point and the triangle
        plot.triplot(points[:, 0], points[:, 1], tri.simplices, color='blue')
        plot.plot(points[:, 0], points[:, 1], 'o', color='red')
        plot.plot(desired_point[:, 0], desired_point[:, 1], 'x', color='black', markersize=8, markeredgewidth=2)
        
        # Highlight the triangle
        plot.fill(plot_points[0][:, 0], plot_points[0][:, 1], color='gray', alpha=0.4, label='Containing Triangle')

        plot.title(f"Triangle Containing the Desired Angle ({azimuth}, {elevation}) for Layout = ({speaker_layout}) ", fontsize=8) 
        

        plot.gca().invert_xaxis()

        # label points
        # for i, txt in enumerate(available_angles):
        #     plot.annotate(f"{txt}", (points[i][0], points[i][1]), fontsize=8, ha='center', va='top')

        plot.xlabel("Azimuth")
        plot.ylabel("Elevation")
        
        # plot.ylim(-90, 90)
        plot.show()

    
    # Flatten the triangle points array
    triangle_points = [(float(coord[0]), float(coord[1])) for sublist in triangle_points for coord in sublist]
    
    # convert azimuths to range 0 - 360
    triangle_points = [(angle[0] + 360, angle[1]) if angle[0] < 0 else angle for angle in triangle_points]

    return triangle_points

# Function to render source for any given location, subject, sample rate, IR type and speaker layout
def render_source(input_file, subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation, mode="auto"):
    # Render the source for a given location, subject, sample rate, IR type and speaker layout

    # Generate the HRIR/BRIR for the specified location
    ir = generate_sadie_ir(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation, mode=mode)

    output = np.convolve(input_file, ir[0])
    output = np.vstack([output , np.convolve(input_file, ir[1])])

    return output

# Function to pan a source using amplitude panning
def pan_source(pan, input_file):
    # Pan a source using amplitude panning

    # Check if pan is within the valid range
    if pan < -1 or pan > 1:
        raise ValueError("Pan value must be between -1 and 1")

    # Convert -1 to 1 range into 0 to 1 range
    pan = (pan + 1) / 2 

    # Use constant power panning law
    gain_l = np.cos(pan * np.pi / 2)
    gain_r = np.sin(pan * np.pi / 2)

    # Apply the gains to the input file to pan the source
    output = np.vstack([input_file * gain_l, input_file * gain_r])

    return output

def mix_tracks_binaural(tracks, subject_id, sample_rate, ir_type, speaker_layout, mode="auto", reverb_type='1'):
    # Render the mix for a given tracks object, subject, IR type and speaker layout

    # Check if tracks is not an array
    if not isinstance(tracks, list):
        raise ValueError("Tracks must be an array of TrackObjects as defined in the TrackObject class in sadie_utilities.py")
    # If it is an array, check if each element is a track object
    for track in tracks:
        if not isinstance(track, TrackObject):
            raise ValueError("Each element in the tracks array must be a TrackObject as defined in the TrackObject class in sadie_utilities.py")

    # Check if all tracks have the same dimensions
    track_lengths = [len(track.audio) for track in tracks]
    if not all(length == track_lengths[0] for length in track_lengths):
        raise ValueError("All tracks must have the same length")
    
    # Check if all tracks have azimuth and elevation
    for track in tracks:
        if track.azimuth is None or track.elevation is None:
            raise ValueError("All tracks must have azimuth and elevation specified")

    # load reverb IR
    if reverb_type == '1':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "lecture_theatre.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '2':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "office.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '3':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "small_room.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '4':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "meeting_room.wav"), sr=sample_rate, mono=True)
    else:
        raise ValueError("Invalid reverb type. Choose from 1, 2, 3, or 4")
    
    ir_length = len(reverb_ir)-1

    print("Rendering Mix...")

    # Render and sum the sources for each track
    output_tracks = []
    for i, track in enumerate(tracks):
        print("Mixing ",track.name)
        if i == 0:
            
            if track.reverb != 0:
                print("Adding Reverb (",track.reverb,") to ",track.name)
                reverb = oaconvolve(track.audio, reverb_ir, mode='full')

                first_source = (reverb * track.reverb) + (np.pad(track.audio,(0, ir_length), 'constant') * (1-track.reverb))
            else:
                first_source = np.pad(track.audio,(0, ir_length), 'constant')
            
            first_source = render_source(first_source, subject_id, sample_rate, ir_type, speaker_layout, track.azimuth, track.elevation, mode) * track.level
            
            output = first_source
            output_tracks.append(first_source)
        else:
            
            if track.reverb != 0:
                print("Adding Reverb (",track.reverb,") to ",track.name)
                reverb = oaconvolve(track.audio, reverb_ir, mode='full')

                next_source = (reverb * track.reverb) + (np.pad(track.audio,(0, ir_length), 'constant') * (1-track.reverb))
            else:
                next_source = np.pad(track.audio,(0, ir_length), 'constant')
            
            next_source = render_source(next_source, subject_id, sample_rate, ir_type, speaker_layout, track.azimuth, track.elevation, mode) * track.level
            
            output += next_source
            output_tracks.append(next_source)

    return output, np.array(output_tracks)

def mix_tracks_surround(tracks, sample_rate, speaker_layout, reverb_type='1', verbose = False, plots=False):
    # Render the mix for a given tracks object, subject, IR type and speaker layout

    # Check if tracks is not an array
    if not isinstance(tracks, list):
        raise ValueError("Tracks must be an array of TrackObjects as defined in the TrackObject class in sadie_utilities.py")
    # If it is an array, check if each element is a track object
    for track in tracks:
        if not isinstance(track, TrackObject):
            raise ValueError("Each element in the tracks array must be a TrackObject as defined in the TrackObject class in sadie_utilities.py")

    # Check if all tracks have the same dimensions
    track_lengths = [len(track.audio) for track in tracks]
    if not all(length == track_lengths[0] for length in track_lengths):
        raise ValueError("All tracks must have the same length")
    
    # Check if all tracks have azimuth and elevation
    for track in tracks:
        if track.azimuth is None or track.elevation is None:
            raise ValueError("All tracks must have azimuth and elevation specified")

    # load reverb IR
    if reverb_type == '1':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "lecture_theatre.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '2':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "office.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '3':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "small_room.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '4':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "meeting_room.wav"), sr=sample_rate, mono=True)
    else:
        raise ValueError("Invalid reverb type. Choose from 1, 2, 3, or 4")
    
    # # Create array of tracks with reverb and level applied according the tracks object mix params
    
    ir_length = len(reverb_ir)-1

    if verbose:
        print(f"\nGenerating ({speaker_layout}) Surround Mix...")

    # Assume all tracks have same length
    output_length = len(tracks[0].audio) + ir_length

    # Preallocate 2D array: shape = (num_tracks, output_length)
    processed_tracks = np.zeros((len(tracks), output_length), dtype=np.float32)

    for i, track in enumerate(tracks):

        if verbose:
            print("Adding Reverb (", track.reverb, ") and Gain (", track.level, ") to", track.name)

        # Convolve with IR
        reverb_audio = oaconvolve(track.audio, reverb_ir, mode='full')

        # Pad dry signal
        dry_audio = np.pad(track.audio, (0, ir_length), 'constant')

        # Mix dry/wet and apply level
        processed_track = (reverb_audio * track.reverb + dry_audio * (1 - track.reverb)) * track.level

        # Store in matrix
        processed_tracks[i, :] = processed_track

    # Get surround channel gains for each track

    if verbose:
        print(f"\nCalculating surround channel gains for each track azimuth and elevation using VBAP...")

    channel_gains = []

    for track in tracks:
        gains = generate_surround_channel_gains(track.azimuth, track.elevation, speaker_layout, verbose=False)
        channel_gains.append(gains)

    if verbose:
        print(f"\nSurround channel gains for each track in presentation order:")

    # Get channel names from the surround layout for column headers
    channel_spec = surround.get_channel_angles(speaker_layout)
    channel_names = [ch.name for ch in channel_spec]

    if verbose:
        # Print header row
        header_cols = ["Track", "Azi", "Ele"] + channel_names
        header = "\t".join(header_cols)
        underline = "\t".join("-" * len(col) for col in header_cols)
        print(header)
        print(underline)

        # Print each track's gains aligned with the headers
        for i, gain in enumerate(channel_gains):
            gain_list = np.asarray(gain).tolist()
            formatted_gains = "\t".join(f"{g:.2f}" for g in gain_list)
            print(f"{i+1}\t{tracks[i].azimuth}\t{tracks[i].elevation}\t{formatted_gains}")

    # Convert channel_gains to numpy array with 2 decimal float accuracy
    channel_gains = np.array(channel_gains).astype(np.float32)
    channel_gains = np.round(channel_gains, 2)

    # Compute surround channels
    surround_channels = np.matmul(channel_gains.T, processed_tracks)

    if verbose:
        print(f"\nSurround Mix Completed: {speaker_layout} - ({surround_channels.shape[0]} channels)")

    # plot all surround channels in subplots with channel names
    if plots:
        num_channels = surround_channels.shape[0]
        fig, axs = plot.subplots(num_channels, 1, figsize=(10, 2 * num_channels))
        for i, ax in enumerate(axs):
            ax.plot(surround_channels[i, :])

            # if sum of channel is 0, color plot lines red
            if np.sum(surround_channels[i, :]) == 0:
                ax.lines[0].set_color('red')

            ax.set_xlim([0, surround_channels.shape[1]])
            # ax.set_title(channel_names[i])
            # ax.set_xlabel("Time")
            ax.set_ylabel(channel_names[i])
            ax.set_ylim([-1, 1])
        plot.tight_layout()
        plot.show()

    return surround_channels, channel_gains

def mix_tracks_stereo(tracks, sample_rate, reverb_type='1'):
    # Render the mix for a given tracks object, subject, IR type and speaker layout

    # Check if tracks is not an array
    if not isinstance(tracks, list):
        raise ValueError("Tracks must be an array of TrackObjects as defined in the TrackObject class in sadie_utilities.py")
    # If it is an array, check if each element is a track object
    for track in tracks:
        if not isinstance(track, TrackObject):
            raise ValueError("Each element in the tracks array must be a TrackObject as defined in the TrackObject class in sadie_utilities.py")

    # Check if all tracks have the same dimensions
    track_lengths = [len(track.audio) for track in tracks]
    if not all(length == track_lengths[0] for length in track_lengths):
        raise ValueError("All tracks must have the same length")
    
    # Check if all tracks have azimuth and elevation
    for track in tracks:
        if track.pan is None:
            raise ValueError("All tracks must have a panning value (-1 to 1) specified")

    print("Rendering Mix...")

     # load reverb IR
    if reverb_type == '1':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "lecture_theatre.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '2':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "office.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '3':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "small_room.wav"), sr=sample_rate, mono=True)
    elif reverb_type == '4':
        reverb_ir, sr = librosa.load(os.path.join(reverb_base_path, "meeting_room.wav"), sr=sample_rate, mono=True)
    else:
        raise ValueError("Invalid reverb type. Choose from 1, 2, 3, or 4")
    
    
    ir_length = len(reverb_ir)-1

    # Render and sum the sources for each track
    for i, track in enumerate(tracks):
        print("Mixing ",track.name)
        if i == 0:
            
            if track.reverb != 0:
                print("Adding Reverb (",track.reverb,") to ",track.name)
                reverb = oaconvolve(track.audio, reverb_ir, mode='full')

                first_source = (reverb * track.reverb) + (np.pad(track.audio,(0, ir_length), 'constant') * (1-track.reverb))
            else:
                first_source = np.pad(track.audio,(0, ir_length), 'constant')
            
            first_source = pan_source(track.pan, first_source) * track.level

            print("Level", track.level, "Pan", track.pan)
            
            output = first_source
        else:
            
            if track.reverb != 0:
                print("Adding Reverb (",track.reverb,") to ",track.name)
                reverb = oaconvolve(track.audio, reverb_ir, mode='full')

                next_source = (reverb * track.reverb) + (np.pad(track.audio,(0, ir_length), 'constant') * (1-track.reverb))
            else:
                next_source = np.pad(track.audio,(0, ir_length), 'constant')
            
            next_source = pan_source(track.pan, next_source) * track.level

            print("Level", track.level, "Pan", track.pan)

            output += next_source

    return output

def render_surround_to_binaural(surround_container, sr, subject_id, ir_type, input_layout, render_layout, mode="auto"):
  
    # Get the channel angles for the speaker layout
    channel_spec = surround.get_channel_angles(input_layout)

    # Create a dictionary of channel names and their corresponding channel objects
    channel_index = {channel.name: channel for channel in channel_spec}

    # Channel names
    channel_names = list(channel_index.keys())

    # Check that the number of channels in the audio file matches the number of channels in the speaker layout
    if len(surround_container) != len(channel_spec):    
        raise ValueError(f"Number of channels in the input file ({len(surround_container)}) does not match the number of channels in the input speaker layout ({len(channel_spec)})")
    else:
        print("Multichannel Audio file has been loaded as a", input_layout, "file with the following channel mapping", channel_names)

    # Extract the individual channels from the surround container
    channels_audio = [surround_container[i] for i in range(len(channel_names))]

    # Create TrackObject instances for each channel
    channels = [
        TrackObject(
            name=channel_index[name].name,
            azimuth=channel_index[name].azi,
            elevation=channel_index[name].ele,
            level=0.5,
            reverb=0.0,
            audio=audio
        )
        for name, audio in zip(channel_names, channels_audio)
    ]

    # Mix the tracks
    output = mix_tracks_binaural(channels, subject_id, sr, ir_type, render_layout, mode, reverb_type="1")

    
    return output, sr

class TrackObject:
    def __init__(self, name, azimuth=None, elevation=None, pan=None, level=0, reverb=0, audio=None):
        self.name = name
        self.azimuth = azimuth
        self.elevation = elevation
        self.pan = pan
        self.level = level
        self.reverb = reverb
        self.audio = audio

    def __repr__(self):
        return (f"Track Name={self.name}, Azimuth={self.azimuth}°, "
                f"Elevation={self.elevation}°, Pan={self.pan}°, "
                f"Level={self.level}, Reverb={self.reverb}")





