import argparse
import shlex
import pyperclip
from audio import analyzer
import format.output
from torrent import torrent

# Should be easy to edit this as needed, add/change new functions
def parse_args():
    parser = argparse.ArgumentParser(description="Process album/music information and generate torrent.")
    parser.add_argument("-p", "--paths", nargs='+', help="Album folder or file path. Seperate with space")
    parser.add_argument("-s", "--spectrogram", action="store_true", help="Upload spectrogram. Default: False.")
    parser.add_argument("-g", "--generate-torrent", action="store_true", help="Generate torrent file. Default: False")
    parser.add_argument("-t", "--save-torrent", help="Path to save torrent file (default=Album folder). Requires torrent to be saved.")
    parser.add_argument("-c", "--config", help="Tracker configuration name.")
    parser.add_argument("-f", "--format", choices=["bbcode", "markdown"], help="Table format (bbcode/markdown).")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.paths:
        album_paths = args.paths
    else:
        album_paths_input = input("Enter album folder(s) separated by spaces: ")
        album_paths = shlex.split(album_paths_input)

    all_albums_meta = analyzer.analyze_albums(album_paths, args.spectrogram)

    for album_path in album_paths:
        print(f"Processing album at path: {album_path}")

    if args.generate_torrent or (not args.paths and input("Generate torrent? (y/n, default=y): ").lower() != "n"):
        save_path = args.save_torrent or input("Save torrent to (default=Album folder): ") or album_path
        config_name = args.config or input("Tracker configuration: ")
        torrent_created = torrent.create(album_paths, save_path, config_name)

        if torrent_created:
            print("Torrent file created.")
        else:
            print("Torrent file not created.")

    default_format = "bbcode"  # Set your default format here: "bbcode" or "markdown"
    output_format = args.format or input(f"Choose output format (bbcode/markdown, default={default_format}): ").lower() or default_format

    formatted_tables = []
    for album_meta in all_albums_meta:
        if output_format == "markdown":
            table_output = format.output.markdown(album_meta)
        else:
            table_output = format.output.bbcode(album_meta)
        formatted_tables.append(table_output)

    combined_output = "\n".join(formatted_tables)
    pyperclip.copy(combined_output)
    print(f"{output_format.capitalize()} table(s) copied to clipboard. Press 'C' to copy again, or any other key to exit.")

    while True:
        user_input = input()
        if user_input.lower() == 'c':
            pyperclip.copy(combined_output)
            print("Table re-copied to clipboard. Press 'C' to copy again, or any other key to exit.")
        else:
            break

    print("Done.")


if __name__ == "__main__":
    main()