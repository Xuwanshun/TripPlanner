import os
import requests
from dotenv import load_dotenv

load_dotenv()
import os
print(f"[{os.getenv('SERPER_API_KEY')}]")

url = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": os.getenv("SERPER_API_KEY"),
    "Content-Type": "application/json"
}
payload = {"q": "Toronto weather"}

response = requests.post(url, headers=headers, json=payload)

print(response.status_code)
print(response.text)