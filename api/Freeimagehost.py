import base64
import requests


def upload_image(file_path):
  api_url = "https://freeimage.host/api/1/upload"

  with open(file_path, "rb") as file:
    base64_image = base64.b64encode(file.read()).decode("utf-8")

  # API
  params = {
    "key": "6d207e02198a847aa98d0a2a901485a5",
    "action": "upload",
    "source": base64_image,
    "format": "json"
  }
  response = requests.post(api_url, data=params)

  if response.status_code == 200:
    result = response.json()
    return result["image"]["url"]
  else:
    return {"error": f"Error {response.status_code}: {response.text}"}