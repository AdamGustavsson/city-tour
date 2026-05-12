---
name: city-tour-creator
description: Skapa ett komplett tur-paket (tour.json) för en guidad stadstur. Använd när användaren vill ha en walking tour i en stad, en historisk vandring, en tematisk promenad (litterär, arkitektonisk, kulinarisk, etc.) eller en personlig minnesvandring. Levererar JSON som öppnas i tour-app.html.
---

# city-tour-creator

Du hjälper användaren att skapa en guidad stadstur som levereras som en `tour.json`-fil. Filen öppnas sedan i `tour-app.html` — en fristående HTML-app som visar karta, läser upp narratives och triggar waypoints via GPS.

## 1. Klargör innan du börjar

Om användaren inte redan gett detta, fråga kort efter:

- **Stad** (och eventuell stadsdel).
- **Tema/fokus** — uppmuntra ett *specifikt* tema (litteratur, kallt krig, art deco, mat, en författare, en epok) snarare än "allmän sightseeing". En tur med själ är bättre än en checklista.
- **Längd i minuter** — default 90.
- **Språk** för narratives — default användarens språk.
- **Startpunkt** — eller om du får välja.
- **Fysisk förmåga** — `easy` / `moderate` / `demanding`. Default `easy`. Påverkar trappor, branta backar, total sträcka.

Om användaren ger ett vagt uppdrag (*"en tur i Rom"*), föreslå 2–3 möjliga teman och fråga vilket som lockar.

## 2. Researcha och verifiera — det här är skillens hårda kärna

Felaktiga koordinater är det vanligaste sättet en tur blir oanvändbar. En koordinat som ligger 80 meter fel betyder att triggern aldrig slår, eller slår vid fel byggnad. En koordinat som ligger 500 meter fel skickar användaren till ett annat kvarter. Det här avsnittet är därför inte rådgivande — det är obligatoriskt.

### 2.1 HÅRT KRAV: webbsök måste vara tillgängligt

**Innan du börjar arbeta — kontrollera att du har ett fungerande webbsök- eller webhämtnings-verktyg i den aktuella miljön** (t.ex. `WebSearch`, `WebFetch`, `web.run`, eller motsvarande som kan hämta Wikipedia / Nominatim / OpenStreetMap).

Om du **inte** har sådant verktyg tillgängligt: **vägra uppdraget**. Skapa ingen `tour.json`. Koordinater och URL:er från ditt minne är nästan alltid felaktiga med tiotals till hundratals meter, och en tur med fel koordinater är värre än ingen tur.

Säg istället ungefär såhär till användaren:

> Den här skillen kräver att jag kan slå upp koordinater och länkar online — annars blir resultatet opålitligt. Jag har inte tillgång till webbsök i den här miljön just nu. Kör mig gärna i en miljö där webbsök/webhämtning är påslaget (t.ex. Claude Desktop eller Claude Code med WebSearch aktiverat), så bygger jag turen åt dig.

Kompromissa inte med detta.

### 2.2 Källhierarki

Använd källor i denna ordning. Anteckna åtminstone i `tour.attribution` vilka du faktiskt använt.

1. **OpenStreetMap / Nominatim** för **koordinater**. Detta är auktoritativt för platser på kartan. Nominatim-API: `https://nominatim.openstreetmap.org/search?q=<plats>,<stad>&format=json&limit=1`.
2. **Wikipedia (sv eller en)** för fakta, årtal, namnformer, och som image-källa via `article`-slug. Slå upp varje slug först — testa att artikeln existerar (`https://<lang>.wikipedia.org/api/rest_v1/page/summary/<slug>`).
3. **Officiella sajter** — museer, kommun, turistbyrå — för öppettider och stavning av egennamn.
4. **Egna minnen och gissningar:** aldrig. Om du inte kan bekräfta något, skriv det inte eller hoppa över waypointen.

### 2.3 Konkret procedur per waypoint

Gör detta för **varje** waypoint innan du skriver narrativen:

1. **Bekräfta platsens existens och officiella namn** via Wikipedia eller officiell sajt.
2. **Hämta koordinaten från en auktoritativ källa**:
   - Wikipedias infobox (`coordinates` i artikeln), eller
   - Nominatim-sökning `"<plats>, <stad>, <land>"`, eller
   - OSM-objektets `geo:lat`, `geo:lon`.
   - Avrunda till **4 decimaler** (≈ 11 m precision). Verifiera att du inte bytt plats på lat/lng (i Sverige är lat ≈ 55–69, lng ≈ 11–24; i Sydeuropa lng är ofta negativ — t.ex. Lissabon –9).
3. **Verifiera fakta i narrativen** mot Wikipedia eller annan källa. Datum, namn, antal — varje sådan uppgift bör vara hämtad, inte mints.
4. **Plocka image-slug:en** direkt från Wikipedia-URLen (delen efter `/wiki/`). Använd alltid `_` istället för mellanslag och URL-encoda specialtecken (`%C3%A9` för `é`).
5. **Räkna avstånd till nästa waypoint** med haversine-formeln på de verifierade koordinaterna (eller använd `scripts/compute_distances.py` på din draft). Sätt `walk_to_next.distance_m` till ~1.2x fågelvägen för en realistisk gångväg, mer i bergiga eller krångliga kvarter.

### 2.4 Verktyg som följer med skillen

Skillen inkluderar tre Python-script under `scripts/` som du **ska köra mot din `tour.json` innan leverans**. Alla använder bara Python stdlib — inga `pip install`:

| Script | Syfte | Kräver internet |
|---|---|---|
| `scripts/validate_tour.py <fil>` | Strukturvalidering (schema, order, koord-intervall, radien 15–80 m, narrative-längd, https-länkar). Bör alltid passera. | Nej |
| `scripts/compute_distances.py <fil>` | Räknar haversine mellan dina koordinater, jämför mot `walk_to_next.distance_m` och totalsumman. Flaggar avstånd som är kortare än fågelvägen (omöjligt) eller > 2x fågelvägen (troligen fel koord). | Nej |
| `scripts/verify_coordinates.py <fil>` | Multi-källa: (1) Nominatim-drift, (2) Wikipedia-koordinat från waypointens `images.article`-slug, (3) kluster-outlier-check mot centroiden, (4) OSM-klass/typ för felmatchade features (t.ex. en kyrka som returnerar `highway:residential` = matchade gatan, inte byggnaden). Två oberoende källor inom 50 m = bekräftad. | Ja (Nominatim + Wikipedia) |

**Workflow:**

```
# 1. Du har skrivit tour.json
python3 scripts/validate_tour.py tour-min-tur.json
# 2. Strukturen ok — kontrollera geometrin
python3 scripts/compute_distances.py tour-min-tur.json
# 3. Slutligen verifiera koordinater mot OSM
python3 scripts/verify_coordinates.py tour-min-tur.json
```

Om `verify_coordinates.py` rapporterar fel: **rätta koordinaten innan leverans**. Om Nominatim inte hittar en plats men du har en stark Wikipedia-koordinat — det är ok, men anteckna i `tour.attribution`.

Om Python inte är tillgängligt i miljön: gör samma kontroller manuellt. Räkna åtminstone haversine på två-tre slumpvalda waypoint-par för att fånga ordersfel och inverterade lat/lng.

### 2.5 Om du fortfarande inte kan verifiera en specifik plats

Hoppa över waypointen, eller markera den som `optional: true` och var explicit i narrativen att den är osäker. Aldrig leverera en koordinat du gissat på.

## 3. Planera rutten geografiskt

- 6–10 waypoints för en 90-min tur. Hellre 8 starka stopp än 14 medioker.
- Logisk promenadordning — undvik back-tracking.
- Loop eller linje som slutar nära kollektivtrafik.
- Total sträcka:
  - 60 min ≈ 2.5 km
  - 90 min ≈ 3–5 km
  - 120 min ≈ 5–6 km
- Ta hänsyn till topografi, trappor, högtrafikerade vägar.
- Variera tempo: ett stort torg, sedan en stilla bakgata, sedan ett café.

## 4. Skriv waypoint-narratives

Detta är skillens hjärta. En tur står och faller på narrativen.

- **60–120 sekunder uppläst per stopp** = ungefär **150–280 ord**.
- Konversationell ton, som en kunnig vän — inte en faktaspruta.
- **Anekdoter framför fakta-uppräkning.** En historia om personen som dog här slår tio årtal.
- Använd små lokala fraser där det passar (en *bica*, en *cicchetto*) — utan att bli pretentiös.
- Undvik den generiska AI-rösten ("År 1503 byggdes denna kyrka..."). Skriv som om du står där.
- Adressera lyssnaren ibland: *"Titta upp till vänster — där, mellan andra och tredje våningen..."*

Se `references/waypoint-guide.md` för exempel sida vid sida av svag och stark text.

## 5. Använd rätt JSON-schema

Följ schemat i `references/tour-schema.json` exakt. Vanliga fallgropar:

- `order` måste vara 1-indexerad och konsekutiv (1, 2, 3, ...).
- `coordinates` är `[lat, lng]`, inte `[lng, lat]` (GeoJSON-konventionen är tvärtom — vi följer Leaflet).
- `trigger_radius_m` är 15–80. **Resonera så här:** koordinaten ligger ofta i mitten av en byggnad eller plats, men användaren befinner sig typiskt utanför entrén eller på motsatt trottoar när de "är framme". Radien måste täcka den realistiska *anflygningspunkten* — annars triggar appen aldrig och användaren tror att den är trasig.
  - Tumregel för byggnader: `(byggnadens längsta halv-dimension) + 10–15 m buffert`.
  - Specifik bänk, brunn eller staty: **15–20 m** (här står användaren rakt på koordinaten).
  - Liten butik, café, dörr: **25–30 m**.
  - Kyrka eller normal byggnad: **40–50 m**.
  - Stor byggnad (saluhall, katedral, museum med fasad mot flera gator): **50–70 m**.
  - Litet torg där användaren rör sig in: **40 m**.
  - Stort torg, park eller utsiktsplats: **60–80 m**.
  - **Tveka uppåt, inte nedåt.** En för stor radie triggar några sekunder tidigare än optimalt — irriterande, men turen flyter. En för liten triggar aldrig och bryter hela upplevelsen.
  - Bergsiga eller smala gränder med dålig GPS: lägg på **5–10 m**.
- Hitta aldrig på URL:er. Använd `images: [{ source: "wikipedia", article: "<slug>", lang: "en" }]` eller `{ source: "search_query", query: "..." }` istället.
- Wikipedia-slugs är artikelnamnet med understreck (`A_Brasileira`, inte `A Brasileira`).

## 6. Validera — kör alla tre scripten

Innan leverans, kör i ordning:

```
python3 scripts/validate_tour.py    <fil>   # struktur
python3 scripts/compute_distances.py <fil>  # geometri
python3 scripts/verify_coordinates.py <fil> # vs Nominatim
```

Alla tre måste sluta utan errors. Varningar (drift 100–500 m, ovanliga avstånd) ska du gå igenom manuellt och åtgärda eller motivera.

Om scripten inte kan köras i din miljö, gör motsvarande kontroller för hand:

- JSON parsar utan fel.
- `schema_version: "1.0"`.
- `waypoints.length >= 3`.
- Alla `coordinates` inom giltigt intervall.
- `order` 1-indexerad och konsekutiv.
- Total `distance_km` ≈ summa av `walk_to_next.distance_m / 1000`.
- `duration_minutes` ≈ promenadtid + uppläsningstid + spilltid.
- Två stickprov: räkna haversine för hand mellan första-andra och mitten-mitten+1, jämför mot dina `walk_to_next.distance_m`.

## 7. Leverera

Skapa filen som `tour-{city}-{theme}-{duration}min.json` (slug-format, små bokstäver, bindestreck). Exempel: `tour-lisboa-pessoa-90min.json`.

Beroende på runtime: skapa filen direkt om du kan, annars lägg JSON i ett `json`-codeblock med tydlig instruktion om att spara som `.json`-fil.

Avsluta med en kort sammanfattning till användaren:

> Klar! 8 stopp · 3.8 km · ~90 min · Pessoa-tema.
> Öppna `tour-app.html` i din webbläsare på mobilen, dra in filen, tryck Starta tur.

---

## Tänk så här om mindre uppenbara saker

### Vägbeskrivningar mellan stopp — gör inte det

Försök **inte** skriva text-baserade vägbeskrivningar mellan waypoints. Du kan inte avgöra enkelriktningar, trappor, aktuella avstängningar eller vilken hörna som är vilken — och fel där förstör flödet i turen. Appen löser det åt användaren via Google Maps-knappen "Navigera till nästa". Fyll i `walk_to_next.distance_m` och `walk_to_next.estimated_minutes`, inget mer.

### Stängda eller borttagna platser

Om en plats du minns kanske är borta (restaurang, butik): markera waypoint som `optional: true` och skriv narrative som om den möjligen är borta. *"Om dörren fortfarande står öppen — annars titta in genom skyltfönstret."* Lägg inte energi på att hitta på existens.

### Undvik den generiska AI-rösten

| Svag | Stark |
|---|---|
| "Denna kyrka byggdes år 1503 i gotisk stil." | "Lägg märke till hur dörrhandtagen är slitna blanka i mitten — fem hundra år av människor som dragit in sig själva i mässan." |
| "Författaren X var född här år 1888 och dog 1935." | "Han hyrde fjärde våningen och skrev där, i lönndom, under fyra olika namn. Granne under honom var en revisor som aldrig förstod varför ljuset alltid var tänt så sent." |
| "Detta är ett populärt café bland turister." | "Beställ en bica och stå vid baren — tre escudos extra om du sätter dig." |

### När du inte vet

Hitta inte på. Säg att du inte vet, eller hoppa över detaljen. En tur med 6 säkra stopp är mycket starkare än en med 10 där tre är hallucinationer.
