#!/usr/bin/env python3
"""Busca a contagem de Google Reviews na home do braboscleaning.com
e publica no relogio Ulanzi/AWTRIX via flespi MQTT (REST).

Roda no GitHub Actions a cada 30 minutos. Sem dependencias externas.
Mensagens publicadas como "retained": o broker guarda a ultima e
entrega na hora quando o relogio liga/reconecta.
"""
import json
import os
import re
import sys
import urllib.request

SITE = "https://braboscleaning.com/"
TOKEN = os.environ["FLESPI_TOKEN"]
PREFIX = "awtrix_9da880"  # prefixo MQTT configurado no relogio
APP = "googlereviews"

GREEN = "#8DC63F"   # verde BraBos
YELLOW = "#FFC400"  # estrelas
ICON = "23565"      # G colorido fundo preto (ja baixado no relogio)

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


def get_count():
    req = urllib.request.Request(SITE, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    m = re.search(r"(\d{2,4})\+?\s*Five-Star", html) or re.search(
        r"With (\d{2,4}) five-star", html, re.I
    )
    return m.group(1) if m else None


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
        headers={
            "Authorization": "FlespiToken " + TOKEN,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=30).status


def main():
    num = get_count()
    if not num:
        print("ERRO: contagem nao encontrada na home")
        sys.exit(1)

    # Mantem apps nativos desligados (resiliente a reboot do relogio)
    publish(f"{PREFIX}/settings", {"TIM": False, "DAT": False, "HUM": False, "TEMP": False, "BAT": False})

    app = {"icon": ICON, "background": "000000", "draw": build_draw(num), "duration": 10}
    status = publish(f"{PREFIX}/custom/{APP}", app)
    print(f"OK: {num} reviews publicados (HTTP {status})")


if __name__ == "__main__":
    main()
