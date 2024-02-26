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
    
    if torrent_config is None:
        return False
    
    required_keys = {'announce_urls', 'source', 'is_private'}
    if not required_keys.issubset(torrent_config.keys()):
        print("Configuration data is missing some required keys.")
        return False
    
    success = False
    created_torrents = []

    for content in contents:
        if not os.path.exists(content):
            print(f"Content path does not exist: {content}")
            continue
        
        content_name = os.path.basename(content)
        torrent_file_path = os.path.join(save_path, f"{content_name}.torrent")
        
        if os.path.exists(torrent_file_path):
            user_choice = input(f"'{torrent_file_path}' already exists. Do you want to overwrite it? (y/n): ").lower()
            if user_choice != 'y':
                print(f"Skipping '{content_name}'...")
                continue
        try:
            os.makedirs(os.path.dirname(torrent_file_path), exist_ok=True)  # Make sure the torrent file directory exists
        except Exception as e:
            print(f"Failed to create directory for torrent file: {e}")
            continue

        try:
            t = Torrent(path=content,
                        trackers=torrent_config['announce_urls'],
                        source=torrent_config['source'],
                        private=torrent_config['is_private'])
            t.generate()
            t.write(torrent_file_path)
            print(f"Torrent file created: {torrent_file_path}")
            created_torrents.append(torrent_file_path)
            success = True
        except Exception as e:
            print(f"Failed to create torrent for {content}. Error: {e}")
    
    return success, created_torrents


if __name__ == "__main__":
    create(r'conf', '.', "example")
