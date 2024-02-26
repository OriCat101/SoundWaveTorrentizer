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

def markdown(metadata):
    headers = ["Filename"] + [key.capitalize() for key in metadata[list(metadata.keys())[0]]]
    md_table = "| " + " | ".join(headers) + " |\n"
    
    md_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    for track, track_info in metadata.items():
        row = [track] + list(track_info.values())
        sanitized_row = [str(item).replace('[url]', '').replace('[/url]', '') for item in row]
        md_table += "| " + " | ".join(sanitized_row) + " |\n"
    
    return md_table