#!/usr/bin/env python3
"""
verify_coordinates.py — verifiera waypoint-koordinater mot OpenStreetMaps
Nominatim API (gratis, ingen nyckel).

För varje waypoint:
- Slå upp "<title>, <city>" (eller "<title>, <city>, <country>") i Nominatim.
- Räkna avståndet mellan inlagd koordinat och det Nominatim returnerar.
- Flagga avstånd > 100 m som varning, > 500 m som troligt fel.

OBS: kräver internet. Nominatim har en användarpolicy (max 1 req/s,
identifierande User-Agent). Skriptet respekterar detta.

Användning:
    python3 verify_coordinates.py path/to/tour.json
"""
import json, math, sys, time, urllib.parse, urllib.request

NOMINATIM = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "city-tour-creator/1.0 (skill verification script)"


def haversine(a, b):
    R = 6371000.0
    lat1, lng1 = math.radians(a[0]), math.radians(a[1])
    lat2, lng2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlng/2)**2
    return 2 * R * math.asin(math.sqrt(h))


def nominatim_search(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    req = urllib.request.Request(f"{NOMINATIM}?{params}",
                                 headers={"User-Agent": USER_AGENT,
                                          "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    if not data:
        return None
    return (float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", ""))


def main():
    if len(sys.argv) != 2:
        print("Usage: verify_coordinates.py <tour.json>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)

    city = data["tour"].get("city", "")
    country = data["tour"].get("country", "")
    suffix = f", {city}" + (f", {country}" if country else "")

    print(f"Verifying against Nominatim — city: {city!r}\n")
    n_warn = 0
    n_err = 0
    for w in data["waypoints"]:
        query = w["title"] + suffix
        try:
            result = nominatim_search(query)
        except Exception as e:
            print(f"  {w['order']:>2}. {w['title']:40}  FETCH ERROR: {e}")
            time.sleep(1.1); continue
        if not result:
            print(f"  {w['order']:>2}. {w['title']:40}  NOT FOUND in Nominatim — verify manually")
            n_warn += 1
        else:
            lat, lng, name = result
            d = haversine(w["coordinates"], [lat, lng])
            flag = ""
            if d > 500:
                flag = "ERROR — likely wrong coord"; n_err += 1
            elif d > 100:
                flag = "WARN — drift > 100m"; n_warn += 1
            print(f"  {w['order']:>2}. {w['title']:40}  drift={int(d)}m  {flag}")
            if flag:
                print(f"        you: {w['coordinates']}")
                print(f"        osm: [{lat:.4f}, {lng:.4f}]  ({name[:80]})")
        time.sleep(1.1)  # Nominatim: max 1 req/s

    print()
    print(f"Result: {n_err} likely error(s), {n_warn} warning(s).")
    print("Note: Nominatim is OSM — not always perfect, especially for small places.")
    print("Drift > 500m almost always means a wrong coord; investigate manually.")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
