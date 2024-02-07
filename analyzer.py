import os
from pydub import AudioSegment
import matplotlib.pyplot as plt
from mutagen.flac import FLAC
import hashlib
from tqdm import tqdm


def get_audio_codec(file_path):
  _, extension = os.path.splitext(file_path)
  return extension.lower()[1:]  # Removing the dot at the beginning


def save_spectrogram_plot(audio, output_folder, file_path):
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


def analyze_album(album_folder, output_folder="output/spectrogram"):
  track_num = 0
  flac_files = [file for file in os.listdir(album_folder) if file.lower().endswith('.flac')]
  album = {}

  for file in tqdm(flac_files, desc="Processing tracks", unit="files"):
    file_path = os.path.join(album_folder, file)
    track_num += 1
    flac_info = get_flac_info(file_path, output_folder)
    file_name = os.path.basename(file_path)
    album[file_name] = flac_info

    if track_num == 1:
      # Save spectrogram
      audioSegment = AudioSegment.from_file(file_path, format="flac")
      save_spectrogram_plot(audioSegment, output_folder, file_path)

  return album


def get_flac_info(file_path, output_folder="output/spectrogram"):
  result = {}

  if os.path.isfile(file_path) and file_path.lower().endswith('.flac'):
    audio = FLAC(file_path)

    # Extract other parameters
    result['duration'] = convert_seconds_to_hms(audio.info.length)
    result['channels'] = audio.info.channels
    result['bits_per_sample'] = audio.info.bits_per_sample
    result['bitrate'] = f"{int(audio.info.bitrate / 1000)} kbps"
    result['codec'] = "FLAC"
    result['embedded_cuesheet'] = audio.cuesheet

    # Calculate MD5 hash of audio data
    with open(file_path, 'rb') as flac_file:
      audio_data = flac_file.read()
      md5_hash = hashlib.md5(audio_data).hexdigest()
      result['audio_md5'] = md5_hash

  else:
    print(f"Invalid file path: {file_path}")

  return result


def convert_seconds_to_hms(seconds):
  hours, remainder = divmod(seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return f"{int(hours)}:{int(minutes)}:{int(seconds)}"


def generate_bbcode_table(metadata):
  bbcode = "[table]\n"

  # Header row
  bbcode += "[tr]\n"
  bbcode += f"[td][b]Filename[/b][/td]\n"
  for key in metadata[list(metadata.keys())[0]]:
    bbcode += f"[td][b]{key.capitalize()}[/b][/td]\n"
  bbcode += "[/tr]\n"

  # Data rows
  for track, track_info in metadata.items():
    bbcode += f"[tr]\n[td]{track}[/td]\n"

    for value in track_info.values():
      bbcode += f"[td]{value}[/td]\n"

    bbcode += "[/tr]\n"

  bbcode += "[/table]"
  return bbcode


if __name__ == "__main__":
  # Example usage:
  album_folder = r"C:\Users\ork\Downloads\spam\Petar Dundov - At The Turn Of Equilibrium (2016)(FLAC)(CD)"
  output_folder = "output/folder1"
  album_data = analyze_album(album_folder, output_folder)
  print(generate_bbcode_table(album_data))
