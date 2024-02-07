import analyzer
def main():
    album_path=input("Album folder: ")
    upload_spectrogram = input("Upload spectrogram? (y/n, default=n): ")
    if upload_spectrogram.lower() == "y":
        upload_spectrogram = True
    else:
        upload_spectrogram = False

    album_meta=analyzer.analyze_album(album_path, upload_spectrogram)
    print(analyzer.generate_bbcode_table(album_meta))
    # print(album_meta)

if __name__ == "__main__":
    main()
