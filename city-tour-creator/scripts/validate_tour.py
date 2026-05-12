#!/usr/bin/env python3
"""
validate_tour.py — strukturvalidering av en tour.json.

Kontrollerar:
- schema_version finns och är "1.0"
- alla obligatoriska tour-fält finns
- minst 3 waypoints
- order är 1-indexerad och konsekutiv
- coordinates är inom giltigt lat/lng-intervall
- trigger_radius_m inom 15..80
- bild-källor är giltiga (wikipedia/search_query/local)
- länkar börjar med https://
- narrative >= 50 tecken

Exit-kod 0 = giltig, 1 = fel hittade.

Användning:
    python3 validate_tour.py path/to/tour.json
"""
import json, sys

REQ_TOUR = ["id", "title", "city", "language", "duration_minutes",
            "distance_km", "difficulty", "start_coordinates"]
REQ_WP = ["id", "order", "title", "coordinates", "short", "narrative"]
DIFFICULTIES = {"easy", "moderate", "demanding"}


def err(errors, path, msg):
    errors.append(f"  {path}: {msg}")


def valid_latlng(c):
    return (isinstance(c, list) and len(c) == 2
            and all(isinstance(x, (int, float)) for x in c)
            and -90 <= c[0] <= 90 and -180 <= c[1] <= 180)


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["root: not a JSON object"]

    if data.get("schema_version") != "1.0":
        err(errors, "schema_version", f"expected '1.0', got {data.get('schema_version')!r}")

    t = data.get("tour")
    if not isinstance(t, dict):
        err(errors, "tour", "missing or not an object")
    else:
        for f in REQ_TOUR:
            if f not in t:
                err(errors, f"tour.{f}", "missing")
        if "start_coordinates" in t and not valid_latlng(t["start_coordinates"]):
            err(errors, "tour.start_coordinates", f"invalid lat/lng: {t['start_coordinates']}")
        if "difficulty" in t and t["difficulty"] not in DIFFICULTIES:
            err(errors, "tour.difficulty", f"must be one of {DIFFICULTIES}")
        if "duration_minutes" in t and not (15 <= t["duration_minutes"] <= 480):
            err(errors, "tour.duration_minutes", "should be 15..480")

    wps = data.get("waypoints")
    if not isinstance(wps, list):
        err(errors, "waypoints", "missing or not an array")
    elif len(wps) < 3:
        err(errors, "waypoints", f"need at least 3, got {len(wps)}")
    else:
        seen_ids = set()
        for i, w in enumerate(wps):
            p = f"waypoints[{i}]"
            if not isinstance(w, dict):
                err(errors, p, "not an object"); continue
            for f in REQ_WP:
                if f not in w:
                    err(errors, f"{p}.{f}", "missing")
            if "order" in w and w["order"] != i + 1:
                err(errors, f"{p}.order", f"expected {i+1}, got {w['order']}")
            if "coordinates" in w and not valid_latlng(w["coordinates"]):
                err(errors, f"{p}.coordinates", f"invalid: {w['coordinates']}")
            if "trigger_radius_m" in w:
                r = w["trigger_radius_m"]
                if not (15 <= r <= 80):
                    err(errors, f"{p}.trigger_radius_m", f"should be 15..80, got {r}")
            if "id" in w:
                if w["id"] in seen_ids:
                    err(errors, f"{p}.id", f"duplicate id {w['id']!r}")
                seen_ids.add(w["id"])
            if "narrative" in w and isinstance(w["narrative"], str) and len(w["narrative"]) < 50:
                err(errors, f"{p}.narrative", f"too short ({len(w['narrative'])} chars, min 50)")
            for j, img in enumerate(w.get("images") or []):
                if not isinstance(img, dict) or img.get("source") not in {"wikipedia", "search_query", "local"}:
                    err(errors, f"{p}.images[{j}]", f"invalid source: {img}")
            for j, lnk in enumerate(w.get("links") or []):
                if not isinstance(lnk, dict) or not str(lnk.get("url", "")).startswith("https://"):
                    err(errors, f"{p}.links[{j}].url", "must start with https://")
    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_tour.py <tour.json>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    errors = validate(data)
    if errors:
        print(f"INVALID — {len(errors)} error(s):")
        for e in errors:
            print(e)
        sys.exit(1)
    print(f"OK — {len(data['waypoints'])} waypoints, schema 1.0")


if __name__ == "__main__":
    main()
