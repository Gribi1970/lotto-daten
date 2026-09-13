import json
import urllib.request
from datetime import datetime

API_URL = "https://services.lotto-hessen.de/spielinformationen/gewinnzahlen/lotto"

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    req = urllib.request.Request(API_URL, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        return json.loads(content)

def main():
    try:
        raw_data = fetch_data()
    except Exception as e:
        print(f"Fehler beim Laden der API: {e}")
        return

    # Lade existierende Daten, um bis zu 3 Ziehungen zu behalten
    try:
        with open("lotto.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except Exception:
        existing_data = {"wednesday": [], "saturday": []}

    wednesday = existing_data.get("wednesday", [])
    saturday = existing_data.get("saturday", [])

    # Die API liefert unter anderem: {"Datum":"...", "Ziehung":"Mittwoch", "Superzahl":..., "Zahl":[...]}
    # Oder ein verschachteltes Array
    items = raw_data if isinstance(raw_data, list) else [raw_data]

    for item in items:
        # Prüfe, ob die erwarteten Felder existieren
        date_str = item.get("Datum") or item.get("date") or ""
        numbers = item.get("Zahl") or item.get("numbers") or []
        super_num = item.get("Superzahl") if "Superzahl" in item else item.get("superNumber", 0)
        draw_type = item.get("Ziehung") or item.get("day") or ""

        if numbers and len(numbers) == 6:
            draw_entry = {
                "date": date_str,
                "numbers": sorted([int(x) for x in numbers]),
                "superNumber": int(super_num)
            }

            if "mittwoch" in draw_type.lower():
                if not any(d.get("date") == date_str for d in wednesday):
                    wednesday.insert(0, draw_entry)
            elif "samstag" in draw_type.lower():
                if not any(d.get("date") == date_str for d in saturday):
                    saturday.insert(0, draw_entry)

    # Jeweils auf maximal 3 Ziehungen begrenzen
    data_to_save = {
        "wednesday": wednesday[:3],
        "saturday": saturday[:3]
    }

    with open("lotto.json", "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)

    print("lotto.json erfolgreich geschrieben:")
    print(json.dumps(data_to_save, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
