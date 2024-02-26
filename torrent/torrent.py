import os

from torf import Torrent
import json


def load_torrent_config(config_name):
    """
    Load tracker configuration from a JSON file.

    Parameters:
    - config_name (str): The name of the configuration file.

    Returns:
    - dict: Dictionary containing the loaded configuration data.
    """

    config_file = os.path.abspath(f"conf/{config_name}.json")

    try:
        with open(config_file, 'r') as file:
            config_data = json.load(file)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_file}")
        return None

    return config_data['torrent']


def create(contents, save_path, config_name):
    """
    Create torrent files using the specified contents and configuration.

    Parameters:
    - contents (list): List of paths to the contents to be included in the torrents.
    - save_path (str): The path where the generated torrent files will be saved.
    - config_name (str): The name of the configuration file without the extension.
    """
    torrent_config = load_torrent_config(config_name)
    success = False # This fixes the torrent creation error

    for content in contents:
        content_name = os.path.basename(content)
        torrent_file_path = os.path.join(save_path, f"{content_name}.torrent")
        original_torrent_file_path = torrent_file_path
        # This is how we check for potential torrent duplicates and skip them if wanted
        if os.path.exists(torrent_file_path):
            user_choice = input(f"'{torrent_file_path}' already exists. Do you want to skip it and continue? (y/n): ").lower()
            if user_choice == 'y':
                print(f"Skipping '{content_name}'...")
                continue
            else:
                # Modify the file name to prevent overwriting
                base_name, extension = os.path.splitext(original_torrent_file_path)
                index = 1
                while True:
                    new_file_name = f"{base_name}_{index}{extension}"
                    torrent_file_path = new_file_name
                    if not os.path.exists(torrent_file_path):
                        break
                    index += 1

        t = Torrent(path=content,
                    trackers=torrent_config['announce_urls'],
                    source=torrent_config['source'],
                    private=torrent_config['is_private'])
        t.generate()
        t.write(torrent_file_path)
        success = True

    return success


if __name__ == "__main__":
    create(r'conf', '.', "example")