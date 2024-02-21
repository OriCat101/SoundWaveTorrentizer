import argparse
import pyperclip
from audio import analyzer
import format.output
from torrent import torrent

# Should be easy to edit this as needed, add/change new functions
def parse_args():
    parser = argparse.ArgumentParser(description="Process album/music information and generate torrent.")
    parser.add_argument("-p", "--path", help="Album folder or file path.")
    parser.add_argument("-s", "--spectrogram", action="store_true", help="Upload spectrogram. Default: False.")
    parser.add_argument("-g", "--generate-torrent", action="store_true", help="Generate torrent file. Default: False")
    parser.add_argument("-t", "--save-torrent", help="Path to save torrent file (default=Album folder). Requires torrent to be saved.")
    parser.add_argument("-c", "--config", help="Tracker configuration name.")
    parser.add_argument("-f", "--format", choices=["bbcode", "markdown"], help="Table format (bbcode/markdown).")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.path:
        album_path = args.path
    else:
        album_path = input("Album folder: ")

    if args.spectrogram:
        upload_spectrogram = args.spectrogram
    else:
        upload_spectrogram = input("Upload spectrogram? (y/n, default=n): ").lower() == "y"

    album_meta = analyzer.analyze_album(album_path, upload_spectrogram)

    if args.generate_torrent or (not args.path and input("Generate torrent? (y/n, default=y): ").lower() != "n"):
        save_path = args.save_torrent or input("Save torrent to (default=Album folder): ") or album_path
        config_name = args.config or input("Tracker configuration: ")
        torrent.create(album_path, save_path, config_name)
        print("Torrent file created.")

    default_format = "bbcode"  # Set your default format here: "bbcode" or "markdown"
    output_format = args.format or input(f"Choose output format (bbcode/markdown, default={default_format}): ").lower() or default_format

    if output_format == "markdown":
        table_output = format.output.markdown(album_meta)
        print("Markdown table copied to clipboard.")
    else:
        table_output = format.output.bbcode(album_meta)
        print("BBCode table copied to clipboard.")

    pyperclip.copy(table_output) # A fallback in case you accidently lose your paste
    print("Table copied to clipboard. Press 'C' to copy again, or any other key to exit.")

    while True:
        user_input = input()
        if user_input.lower() == 'c':
            pyperclip.copy(table_output)
            print("Table re-copied to clipboard. Press 'C' to copy again, or any other key to exit.")
        else:
            break

    print("Done.")


if __name__ == "__main__":
    main()