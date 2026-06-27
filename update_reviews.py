#!/usr/bin/env python3
"""Busca a contagem REAL de Google Reviews somando os 3 perfis do BraBos
(Boston, Newton, Cambridge) via Google Places API e publica no relogio
Ulanzi/AWTRIX via flespi MQTT (REST).

Roda no GitHub Actions a cada 30 minutos. Sem dependencias externas.
Se a API falhar, NAO publica: a mensagem retida anterior continua na tela
(nunca mostra numero velho como se fosse o atual).
"""
import json
import os
import sys
import urllib.parse
import urllib.request

TOKEN = os.environ["FLESPI_TOKEN"]
GOOGLE_KEY = os.environ["GOOGLE_MAPS_API_KEY"]
PREFIX = "awtrix_9da880"
APP = "googlereviews"

PLACE_IDS = [
    "ChIJJ4WMj8rd1AwRwuQ7FtVQu6g",  # Boston
    "ChIJu-KuugB544kRbcPZW0m2tM0",  # Newton
    "ChIJB3RyybVx44kRpE98r82kuNU",  # Cambridge
]

GREEN = "#8DC63F"
YELLOW = "#FFC400"
ICON = "23565"

FONT = {
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", "###", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", "..#", "..#", "..#"],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
}


def place_total(place_id):
    """user_ratings_total de um place_id (levanta excecao se falhar)."""
    url = "https://maps.googleapis.com/maps/api/place/details/json?" + urllib.parse.urlencode(
        {"place_id": place_id, "fields": "user_ratings_total", "key": GOOGLE_KEY}
    )
    req = urllib.request.Request(url, headers={"User-Agent": "brabos-awtrix"})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    if data.get("status") != "OK":
        raise RuntimeError(f"Places API status={data.get('status')} ({place_id})")
    return int(data["result"]["user_ratings_total"])


def get_count():
    total = sum(place_total(pid) for pid in PLACE_IDS)
    if not (0 < total <= 9999):  # sanidade
        raise RuntimeError(f"total implausivel: {total}")
    return str(total)


def build_draw(num):
    draw = []
    w = len(num) * 4 - 1
    x0 = 10 + max(0, (19 - w) // 2)
    for i, ch in enumerate(num):
        for y, row in enumerate(FONT[ch]):
            for x, c in enumerate(row):
                if c == "#":
                    draw.append({"dp": [x0 + i * 4 + x, y, GREEN]})
    for i in range(5):  # 5 estrelas
        sx, sy = 10 + i * 4, 5
        for px, py in [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]:
            draw.append({"dp": [sx + px, sy + py, YELLOW]})
    return draw


def publish(topic, payload):
    body = json.dumps(
        {"topic": topic, "payload": json.dumps(payload), "retained": True}
    ).encode()
    req = urllib.request.Request(
        "https://flespi.io/mqtt/messages",
        data=body,
        headers={"Authorization": "FlespiToken " + TOKEN, "Content-Type": "application/json"},
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=30).status


def main():
    try:
        num = get_count()
    except Exception as e:
        print(f"ERRO ao buscar contagem: {e}")
        print("Nada publicado -- relogio mantem o ultimo valor (msg retida).")
        sys.exit(1)

    publish(f"{PREFIX}/settings", {"TIM": False, "DAT": False, "HUM": False, "TEMP": False, "BAT": False})
    app = {"icon": ICON, "background": "000000", "draw": build_draw(num), "duration": 10}
    status = publish(f"{PREFIX}/custom/{APP}", app)
    print(f"OK: {num} reviews publicados (HTTP {status})")


if __name__ == "__main__":
    main()
