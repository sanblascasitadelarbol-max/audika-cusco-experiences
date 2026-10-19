#!/usr/bin/env python3
"""Genera disponibilidad desde calendarios iCal privados de Airbnb."""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path

IDS = set("104-A 104-B 104 104-2 103 101 102 101-102 106-1 106-2 401 402 403 andina 105-1 105-full 107".split())
OUT = Path(__file__).resolve().parents[1] / "web_publica" / "disponibilidad.json"

def date(prop):
    value = prop.split(":", 1)[-1].strip()
    if not re.fullmatch(r"\d{8}(T\d{6}Z?)?", value):
        raise ValueError("Fecha iCal inesperada")
    return f"{value[:4]}-{value[4:6]}-{value[6:8]}"

def parse_ical(raw):
    text = re.sub(r"\n[ \t]", "", raw.replace("\r\n", "\n").replace("\r", "\n"))
    if "BEGIN:VCALENDAR" not in text or "END:VCALENDAR" not in text:
        raise ValueError("Respuesta no es un calendario")
    result = []
    for event in re.findall(r"(?m)^BEGIN:VEVENT\n(.*?)^END:VEVENT\s*$", text, re.S | re.M):
        properties = {}
        for line in event.split("\n"):
            if ":" in line:
                properties.setdefault(line.split(":", 1)[0].split(";", 1)[0].upper(), []).append(line)
        if any(line.rsplit(":", 1)[-1].strip().upper() == "CANCELLED" for line in properties.get("STATUS", [])):
            continue
        if any(line.rsplit(":", 1)[-1].strip().upper() == "TRANSPARENT" for line in properties.get("TRANSP", [])):
            continue
        if not properties.get("DTSTART") or not properties.get("DTEND"):
            raise ValueError("Evento sin fechas")
        start, end = date(properties["DTSTART"][0]), date(properties["DTEND"][0])
        if start < end:
            result.append({"start": start, "end": end})
    return sorted(result, key=lambda v: (v["start"], v["end"]))

def main():
    feeds = json.loads(os.environ["AUDIKA_ICAL_FEEDS_JSON"])
    if not isinstance(feeds, dict) or set(feeds) != IDS:
        raise ValueError("Se esperan exactamente 17 calendarios")
    for key, url in feeds.items():
        if not isinstance(url, str) or not re.fullmatch(r"https://www\.airbnb\.com\.pe/calendar/ical/\d+\.ics\?t=[0-9a-f]+", url):
            raise ValueError("URL inválida en " + key)
    results = {"updatedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "checked": [], "blocked": {}, "errors": []}
    for key in sorted(IDS):
        try:
            request = urllib.request.Request(feeds[key], headers={"User-Agent": "Mozilla/5.0", "Accept": "text/calendar"})
            with urllib.request.urlopen(request, timeout=25) as response:
                if response.status != 200:
                    raise ValueError("Respuesta HTTP inesperada")
                raw = response.read(4_000_001)
                if len(raw) > 4_000_000:
                    raise ValueError("Calendario demasiado grande")
            result = parse_ical(raw.decode("utf-8-sig"))
            results["checked"].append(key)
            results["blocked"][key] = result
        except Exception as exc:
            results["errors"].append(key)
            print("Sin verificación para", key, type(exc).__name__)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Calendarios verificados:", len(results["checked"]), "/ 17")
    if not results["checked"]:
        raise SystemExit("No se ha confirmado ningún calendario; publicación detenida.")

if __name__ == "__main__":
    main()
