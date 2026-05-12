#!/usr/bin/env python3
"""
compute_distances.py — räkna om avstånd mellan waypoints och jämför
med det som står i tour.json.

Använder haversine (fågelvägs-avstånd). En riktig gång-rutt är
typiskt 1.15–1.35x fågelvägs-avståndet i en rutnätsstad. Skriptet
flaggar walk_to_next.distance_m som verkar orimligt liten (< 0.9x
fågelväg) eller orimligt stor (> 2.0x fågelväg) — en stark hint om
att en koordinat är fel eller att avståndet är gissat.

Användning:
    python3 compute_distances.py path/to/tour.json
"""
import json, math, sys


def haversine(a, b):
    R = 6371000.0
    lat1, lng1 = math.radians(a[0]), math.radians(a[1])
    lat2, lng2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlng/2)**2
    return 2 * R * math.asin(math.sqrt(h))


def main():
    if len(sys.argv) != 2:
        print("Usage: compute_distances.py <tour.json>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)

    wps = data["waypoints"]
    total_birdline = 0.0
    total_claimed = 0
    warnings = []

    print(f"{'#':>2}  {'Title':40}  {'Birdline':>8}  {'Claimed':>8}  {'Ratio':>6}  Note")
    print("-" * 88)
    for i in range(len(wps) - 1):
        a, b = wps[i], wps[i+1]
        bird = haversine(a["coordinates"], b["coordinates"])
        claimed = (a.get("walk_to_next") or {}).get("distance_m")
        ratio_str = ""
        note = ""
        if claimed is not None:
            ratio = claimed / bird if bird > 0 else 0
            ratio_str = f"{ratio:.2f}x"
            if ratio < 0.9:
                note = "WARN: shorter than birdline — coord likely wrong"
                warnings.append((i, a["title"], b["title"], note))
            elif ratio > 2.0:
                note = "WARN: much longer than birdline — recheck"
                warnings.append((i, a["title"], b["title"], note))
            total_claimed += claimed
        total_birdline += bird
        print(f"{i+1:>2}  {a['title'][:40]:40}  {int(bird):>6}m  "
              f"{(str(claimed)+'m' if claimed is not None else '—'):>8}  {ratio_str:>6}  {note}")

    # Total
    total_km_claimed = data["tour"].get("distance_km")
    print("-" * 88)
    print(f"Total birdline:  {total_birdline/1000:.2f} km")
    if total_claimed:
        print(f"Total claimed (sum walk_to_next): {total_claimed/1000:.2f} km")
    if total_km_claimed is not None:
        print(f"tour.distance_km field:           {total_km_claimed} km")
        # Real walking is ~1.2-1.4x birdline.
        ratio = total_km_claimed * 1000 / total_birdline if total_birdline else 0
        print(f"Ratio tour.distance_km / birdline: {ratio:.2f}x (expected 1.1–1.5x)")
        if ratio < 0.95:
            print("WARN: tour.distance_km is less than birdline — impossible.")
        elif ratio > 1.8:
            print("WARN: tour.distance_km much greater than birdline — recheck.")

    if warnings:
        print(f"\n{len(warnings)} warning(s) — review coordinates carefully.")
        sys.exit(1)
    print("\nDistances look consistent.")


if __name__ == "__main__":
    main()
