import base64
import os
import tempfile
import requests
import matplotlib.pyplot as plt
import hashlib
from pydub import AudioSegment
from mutagen.flac import FLAC
from tqdm import tqdm


def get_audio_codec(file_path):
  _, extension = os.path.splitext(file_path)
  return extension.lower()[1:]  # Removing the dot at the beginning


def save_spectrogram_plot(audio, file_path):
  mixed_channel = audio.set_channels(1)

  plt.specgram(
    mixed_channel.get_array_of_samples(),
    Fs=mixed_channel.frame_rate,
    cmap='viridis',
    NFFT=2000,  # Increase the number of FFT points for higher frequency resolution
    noverlap=100,  # Increase the overlap for smoother spectrogram
  )
  plt.title(f'Mixed Channel Spectrogram: {os.path.basename(file_path)}')
  plt.xlabel('Time (s)')
  plt.ylabel('Frequency (Hz)')

  tmp_folder = tempfile.mkdtemp()
  spectrogram = os.path.join(tmp_folder,
                             f"{os.path.splitext(os.path.basename(file_path))[0]}_mixed_channel_spectrogram.png")
  plt.savefig(spectrogram)
  plt.close()

  return spectrogram


def analyze_album(album_folder, upload_spectrogram=False):
  flac_files = [file for file in os.listdir(album_folder) if file.lower().endswith('.flac')]
  album = {}

  for file in tqdm(flac_files, desc="Processing tracks", unit="files"):
    file_path = os.path.join(album_folder, file)
    flac_info = get_flac_info(file_path, upload_spectrogram)
    file_name = os.path.basename(file_path)
    album[file_name] = flac_info

    try:
      album = dict(sorted(album.items(), key=lambda x: int(x[1]['#']), reverse=False))
    except:
      pass

  return album


def get_flac_info(file_path, upload_spectrogram=False):
  result = {}

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

    result['duration'] = convert_seconds_to_hms(audio.info.length)
    result['channels'] = audio.info.channels
    result['bits_per_sample'] = audio.info.bits_per_sample
    result['sample_rate'] = f"{audio.info.sample_rate/1000} kHz"
    result['bitrate'] = f"{int(audio.info.bitrate / 1000)} kbps"
    result['codec'] = "FLAC"
    result['embedded_cuesheet'] = audio.cuesheet

    if upload_spectrogram:
      audio_segment = AudioSegment.from_file(file_path, format="flac")
      plot_path = save_spectrogram_plot(audio_segment, file_path)
      result['spectrogram'] = f"[url]{upload_image(plot_path)}[/url]"

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

  return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def generate_bbcode_table(metadata):
  bbcode = "[table]\n"
  bbcode += "[tr]\n"
  bbcode += f"[td][b]Filename[/b][/td]\n"

  for key in metadata[list(metadata.keys())[0]]:
    bbcode += f"[td][b]{key.capitalize()}[/b][/td]\n"
  bbcode += "[/tr]\n"

  for track, track_info in metadata.items():
    bbcode += f"[tr]\n[td]{track}[/td]\n"
    for value in track_info.values():
      bbcode += f"[td]{value}[/td]\n"

    bbcode += "[/tr]\n"

  bbcode += "[/table]"
  return bbcode


def upload_image(file_path):
  api_url = "https://freeimage.host/api/1/upload"

  with open(file_path, "rb") as file:
    base64_image = base64.b64encode(file.read()).decode("utf-8")

  # API
  params = {
    "key": "6d207e02198a847aa98d0a2a901485a5",
    "action": "upload",
    "source": base64_image,
    "format": "json"
  }
  response = requests.post(api_url, data=params)

  if response.status_code == 200:
    result = response.json()
    return result["image"]["url"]
  else:
    return {"error": f"Error {response.status_code}: {response.text}"}


if __name__ == "__main__":
  album_folder = r"%userprofile%\Downloads\spam\Petar Dundov - At The Turn Of Equilibrium (2016)(FLAC)(CD)"
  album_data = analyze_album(album_folder)
  print(generate_bbcode_table(album_data))
