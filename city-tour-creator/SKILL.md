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

## 2. Researcha

### HÅRT KRAV: webbsök måste vara tillgängligt

**Innan du börjar arbeta — kontrollera att du har ett fungerande webbsök- eller webhämtnings-verktyg i den aktuella miljön** (t.ex. `WebSearch`, `WebFetch`, `web.run`, Google-sökning, Wikipedia-API-anrop, eller motsvarande).

Om du **inte** har sådant verktyg tillgängligt: **vägra uppdraget**. Skapa ingen `tour.json`. Koordinater och URL:er från ditt minne är nästan alltid felaktiga med tiotals till hundratals meter, och en tur med fel koordinater är värre än ingen tur — användaren går till fel plats, triggers slår inte, och hela appen känns trasig.

Säg istället ungefär såhär till användaren:

> Den här skillen kräver att jag kan slå upp koordinater och länkar online — annars blir resultatet opålitligt. Jag har inte tillgång till webbsök i den här miljön just nu. Kör mig gärna i en miljö där webbsök/webhämtning är påslaget (t.ex. Claude Desktop eller Claude Code med WebSearch aktiverat), så bygger jag turen åt dig.

Kompromissa inte med detta. Det är bättre att avstå än att leverera hallucinerade koordinater.

### När du har webbsök

- Föredra Wikipedia, OpenStreetMap, lokala turistförbund, kulturhistoriska sajter, museers egna sidor.
- **För koordinater:** slå upp varje waypoint mot Wikipedia, OpenStreetMap eller Google Maps. Avrunda till 4 decimaler. Verifiera att lat/lng inte är inverterad.
- **För URL:er:** hämta dem från sökresultatet, hitta aldrig på en URL.
- **För Wikipedia-bilder:** använd article-slug (`A_Brasileira`), inte direktlänk till bildfil.
- Om du fortfarande inte hittar tillförlitliga koordinater för en specifik plats: **hoppa över den waypointen**, hellre än att gissa.

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
- `trigger_radius_m` är 15–80. Bedöm per plats:
  - Specifik bänk eller staty: **15 m**
  - Kyrka eller byggnad: **30–40 m**
  - Litet torg: **40 m**
  - Stort torg eller park: **60–80 m**
- Hitta aldrig på URL:er. Använd `images: [{ source: "wikipedia", article: "<slug>", lang: "en" }]` eller `{ source: "search_query", query: "..." }` istället.
- Wikipedia-slugs är artikelnamnet med understreck (`A_Brasileira`, inte `A Brasileira`).

## 6. Validera

Innan leverans, kontrollera:

- JSON är giltig (parsa det själv).
- `schema_version: "1.0"` finns.
- `waypoints.length >= 3`.
- Alla `coordinates` är inom giltigt intervall (lat ±90, lng ±180).
- `order` 1-indexerad och konsekutiv.
- Räkna total `distance_km` genom att summera `walk_to_next.distance_m` och dividera med 1000.
- `duration_minutes` ≈ promenadtid + uppläsningstid + lite spilltid.

## 7. Leverera

Skapa filen som `tour-{city}-{theme}-{duration}min.json` (slug-format, små bokstäver, bindestreck). Exempel: `tour-lisboa-pessoa-90min.json`.

Beroende på runtime: skapa filen direkt om du kan, annars lägg JSON i ett `json`-codeblock med tydlig instruktion om att spara som `.json`-fil.

Avsluta med en kort sammanfattning till användaren:

> Klar! 8 stopp · 3.8 km · ~90 min · Pessoa-tema.
> Öppna `tour-app.html` i din webbläsare på mobilen, dra in filen, tryck Starta tur.

---

## Tänk så här om mindre uppenbara saker

### Övergångar (`walk_to_next.directions_hint`)

Inte turn-by-turn. Appen har en Google Maps-knapp för det. Skriv en *minnesregel* för riktning, gärna med en visuell ledtråd:

- Svagt: *"Gå 320 m åt nordväst."*
- Starkt: *"Följ Rua Garrett nedför mot floden — du ser Tejo glimta längst ner."*

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
