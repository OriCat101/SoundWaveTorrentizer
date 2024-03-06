import os
import tempfile
import matplotlib.pyplot as plt
import hashlib
import numpy as np
from pydub import AudioSegment
from mutagen.flac import FLAC
from alive_progress import alive_bar
# local
from api.Freeimagehost import upload_image
from format.data import seconds_to_hhmmss


def get_audio_codec(file_path):
    """
    Get the audio codec from the file extension.

    Parameters:
    - file_path (str): The path of the audio file.

    Returns:
    - str: The audio codec.
    """
    _, extension = os.path.splitext(file_path)
    return extension.lower()[1:]  # Removing the dot at the beginning


# One day we'll figure out to fix the divide by zero error, but it doesn't break the script so, it's a to-do
def save_spectrogram_plot(audio, file_path):
    """
    Save a spectrogram plot of the audio file.

    Parameters:
    - audio (AudioSegment): The audio segment.
    - file_path (str): The path of the audio file.

    Returns:
    - str: The path to the saved spectrogram plot.
    """
    # Ensure the frame rate is not zero to avoid division by zero
    if audio.frame_rate == 0:
        raise ValueError("Audio frame rate cannot be zero.")

    # Convert audio segment to mono (single channel)
    mixed_channel = audio.set_channels(1)

    # This is what fixes the divide by zero error
    samples = np.array(mixed_channel.get_array_of_samples())
    if mixed_channel.sample_width == 2:
        samples = samples.astype(np.int16)
    elif mixed_channel.sample_width == 4:
        samples = samples.astype(np.float32)

    # Create the plot
    plt.specgram(
        samples,
        Fs=mixed_channel.frame_rate,
        cmap='viridis',
        NFFT=2000,  # Increase the number of FFT points for higher frequency resolution
        noverlap=100,  # Increase the overlap for smoother spectrogram
    )

    plt.title(f'Mixed Channel Spectrogram: {os.path.basename(file_path)}')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')

    # Save the plot to a temporary file
    tmp_folder = tempfile.mkdtemp()
    spectrogram = os.path.join(tmp_folder,
                               f"{os.path.splitext(os.path.basename(file_path))[0]}_mixed_channel_spectrogram.png")

    plt.savefig(spectrogram)
    plt.close()

    return spectrogram


def analyze_albums(album_paths, upload_spectrogram=False):
    """
    Analyze multiple albums in FLAC format, including nested folders.

    Parameters:
    - album_paths (list): List of paths to the folders containing FLAC files for each album.
    - upload_spectrogram (bool): Flag indicating whether to upload spectrogram images.

    Returns:
    - list: List of dictionaries containing information about the analyzed albums.
    """
    all_albums_data = []

    for album_path in album_paths:
        if os.path.isdir(album_path):
            for root, _, files in os.walk(album_path):
                if any(file.lower().endswith('.flac') for file in files):
                    album_data = analyze_album(root, upload_spectrogram)
                    all_albums_data.append(album_data)

    return all_albums_data


def analyze_album(album_path, upload_spectrogram=False):
    """
    Analyze an album in FLAC format. Ask the user which tracks to upload spectrals.

    Parameters:
    - album_path (str): The path to the folder containing FLAC files.
    - upload_spectrogram (bool): Flag indicating whether to upload spectrogram images.

    Returns:
    - dict: Dictionary containing information about the analyzed album.
    """
    flac_files = [file for file in os.listdir(album_path) if file.lower().endswith('.flac')]
    album = {}

    # Ask the user for input if upload_spectrogram is True
    tracks_to_upload_spectrograms = set()
    if upload_spectrogram:
        print("Enter the track numbers to upload spectrals separated by commas, or '*' for all tracks:")
        user_input = input().strip()
        if not isinstance(user_input, int):
            # Use a wildcard to indicate all tracks for spectrogram upload
            tracks_to_upload_spectrograms = {'*'}
        else:
            # Parses user input, keeping the disc prefix and removing leading zeros from track numbers
            tracks_to_upload_spectrograms = set(track.strip().lstrip('0') for track in user_input.split(','))

    with alive_bar(len(flac_files), title='Processing tracks', bar='classic', spinner='classic', length=40) as bar:
        for file in flac_files:
            file_path = os.path.join(album_path, file)
            track_number = get_track_number(file_path)  # This function should return the track number as a string
            # Determine if this track's spectrogram should be uploaded
            should_upload_spectrogram = ('*' in tracks_to_upload_spectrograms or
                                         any(track_number == track.lstrip('0') for track in
                                             tracks_to_upload_spectrograms))
            flac_info = get_flac_info(file_path, should_upload_spectrogram)
            file_name = os.path.basename(file_path)
            album[file_name] = flac_info
            bar()

    try:
        album = dict(
            sorted(album.items(), key=lambda item: (int(item[1]['disc_number']), int(item[1]['#'])), reverse=False))
    except:
        pass

    return album


# Now this considers how I format tracks with Musicbee. Hopefully I've made it work with other tagging types
def get_track_number(file_path):
    """
    Extract the track number from the FLAC file metadata or filename, ignoring disc number and leading zeros.

    Parameters:
    - file_path (str): The path to the FLAC file.

    Returns:
    - The track number extracted from the file path, or "-" if an error occurs.
    """
    try:
        audio = FLAC(file_path)
        if 'tracknumber' in audio:
            # Split track number and remove leading zeros if present
            return audio['tracknumber'][0].split('/')[0].lstrip('0')
    except Exception as e:
        print(f"Error reading FLAC metadata: {e}")

    return "-"


def get_flac_info(file_path, upload_spectrogram=False):
    """
    Get information about a FLAC file.

    Parameters:
    - file_path (str): The path to the FLAC file.
    - upload_spectrogram (bool): Flag indicating whether to upload spectrogram images.

    Returns:
    - dict: Dictionary containing information about the FLAC file.
    """
    result = {}
    # FLAC file check
    if not os.path.isfile(file_path) or not file_path.lower().endswith('.flac'):
        print(f"Error: The file at {file_path} is not a FLAC file.")
        return {"error": f"The file at {file_path} is not a FLAC file."}

    if os.path.isfile(file_path) and file_path.lower().endswith('.flac'):

        audio = FLAC(file_path)

        if 'tracknumber' in audio:
            result['#'] = audio['tracknumber'][0]
        else:
            result['#'] = "-"

        if 'artist' in audio:
            result['artist'] = audio['artist'][0]
        else:
            result['artist'] = "Unknown"

        if 'title' in audio:
            result['title'] = audio['title'][0]
        else:
            result['title'] = "Unknown"

        result['duration'] = seconds_to_hhmmss(audio.info.length)
        result['channels'] = audio.info.channels
        result['bits_per_sample'] = audio.info.bits_per_sample  # Corrected attribute name
        result['sample_rate'] = f"{audio.info.sample_rate / 1000} kHz"
        result['bitrate'] = f"{int(audio.info.bitrate / 1000)} kbps"
        result['codec'] = audio.mime[0].split("/")[1].upper()
        result['embedded_cuesheet'] = audio.cuesheet

    if not upload_spectrogram:
        result['spectrogram'] = "N/A"
    else:
        # Continues to generate spectrogram as usual
        audio_segment = AudioSegment.from_file(file_path, format="flac")
        plot_path = save_spectrogram_plot(audio_segment, file_path)
        result['spectrogram'] = f"{upload_image(plot_path)}"

    with open(file_path, 'rb') as flac_file:
        audio_data = flac_file.read()
        md5_hash = hashlib.md5(audio_data).hexdigest()
        result['audio_md5'] = md5_hash

    return result
