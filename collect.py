import base64
import json
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

CHANNELS = ["SOSkeyNET", "freedom_iran_npv"]
PATTERN = re.compile(r"(?:vmess|vless|trojan|ss)://[^\s<>\"']+")
TIMEOUT = 4


def fetch_channel(name):
    r = requests.get(f"https://t.me/s/{name}", timeout=30,
                     headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    found = []
    for div in soup.select(".tgme_widget_message_text"):
        found.extend(PATTERN.findall(div.get_text("\n")))
    return found


def b64decode(s):
    s = s.replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * (-len(s) % 4)).decode()


def host_port(link):
    try:
        if link.startswith("vmess://"):
            d = json.loads(b64decode(link[8:].split("#")[0]))
            return d["add"], int(d["port"])
        u = urlparse(link)
        if u.hostname and u.port:
            return u.hostname, u.port
        if link.startswith("ss://"):
            inner = b64decode(link[5:].split("#")[0])
            hp = inner.rsplit("@", 1)[1]
            h, p = hp.rsplit(":", 1)
            return h, int(p)
    except Exception:
        pass
    return None


def is_alive(link):
    hp = host_port(link)
    if hp is None:
        return True  # اگه پارس نشد، نگهش می‌داریم
    try:
        with socket.create_connection(hp, timeout=TIMEOUT):
            return True
    except Exception:
        return False


def main():
    configs = []
    for ch in CHANNELS:
        try:
            configs.extend(fetch_channel(ch))
        except Exception as e:
            print(f"خطا در {ch}: {e}")
    configs = list(dict.fromkeys(configs))
    print(f"{len(configs)} کانفیگ پیدا شد")

    with ThreadPoolExecutor(max_workers=50) as ex:
        results = list(ex.map(is_alive, configs))
    alive = [c for c, ok in zip(configs, results) if ok]
    print(f"{len(alive)} کانفیگ سالم ماند")

    if alive:  # اگه چیزی نموند، فایل قبلی رو خراب نکن
        data = base64.b64encode("\n".join(alive).encode()).decode()
        with open("sub.txt", "w") as f:
            f.write(data)


main()
