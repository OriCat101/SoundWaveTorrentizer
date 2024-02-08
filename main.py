import pyperclip
from audio import analyzer
import format.output
from torrent import torrent


def main():
    album_path = input("Album folder: ")
    upload_spectrogram = input("Upload spectrogram? (y/n, default=n): ")
    if upload_spectrogram.lower() == "y":
        upload_spectrogram = True
    else:
        upload_spectrogram = False

    album_meta = analyzer.analyze_album(album_path, upload_spectrogram)

    generate_torrent = input("Generate torrent? (y/n, default=y): ")
    if generate_torrent.lower() != "n":
        save_path = input("Save torrent to (default=Album folder):")
        if not save_path:
            save_path = album_path

        config_name = input("Tracker configuration: ")
        torrent.create(album_path, save_path, config_name)
        print("Torrent file created.")

    pyperclip.copy(format.output.bbcode(album_meta))
    print("BBCode table copied to clipboard.")
    print("Done.")


if __name__ == "__main__":
    main()
