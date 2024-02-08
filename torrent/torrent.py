import os

from torf import Torrent
import json

def load_tracker_config(config_name):
    """
    Load tracker configuration from a JSON file.

    Parameters:
    - config_name (str): The name of the configuration file.

    Returns:
    - dict: Dictionary containing the loaded configuration data.
    """
    config_file = f"conf/{config_name}.json"
    with open(config_file, 'r') as file:
        config_data = json.load(file)
    return config_data

def create_torrent(content, save_path, config_name):
    """
    Create a torrent file using the specified content and configuration.

    Parameters:
    - content (str): The path to the content to be included in the torrent.
    - save_path (str): The path where the generated torrent file will be saved.
    - config_name (str): The name of the configuration file without the extension.
    """
    torrent_config = load_tracker_config(config_name)
    content_name = os.path.basename(content)

    t = Torrent(path=content,
                trackers=torrent_config.get('announce_urls'),
                source=torrent_config.get('source'),
                private=torrent_config.get('is_private'))
    t.generate()
    t.write(f'{save_path}/{content_name}.torrent')

if __name__ == "__main__":
    create_torrent(r'conf', '.', "example")
