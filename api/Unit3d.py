import requests

wip_disclamer = "[i]This is a upload done with my WIP uploader script ([url]https://github.com/OriCat101/SoundWaveTorrentizer[/url]). If something isn't as expected please leave a comment or open a github issue[/i]"


def authenticate(api_url, token):
  headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
  }
  endpoint = '/api/torrents/upload'
  url = f'{api_url}{endpoint}'

  try:
    response = requests.post(url, headers=headers)

    if response.ok:
      return response.json()
    else:
      print(f'Error: {response.status_code} - {response.text}')
      return None

  except requests.RequestException as e:
    print(f'Request Exception: {e}')
    return None


if __name__ == "__main__":
  api_url = r""
  token = r""
  response = authenticate(api_url, token)
  print(response)
  print("Done.")