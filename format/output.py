def bbcode(metadata):
  bbcode = "[table]\n"
  bbcode += "[tr]\n"
  bbcode += f"[td][b]Filename[/b][/td]\n"

  for key in metadata[list(metadata.keys())[0]]:
    bbcode += f"[td][b]{key.capitalize()}[/b][/td]\n"
  bbcode += "[/tr]\n"

  for track, track_info in metadata.items():
    bbcode += f"[tr]\n[td]{track}[/td]\n"
    for value in track_info.values():
      bbcode += f"[td]{value}[/td]\n"

    bbcode += "[/tr]\n"

  bbcode += "[/table]"
  return bbcode
