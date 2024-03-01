import os
import json
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

def read_format_from_config(config_path):
    """
    Read the default format from the configuration file.
    
    Parameters:
    - config_path (str): The path to the configuration file.
    
    Returns:
    - str: The default format ('bbc' or 'md') from the configuration file if found, None otherwise.
    """
    try:
        with open(config_path) as f:
            data = json.load(f)
        return data['defaults']['format']
    except (FileNotFoundError, KeyError) as e:
        print(f"Error reading config '{config_path}': {e}")
        return None

def main():
    format_value = None
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
            if not is_valid_path(album_path):
                exit()
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
        config_file_path = os.path.join(os.path.dirname(__file__), 'conf', f"{config_name}.json")

        try:
            with open(config_file_path, 'r') as f:
                config_data = json.load(f)
                format_value = config_data.get('defaults', {}).get('format')
                if format_value not in ['bbc', 'md']:
                    print(f"Warning: Invalid format '{format_value}' in config. Defaulting to 'bbc'.")
                    format_value = 'bbc'
       
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_file_path}. Using default format 'bbc'.")
            
        
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in config file at {config_file_path}. Using default format 'bbc'.")
            
        
        except KeyError:
            print(f"Warning: Format not specified in config file at {config_file_path}. Using default format 'bbc'.")
            

        for album_path in album_paths:
            try:
                torrent_file_name = os.path.basename(album_path) + ".torrent"
                if args.save_torrent is None:
                    input_save_path = input(f"Enter path to save torrent file (press Enter to use default album path: {album_path}): ")
                    torrent_save_path = input_save_path or album_path
                elif args.save_torrent is True:
                    torrent_save_path = album_path
                else:
                    torrent_save_path = os.path.expanduser(args.save_torrent)

                torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)

                if not os.path.isdir(torrent_save_path):
                    print(f"Error: Save path does not exist: {torrent_save_path}")
                    continue

                if not os.path.exists(torrent_file_path):
                    torrent_created, created_torrents = torrent.create([album_path], torrent_save_path, config_name)

            except Exception as e:
                print(f"Error generating torrent for album at path {album_path}: {e}")


    # Read the format_value from the user's config
    valid_formats = ['bbc', 'md']
    output_format = format_value if format_value in valid_formats else (args.format if args.format in valid_formats else 'bbc')

    formatted_tables = []

    for album_meta in all_albums_meta:
        if output_format == "md":
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


def is_valid_path(path):
    """
    Check if the path is valid. must be a directory and must exist.
    Args:
        path:

    Returns:
        bool: True if the path is valid, False otherwise.
    """
    if (os.path.exists(path)) and (os.path.isdir(path)):
        return True
    else:
        if not os.path.exists(path):
            print(f"Error: Path does not exist: {path}.")
        elif not os.path.isdir(path):
            print(f"Error: Path is not a valid folder: {path}.")
        else:
            print(f"Error: Invalid path: {path}.")

        return False


if __name__ == "__main__":
    main()
