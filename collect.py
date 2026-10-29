import base64
import re
import requests
from bs4 import BeautifulSoup

CHANNELS = ["SOSkeyNET", "freedom_iran_npv"]
PATTERN = re.compile(r"(?:vmess|vless|trojan|ss)://[^\s<>\"']+")

def fetch_channel(name):
    r = requests.get(f"https://t.me/s/{name}", timeout=30,
                     headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    found = []
    for div in soup.select(".tgme_widget_message_text"):
        text = div.get_text("\n")
        found.extend(PATTERN.findall(text))
    return found

def main():
    configs = []
    for ch in CHANNELS:
        try:
            configs.extend(fetch_channel(ch))
        except Exception as e:
            print(f"خطا در {ch}: {e}")
    configs = list(dict.fromkeys(configs))
    print(f"{len(configs)} کانفیگ پیدا شد")
    if configs:
        data = base64.b64encode("\n".join(configs).encode()).decode()
        with open("sub.txt", "w") as f:
            f.write(data)

main()
