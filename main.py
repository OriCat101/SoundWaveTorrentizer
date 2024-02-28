import os
import argparse
import shlex
import pyperclip
from audio import analyzer
import format.output
from torrent import torrent


def parse_args():
    """
    Parse command line arguments.
    Returns:
    - argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Process album/music information and generate torrent.")
    parser.add_argument("-p", "--paths", nargs='+', help="Album folder or file path. Seperate with space")
    parser.add_argument("-s", "--spectrogram", action="store_true", default=False, help="Upload spectrogram. Default: False.")
    parser.add_argument("-t", "--save-torrent", nargs='?', const=True,
                        help="If the argument is provided but empty, the default album path will be used. Optionally, "
                             "provide a path to save the torrent file.")
    parser.add_argument("-c", "--config", help="Tracker configuration name.")
    parser.add_argument("-f", "--format", choices=["bbc", "md"], default="bbc", help="Table format (bbcode/markdown).")

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
        album_paths = shlex.split(album_paths_input)

    upload_spectrogram = args.spectrogram
    if upload_spectrogram or input("Upload spectrogram? (y/n, default=n): ").lower() == "y":
        upload_spectrogram = True

    all_albums_meta = analyzer.analyze_albums(album_paths, upload_spectrogram)
    # This checks for valid directories, and flac files
    for album_path in album_paths:
        try:
            if not os.path.exists(album_path):
                print(f"Error: Album path does not exist: {album_path}.")
            elif not os.path.isdir(album_path):
                print(f"Error: Path is not a valid album folder: {album_path}.")
            else:
                print(f"Processing album at path: {album_path}")
                # This is what checks for non flac files, but ignores potential cover files like cover.jpg
                non_flac_files = [file for file in os.listdir(album_path) if
                                  not is_flac_file(os.path.join(album_path, file)) and not file.lower().endswith(
                                      ('.jpg', '.png', '.webp')) and not os.path.isdir(os.path.join(album_path, file))]
                if non_flac_files:
                    print(f"Warning: Non-FLAC files found in the folder: {non_flac_files}")

                pass
        except Exception as e:
            print(f"Error processing album at path {album_path}: {e}")
    # Where the torrent magic happens

    if args.save_torrent or (not args.paths and input("Generate torrent? (y/n, default=y): ").lower() != "n"):
        config_name = args.config or input("Tracker configuration: ")

        for album_path in album_paths:
            try:
                torrent_file_name = os.path.basename(album_path) + ".torrent"
                if args.save_torrent is None:
                    input_save_path = input(
                        f"Enter path to save torrent file (press Enter to use default album path: {album_path}): ")
                    torrent_save_path = input_save_path or album_path
                elif args.save_torrent is True:
                    # Use the default album path
                    torrent_save_path = album_path
                else:
                    # Use the save path provided as an argument, expand the user path
                    torrent_save_path = os.path.expanduser(args.save_torrent)

                torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)

                if not os.path.isdir(torrent_save_path):
                    print(f"Error: Save path does not exist: {torrent_save_path}")
                    continue

                if not os.path.exists(torrent_file_path):
                    torrent_created, created_torrents = torrent.create([album_path], torrent_save_path, config_name)

            except Exception as e:
                print(f"Error generating torrent for album at path {album_path}: {e}")

    default_format = "bbcode"  # Set your default format here: "bbcode" or "markdown" (this is really bad practice especially if you already have a config file)
    output_format = args.format or input(
        f"Choose output format (bbcode(bbc)/markdown(md), default={default_format}): ").lower() or default_format
    formatted_tables = []

    for album_meta in all_albums_meta:
        if output_format == "md" or output_format == "markdown":
            table_output = format.output.markdown(album_meta)
        else:
            table_output = format.output.bbcode(album_meta)
        formatted_tables.append(table_output)

    combined_output = "\n".join(formatted_tables)

    # Copy the table to clipboard
    while True:
        pyperclip.copy(combined_output)
        print("Table copied to clipboard. Press 'C' to copy again, or Enter to exit.")

        user_input = input()
        if user_input.lower() == 'c':
            pass
        else:
            break

    print("Done")


if __name__ == "__main__":
    main()
