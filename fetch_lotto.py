import json
import urllib.request
import xml.etree.ElementTree as ET
import re

RSS_URL = "https://www.lotto.de/api/feed/rss/6aus49"

def get_draws():
    req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    root = ET.fromstring(html)

    wednesday = []
    saturday = []

    for item in root.findall('./channel/item'):
        title = item.find('title').text or ""
        desc = item.find('description').text or ""

        # Datum extrahieren
        date_match = re.search(r'\b(\d{1,2}\.\d{1,2}\.\d{2,4})\b', title + " " + desc)
        date_str = date_match.group(1) if date_match else ""

        # 6 Gewinnzahlen (1-49) suchen
        numbers = []
        for n in re.findall(r'\b\d{1,2}\b', desc):
            val = int(n)
            if 1 <= val <= 49 and val not in numbers:
                numbers.append(val)
            if len(numbers) == 6:
                break

        # Superzahl (0-9) suchen
        super_match = re.search(r'Superzahl[:\s]+(\d)', desc)
        super_num = int(super_match.group(1)) if super_match else 0

        if len(numbers) == 6 and date_str:
            draw_data = {
                "date": date_str,
                "numbers": sorted(numbers),
                "superNumber": super_num
            }
            if "mittwoch" in title.lower() and len(wednesday) < 3:
                wednesday.append(draw_data)
            elif "samstag" in title.lower() and len(saturday) < 3:
                saturday.append(draw_data)

    return {"wednesday": wednesday, "saturday": saturday}

if __name__ == "__main__":
    data = get_draws()
    if data["wednesday"] or data["saturday"]:
        with open("lotto.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("lotto.json erfolgreich aktualisiert!")
    else:
        print("Keine neuen Daten gefunden.")
