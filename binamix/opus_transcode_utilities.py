# This script will transcode an input file to opus format at 32, 64, 128, 256, and 512 kbps 
# and then decode them back to wav format. This can be used to test the effect of different bitrates on binaural audio quality.

import soundfile as sf
import subprocess
import os
import sys

# IMPORTANT: Add the path to the Opus Tools folder here. It should contain the binaries 'opusenc' and 'opusdec'.

# Path for Mac OSX
opus_path = './opus-tools-0.1.9-macos/'

# Path for Windows
# opus_path = './opus-tools-0.2-win/'


# Takes path to wav file as input and generates transcodded files in the same folder unless output_path is specified.
def generate_transcodes(input, output_path=None):
    
    if output_path is None:
        output_slug = input.replace(".wav", "") 
    else:
        filename = os.path.basename(input)
        output_slug = f"{output_path}{filename.replace('.wav', '')}"

    # Renmove REF from the filename if exists
    output_slug = output_slug.replace("_REF", "") 

    if not os.path.exists(opus_path):
        print(f"Error: The folder '{opus_path}' was not found.", file=sys.stderr)
        sys.exit(1)

    # Transcode to target bitrates
    transcode_to_32k = [f"{opus_path}opusenc", "--bitrate", "32", input, f"{output_slug}_32k.opus"]
    transcode_to_64k = [f"{opus_path}opusenc", "--bitrate", "64", input, f"{output_slug}_64k.opus"]
    transcode_to_128k = [f"{opus_path}opusenc", "--bitrate", "128", input, f"{output_slug}_128k.opus"]
    transcode_to_256k = [f"{opus_path}opusenc", "--bitrate", "256", input, f"{output_slug}_256k.opus"]
    transcode_to_512k = [f"{opus_path}opusenc", "--bitrate", "512", input, f"{output_slug}_512k.opus"]

    # Run the commands
    subprocess.run(transcode_to_32k, stdout=subprocess.DEVNULL)
    subprocess.run(transcode_to_64k, stdout=subprocess.DEVNULL)
    subprocess.run(transcode_to_128k, stdout=subprocess.DEVNULL)
    subprocess.run(transcode_to_256k, stdout=subprocess.DEVNULL)
    subprocess.run(transcode_to_512k, stdout=subprocess.DEVNULL)

    # Decode targets back to wav
    decode_32k = [f"{opus_path}opusdec", "--force-wav", f"{output_slug}_32k.opus", f"{output_slug}_opus32k.wav"]
    decode_64k = [f"{opus_path}opusdec", "--force-wav", f"{output_slug}_64k.opus", f"{output_slug}_opus64k.wav"]
    decode_128k = [f"{opus_path}opusdec", "--force-wav", f"{output_slug}_128k.opus", f"{output_slug}_opus128k.wav"]
    decode_256k = [f"{opus_path}opusdec", "--force-wav", f"{output_slug}_256k.opus", f"{output_slug}_opus256k.wav"]
    decode_512k = [f"{opus_path}opusdec", "--force-wav", f"{output_slug}_512k.opus", f"{output_slug}_opus512k.wav"]

    # Run the commands
    subprocess.run(decode_32k, stdout=subprocess.DEVNULL)
    subprocess.run(decode_64k, stdout=subprocess.DEVNULL)
    subprocess.run(decode_128k, stdout=subprocess.DEVNULL)
    subprocess.run(decode_256k, stdout=subprocess.DEVNULL)
    subprocess.run(decode_512k, stdout=subprocess.DEVNULL)

    # Delete the opus files
    os.remove(f"{output_slug}_32k.opus")
    os.remove(f"{output_slug}_64k.opus")
    os.remove(f"{output_slug}_128k.opus")
    os.remove(f"{output_slug}_256k.opus")
    os.remove(f"{output_slug}_512k.opus")
    


