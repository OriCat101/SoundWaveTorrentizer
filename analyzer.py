import os
from pydub import AudioSegment
import matplotlib.pyplot as plt
from mutagen.flac import FLAC
import hashlib


def get_audio_codec(file_path):
    """
    Determine the audio codec based on the file extension.

    Parameters:
    - file_path (str): Path to the audio file.

    Returns:
    - str: Audio codec.
    """
    _, extension = os.path.splitext(file_path)
    return extension.lower()[1:]  # Removing the dot at the beginning


def save_spectrogram_plot(audio, output_folder, file_path):
    """
    Save a spectrogram plot to a file.

    Parameters:
    - audio (AudioSegment): Input audio.
    - output_folder (str): Folder to save the spectrogram plot.
    - file_path (str): Path to the audio file.
    """
    mixed_channel = audio.set_channels(1)

    plt.specgram(
        mixed_channel.get_array_of_samples(),
        Fs=mixed_channel.frame_rate,
        cmap='viridis',
        NFFT=2000,  # Increase the number of FFT points for higher frequency resolution
        noverlap=1000,  # Increase the overlap for smoother spectrogram
    )
    plt.title(f'Mixed Channel Spectrogram: {os.path.basename(file_path)}')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save the spectrogram plot to a file
    output_file = os.path.join(output_folder,
                               f"{os.path.splitext(os.path.basename(file_path))[0]}_mixed_channel_spectrogram.png")
    plt.savefig(output_file)
    plt.close()


def get_flac_info(file_path, output_folder="output/spectrogram"):
    """
    Get information about a FLAC audio file and save its spectrogram.

    Parameters:
    - file_path (str): Path to the FLAC audio file.
    - output_folder (str): Folder to save the spectrogram plot.

    Returns:
    - dict: Information about the FLAC file.
    """
    result = {}

    if os.path.isfile(file_path) and file_path.lower().endswith('.flac'):
        audio = AudioSegment.from_file(file_path, format="flac")

        # Save spectrogram with increased detail
        save_spectrogram_plot(audio, output_folder, file_path)

        # Extract other parameters
        result['duration'] = audio.duration_seconds
        result['sample_rate'] = audio.frame_rate
        result['channels'] = audio.channels
        result['bits_per_sample'] = audio.sample_width * 8
        result['bitrate'] = audio.frame_rate * audio.sample_width * 8 * audio.channels / 1000
        result['codec'] = get_audio_codec(file_path)  # Dynamically determine codec
        result['encoding'] = audio.sample_width * 8
        result['embedded_cuesheet'] = 'Yes' if 'cuesheet' in FLAC(file_path) else 'No'

        # Calculate MD5 hash of audio data
        with open(file_path, 'rb') as flac_file:
            audio_data = flac_file.read()
            md5_hash = hashlib.md5(audio_data).hexdigest()
            result['audio_md5'] = md5_hash

    else:
        print("Invalid FLAC file path.")

    return result
