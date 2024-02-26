import os
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


def is_flac_file(file_path):
    """
    Check if a file is a FLAC file.

    Parameters:
    - file_path (str): The path to the file.

    Returns:
    - bool: True if the file is a FLAC file, False otherwise.
    """
    return os.path.isfile(file_path) and file_path.lower().endswith('.flac')

def main():
    args = parse_args()

    if args.paths:
        album_paths = args.paths
    else:
        album_paths_input = input("Enter album folder(s) separated by spaces: ")
        album_paths = shlex.split(album_paths_input) # This was the answer, fixed our input problems. 

    upload_spectrogram = args.spectrogram
    if not upload_spectrogram and input("Upload spectrogram? (y/n, default=n): ").lower() == "y":
        upload_spectrogram = True

    all_albums_meta = analyzer.analyze_albums(album_paths, upload_spectrogram)
    # This checks for valid directories, and is also where we check for flac files
    for album_path in album_paths:
        try:
            if not os.path.exists(album_path):
                print(f"Error: Album path does not exist: {album_path}.")
            elif not os.path.isdir(album_path):
                print(f"Error: Path is not a valid album folder: {album_path}.")
            else:
                print(f"Processing album at path: {album_path}")
                # This is what checks for non flac files, but ignores potential cover files like cover.jpg
                non_flac_files = [file for file in os.listdir(album_path) if not is_flac_file(os.path.join(album_path, file)) and not file.lower().endswith(('.jpg', '.png', '.webp')) and not os.path.isdir(os.path.join(album_path, file))]
                if non_flac_files:
                    print(f"Warning: Non-FLAC files found in the folder: {non_flac_files}")

                pass
        except Exception as e:
            print(f"Error processing album at path {album_path}: {e}")
    # Where the torrent magic happens, fixed it to no longer check the directory for existing torrent checks. Whoops!
    # Where the torrent magic happens
    
    if args.generate_torrent or (not args.paths and input("Generate torrent? (y/n, default=y): ").lower() != "n"):
        config_name = args.config or input("Tracker configuration: ")

        for album_path in album_paths:
            try:
                torrent_file_name = os.path.basename(album_path) + ".torrent"
                if args.save_torrent is None:
                    input_save_path = input(f"Enter path to save torrent file (press Enter to use default album path: {album_path}): ")
                    torrent_save_path = input_save_path or album_path
                else:
                    # Use the save path provided as an argument, expand the user path
                    torrent_save_path = os.path.expanduser(args.save_torrent)

                torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)
                
                if not os.path.isdir(torrent_save_path):
                    print(f"Error: Save path does not exist: {torrent_save_path}")
                    continue

                if not os.path.exists(torrent_file_path):
                    torrent_created, created_torrents = torrent.create([album_path], torrent_save_path, config_name)

                    if torrent_created:
                        print(f"Torrent file created at {torrent_file_path}.")
                        for created_torrent in created_torrents:
                            print(f"Torrent file created: {created_torrent}")
                    else:
                        print("Failed to create torrent file.")
            except Exception as e:
                print(f"Error generating torrent for album at path {album_path}: {e}")


    default_format = "bbcode"  # Set your default format here: "bbcode" or "markdown"
    output_format = args.format or input(f"Choose output format (bbcode/markdown, default={default_format}): ").lower() or default_format

    formatted_tables = []
    for album_meta in all_albums_meta:
        if output_format == "markdown":
            table_output = format.output.markdown(album_meta)
        else:
            table_output = format.output.bbcode(album_meta)
        formatted_tables.append(table_output)
    # Simple fallback, wanted to make sure you had a way to easily copy the files again, and I can't create a clickable text button like I originally wanted
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