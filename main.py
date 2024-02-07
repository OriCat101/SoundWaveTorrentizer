from analyzer import get_flac_info

def get_user_input():
    flac_file_path = input("Enter the path to the FLAC file: ")
    output_folder = input("Enter the path to the output folder (press Enter for default 'output/spectrogram'): ")
    output_folder = output_folder.strip() or "output/spectrogram"
    return flac_file_path, output_folder

def main():
    flac_file_path, output_folder = get_user_input()
    flac_info = get_flac_info(flac_file_path, output_folder)

    print("\nFLAC Information:")
    for key, value in flac_info.items():
        print(f"{key.capitalize()}: {value}")

if __name__ == "__main__":
    main()
