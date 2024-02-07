import pyperclip
from audio import analyzer
import format.output


def main():
    album_path=input("Album folder: ")
    upload_spectrogram = input("Upload spectrogram? (y/n, default=n): ")
    if upload_spectrogram.lower() == "y":
        upload_spectrogram = True
    else:
        upload_spectrogram = False

    album_meta= analyzer.analyze_album(album_path, upload_spectrogram)
    pyperclip.copy(format.output.bbcode(album_meta))
    print("BBCode table copied to clipboard.")

if __name__ == "__main__":
    main()
