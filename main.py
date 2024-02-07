import analyzer
def main():
    album_path=input("Album folder: ")
    album_meta=analyzer.analyze_album(album_path)
    print(analyzer.generate_bbcode_table(album_meta))

if __name__ == "__main__":
    main()
