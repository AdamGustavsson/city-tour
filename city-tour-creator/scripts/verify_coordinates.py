#!/usr/bin/env python3
"""
verify_coordinates.py — multi-source coordinate verification for tour.json.

For each waypoint, runs four checks and reports per-check results:

  1. Nominatim search:  "<title>, <city>"  → expect drift < 100m.
  2. Wikipedia coords:  if the waypoint has a wikipedia image source,
                        fetch the article summary and compare coords.
  3. Cluster bbox:      every waypoint must be within a sane distance
                        of the cluster centroid (catches gross outliers
                        like "wrong city").
  4. OSM class/type:    print what kind of feature Nominatim returned
                        so the agent can spot mismatches (e.g. a church
                        waypoint returning `class=highway`).

Two confirming sources (Nominatim + Wikipedia) within 50m is the gold
standard; flag and re-check anything else.

Exit 0 if no likely errors. Exit 1 if errors found.

Usage:
    python3 verify_coordinates.py path/to/tour.json
"""
import json, math, sys, time, urllib.parse, urllib.request

NOMINATIM = "https://nominatim.openstreetmap.org/search"
WIKI_SUMMARY = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{slug}"
UA = "city-tour-creator/1.0 (skill verification)"

# Distance thresholds (meters)
DRIFT_WARN = 100
DRIFT_ERR = 500
CROSS_SOURCE_OK = 50           # Nominatim+Wikipedia agree within this -> green
CLUSTER_OUTLIER_FACTOR = 3.0   # > this * median distance from centroid -> outlier


def haversine(a, b):
    R = 6371000.0
    lat1, lng1 = math.radians(a[0]), math.radians(a[1])
    lat2, lng2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlng/2)**2
    return 2 * R * math.asin(math.sqrt(h))


def http_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def nominatim_search(query):
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1,
                                     "addressdetails": 1})
    data = http_json(f"{NOMINATIM}?{params}", {"Accept-Language": "en"})
    if not data:
        return None
    d = data[0]
    return {
        "coord": (float(d["lat"]), float(d["lon"])),
        "class": d.get("class"),
        "type": d.get("type"),
        "name": d.get("display_name", ""),
    }


def wikipedia_coord(slug, lang):
    try:
        url = WIKI_SUMMARY.format(lang=lang, slug=urllib.parse.quote(slug))
        data = http_json(url)
    except Exception:
        return None
    c = data.get("coordinates") or {}
    if "lat" in c and "lon" in c:
        return (float(c["lat"]), float(c["lon"]))
    return None


def cluster_check(waypoints):
    """Return dict id -> distance from cluster centroid, plus median."""
    coords = [w["coordinates"] for w in waypoints]
    cx = sum(c[0] for c in coords) / len(coords)
    cy = sum(c[1] for c in coords) / len(coords)
    distances = {}
    for w in waypoints:
        distances[w["id"]] = haversine(w["coordinates"], [cx, cy])
    sorted_d = sorted(distances.values())
    median = sorted_d[len(sorted_d) // 2]
    return distances, median


def fmt_class(r):
    if not r:
        return ""
    return f"{r['class']}:{r['type']}" if r.get("class") else ""


def main():
    if len(sys.argv) != 2:
        print("Usage: verify_coordinates.py <tour.json>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)

    tour = data["tour"]
    city = tour.get("city", "")
    country = tour.get("country", "")
    suffix = f", {city}" + (f", {country}" if country else "")

    waypoints = data["waypoints"]
    cluster_dist, median_dist = cluster_check(waypoints)
    outlier_threshold = max(median_dist * CLUSTER_OUTLIER_FACTOR, 1000)

    print(f"Tour: {tour.get('title')!r}  ({city})\n")
    print(f"{'#':>2}  {'Title':40}  {'Nominatim':>10}  {'Wikipedia':>10}  {'Cluster':>9}  OSM class")
    print("-" * 110)

    n_err = 0
    n_warn = 0

    for w in waypoints:
        title = w["title"]
        coord = w["coordinates"]

        # 1. Nominatim
        try:
            nom = nominatim_search(title + suffix)
            time.sleep(1.1)
        except Exception as e:
            nom = None
            print(f"  Nominatim fetch error for {title!r}: {e}", file=sys.stderr)
        nom_drift_str = "—"
        nom_drift = None
        if nom:
            nom_drift = haversine(coord, nom["coord"])
            nom_drift_str = f"{int(nom_drift)}m"

        # 2. Wikipedia (if waypoint has a wikipedia image source)
        wiki_drift = None
        wiki_drift_str = "—"
        for img in w.get("images") or []:
            if img.get("source") == "wikipedia":
                wc = wikipedia_coord(img["article"], img.get("lang", "en"))
                if wc:
                    wiki_drift = haversine(coord, wc)
                    wiki_drift_str = f"{int(wiki_drift)}m"
                    break

        # 3. Cluster
        cdist = cluster_dist[w["id"]]
        cluster_str = f"{int(cdist)}m"
        cluster_outlier = cdist > outlier_threshold

        # 4. OSM class
        cls = fmt_class(nom)

        # Decide flag
        flag = ""
        # Two sources agree closely → strong green
        if nom_drift is not None and wiki_drift is not None:
            if max(nom_drift, wiki_drift) < CROSS_SOURCE_OK:
                flag = "✓ confirmed"
            elif abs(nom_drift - wiki_drift) > 200 and min(nom_drift, wiki_drift) < 50:
                # One source agrees, one disagrees — Nominatim may have matched wrong feature
                flag = "OK (one source)"
        # Errors
        if (nom_drift is not None and nom_drift > DRIFT_ERR) and (wiki_drift is None or wiki_drift > DRIFT_ERR):
            flag = "ERROR — coord likely wrong"; n_err += 1
        elif cluster_outlier:
            flag = f"ERROR — cluster outlier ({int(cdist)}m vs median {int(median_dist)}m)"; n_err += 1
        elif (nom_drift is not None and nom_drift > DRIFT_WARN) and (wiki_drift is None or wiki_drift > DRIFT_WARN):
            flag = "WARN — drift > 100m, verify"; n_warn += 1

        print(f"  {w['order']:>2}  {title[:40]:40}  {nom_drift_str:>10}  {wiki_drift_str:>10}  {cluster_str:>9}  {cls:25} {flag}")

    print("-" * 110)
    print(f"Cluster: median dist from centroid = {int(median_dist)}m, "
          f"outlier threshold = {int(outlier_threshold)}m")
    print(f"Result: {n_err} likely error(s), {n_warn} warning(s).")
    print()
    print("Reading the columns:")
    print("  Nominatim/Wikipedia drift: distance from your coord to that source's coord.")
    print("  Both < 50m   => coordinate is confirmed by two independent sources.")
    print("  One source   => acceptable but eyeball it on a map.")
    print("  Cluster      => distance from the centroid of all waypoints; outliers")
    print("                  usually mean a coord landed in the wrong neighbourhood.")
    print("  OSM class    => what kind of feature Nominatim matched. A church waypoint")
    print("                  returning `highway:residential` means it matched a street,")
    print("                  not the building — investigate.")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
