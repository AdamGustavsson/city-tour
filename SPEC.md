# Stadstur — SPEC

En guidad stadstur-app som följer det skill-distribuerande mönstret. Användaren ber sin AI generera ett tur-paket (JSON) via en medföljande skill, öppnar paketet i en single-file HTML-app, och går turen. BYOK kan låsa upp röstuppläsning. Navigering mellan waypoints sker via deep-link till Google Maps.

---

## 1. Två leverabler

Detta projekt levererar två saker som tillsammans utgör produkten:

1. **`city-tour-creator/`** — skill-paketet som distribueras till användarens AI (Claude Code, Claude Desktop, Codex, m.fl.). Innehåller `SKILL.md` + referensfiler + exempel.
2. **`tour-app.html`** — den fristående HTML-appen som öppnar en tur-JSON och kör turen.

Båda måste fungera tillsammans men distribueras separat: skillen installerar man i sin AI-runtime, appen öppnar man i en webbläsare.

---

## 2. End-to-end-flöde

1. Användaren installerar skillen i sin AI (eller distribuerar den ad hoc — kopiera in `SKILL.md` i samtalet).
2. Användaren ber sin AI: *"Skapa en 90-minuters stadstur i Lissabon med fokus på Pessoa, på svenska."*
3. AI:n ställer eventuella kompletteringsfrågor och researchar (sökverktyg om tillgängliga, annars eget vetande).
4. AI:n levererar ett komplett `tour.json` enligt schemat i denna spec.
5. Användaren öppnar `tour-app.html` i webbläsaren (på mobil, lokalt eller via valfri statisk hosting).
6. Användaren importerar `tour.json` (drag-and-drop eller filväljare). Tur cachas i `localStorage`.
7. Användaren tittar på översiktsvyn — karta, alla waypoints, beräknad sträcka och tid.
8. Användaren trycker **Starta tur** vid första waypoint.
9. Appen ber om geolocation-tillstånd. När användaren går mellan punkter visar appen avstånd och riktning till nästa.
10. Vid framme-trigger: waypoint-kortet öppnas, ev. röstuppläsning startar (om BYOK).
11. Användaren kan trycka **Navigera dit i Google Maps** för turn-by-turn-handoff.
12. Användaren markerar punkter som besökta, fortsätter till nästa, eller avviker fritt.
13. När turen är klar visas en sammanfattning. Anteckningar och progress finns kvar tills användaren rensar.

---

## 3. Designprinciper

- **Single-file HTML.** Appen är *en* fil. Inga byggsteg. Inga separata CSS/JS-filer. Dependencies via CDN i `<script>`-taggar.
- **Ingen backend.** Inget eget API, ingen databas, ingen authentication. All state lokal.
- **Inga API-nycklar krävs som baseline.** Karta, bilder och länkar fungerar utan nyckel. BYOK är opt-in och adderar funktion (röst), tar inte bort grundfunktion.
- **Mobile-first.** Primär målplattform är iPhone/Android i Safari/Chrome. Desktop ska fungera men prioriteras inte i UI-beslut.
- **Tolerant parser.** Appen ska acceptera mindre avvikelser i `tour.json` (saknade valfria fält, extra fält). Den ska aldrig krascha på en hallucinerad URL — bara dölja den eller markera den som trasig.
- **Privacy by default.** Inga analytics, ingen telemetri, inga tracker-cookies. Eventuella tredjepartsanrop (Wikipedia, kartttiles, TTS-providers) går direkt från klient, aldrig via egen server.

---

## 4. Teknisk stack

- HTML/CSS/Vanilla JS (ES2022). Inga frameworks. Inga byggsteg.
- **Leaflet 1.9+** för kartrendering (CDN).
- **OpenStreetMap-tiles** via `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` med attribution. Alternativt CARTO Voyager eller liknande gratis tile-server.
- **Browser-API:er:** Geolocation API, Web Speech API (för enkel TTS-fallback utan BYOK), IndexedDB (för audio-cache), localStorage (för state och inställningar), Wake Lock API (för att hålla skärmen på under aktiv tur).
- **Inga externa font-importer** — använd `system-ui, -apple-system, "Segoe UI", sans-serif`.

---

## 5. Filstruktur — leverans

```
deliverables/
├── tour-app.html                # Hela appen i en fil
├── city-tour-creator/           # Skill-paketet
│   ├── SKILL.md
│   └── references/
│       ├── tour-schema.json     # JSON Schema (Draft 2020-12)
│       ├── waypoint-guide.md    # Hur man skriver bra narrative
│       ├── routing-tips.md      # Promenadlogik
│       └── examples/
│           ├── stockholm-gamla-stan-60min.json
│           ├── roma-trastevere-2h.json
│           └── lisboa-pessoa-90min.json
└── README.md                    # Hur man kommer igång (för slutanvändaren)
```

---

## 6. Skill-paketet — `SKILL.md`

### Frontmatter (obligatorisk)

```yaml
---
name: city-tour-creator
description: Skapa ett komplett tur-paket (tour.json) för en guidad stadstur. Använd när användaren vill ha en walking tour i en stad, en historisk vandring, en tematisk promenad (litterär, arkitektonisk, kulinarisk, etc.) eller en personlig minnesvandring. Levererar JSON som öppnas i tour-app.html.
---
```

### Body-innehåll (krav)

Body ska instruera AI:n att:

1. **Klargöra input** om användaren inte gett det:
   - Stad och eventuellt stadsdel.
   - Tema/fokus (litteratur, kallt krig, mat, art deco, etc.) — *uppmuntra ett specifikt tema*, inte "allmän sightseeing".
   - Längd i minuter (default 90).
   - Språk för narratives (default användarens språk).
   - Startpunkt eller om AI:n får välja.
   - Fysisk förmåga (default "easy", påverkar trappor/branta backar).

2. **Researcha** — använd sökverktyg om tillgängliga, lita inte på minnet för exakta koordinater eller URL:er. Föredra Wikipedia, lokala turistförbund, kulturhistoriska sajter.

3. **Planera rutten geografiskt** — waypoints i logisk promenadordning, helst loop eller linje som slutar nära kollektivtrafik. Undvik back-tracking. Total sträcka 3–5 km för 90-minuters tur.

4. **Skriva waypoint-narratives** — konversationella, 60–120 sekunders uppläsning per stopp (cirka 150–280 ord), anekdoter framför fakta-uppräkning, små lokala fraser där det passar.

5. **Använda rätt JSON-schema** — fält enligt `references/tour-schema.json`. Aldrig hitta på URL:er; använd Wikipedia article slugs och search queries istället. Trigger-radie ska bedömas per plats (stort torg: 60 m, specifik bänk: 15 m, kyrka: 40 m).

6. **Validera** — kontrollera att JSON-utdata är giltig mot schemat innan leverans. Räkna waypoints, totalsträcka och uppskattad tid.

7. **Leverera** — som JSON-fil (eller code block beroende på runtime) med filnamn `tour-{city}-{theme}-{duration}min.json`.

Body ska också inkludera en kort sektion **"Tänk så här om mindre uppenbara saker"** med:
- Hur man skriver bra övergångar (`walk_to_next.directions_hint` ska ge ett *minne* av riktning, inte turn-by-turn).
- Hur man hanterar stängda/borttagna platser.
- Hur man undviker generisk "år 1503 byggdes denna kyrka"-text.

### `references/`

- `tour-schema.json` — fullständigt JSON Schema, validerbart, med beskrivningar per fält.
- `waypoint-guide.md` — 1–2 sidor om vad som skiljer en stark narrative från en svag. Inkludera 2–3 exempel sida vid sida (svag → stark).
- `routing-tips.md` — kort guide om promenadlogik: undvik högtrafikerade vägar, ta hänsyn till trappor, slutpunkt nära T-bana/buss, hellre 8 starka stopp än 14 medioker.
- `examples/` — tre kompletta, varierade exempel som AI:n kan studera. Måste vara kvalitetshöga — exemplen är skillens "demonstrationer".

---

## 7. JSON-schema för `tour.json`

Top-level:

```json
{
  "schema_version": "1.0",
  "tour": { ... },
  "waypoints": [ ... ]
}
```

### `tour` (objekt)

| Fält | Typ | Krav | Beskrivning |
|---|---|---|---|
| `id` | string | ja | URL-säker slug, t.ex. `"lisboa-pessoa-90min"` |
| `title` | string | ja | Visningsnamn, t.ex. `"Pessoas Lissabon"` |
| `city` | string | ja | T.ex. `"Lisboa"` |
| `country` | string | nej | ISO 3166-1 alpha-2, t.ex. `"PT"` |
| `language` | string | ja | BCP 47, t.ex. `"sv"` eller `"en"` |
| `theme` | string | nej | T.ex. `"Litteraturhistoria"` |
| `duration_minutes` | integer | ja | Uppskattad total tid inkl. uppläsning |
| `distance_km` | number | ja | Total promenadsträcka |
| `difficulty` | enum | ja | `"easy" \| "moderate" \| "demanding"` |
| `intro_narrative` | string | nej | Läses upp/visas innan första waypoint |
| `outro_narrative` | string | nej | Läses upp/visas efter sista waypoint |
| `start_coordinates` | `[lat, lng]` | ja | För att zooma kartan |
| `map_bounds` | `[[s,w],[n,e]]` | nej | Initial viewport |
| `attribution` | string | nej | Källor som AI:n använt |
| `created_at` | ISO 8601 string | nej | När JSON:en skapades |

### `waypoints` (array, minst 3 objekt)

Per waypoint:

| Fält | Typ | Krav | Beskrivning |
|---|---|---|---|
| `id` | string | ja | T.ex. `"wp-01"` |
| `order` | integer | ja | 1-indexerad, måste vara unik och stigande |
| `title` | string | ja | T.ex. `"Café A Brasileira"` |
| `coordinates` | `[lat, lng]` | ja | WGS84 |
| `trigger_radius_m` | integer | ja | 15–80, default 30 |
| `short` | string | ja | 1 mening för listvy och kort-preview |
| `narrative` | string | ja | Huvudtexten som läses upp |
| `narrative_seconds_estimate` | integer | nej | Uppskattad uppläsningslängd |
| `images` | array | nej | Se nedan |
| `links` | array | nej | Se nedan |
| `trivia` | array of string | nej | Extra fakta, visas som lista |
| `walk_to_next` | objekt | nej | Se nedan |
| `accessibility_notes` | string | nej | T.ex. "trappor, ej rullstol" |
| `optional` | boolean | nej | Om `true`: punkten är "om du har tid" |

#### `images[]` per waypoint

```json
{ "source": "wikipedia", "article": "A_Brasileira", "lang": "en" }
{ "source": "wikipedia", "article": "A_Brasileira", "lang": "pt", "thumb_only": true }
{ "source": "search_query", "query": "Café A Brasileira Pessoa statue Lisbon" }
{ "source": "local", "path": "wp-01-photo.jpg" }
```

- `wikipedia` — appen anropar `https://{lang}.wikipedia.org/api/rest_v1/page/summary/{article}`. Default `lang` = `tour.language`, fallback `en`.
- `search_query` — renderas som klickbar knapp "Visa bilder" som öppnar Google Images sökning i ny flik.
- `local` — relativ sökväg, kräver att användaren droppat en bildmapp tillsammans med JSON.

#### `links[]` per waypoint

```json
{ "label": "Wikipedia om caféet", "url": "https://en.wikipedia.org/wiki/A_Brasileira" }
```

`url` måste vara `https://`. Appen verifierar tillgänglighet vid första laddning (HEAD eller no-cors GET) och döljer länkar som verkar trasiga.

#### `walk_to_next`

```json
{
  "distance_m": 320,
  "estimated_minutes": 5,
  "directions_hint": "Gå nedför Rua Garrett mot floden."
}
```

`directions_hint` är *flavor text*, inte turn-by-turn. Faktisk navigering sker via Google Maps deep-link.

### Validering

Appen ska göra basal validering vid import:

- `schema_version` finns och stöds.
- `waypoints.length >= 3`.
- Alla koordinater inom giltigt lat/lng-intervall.
- `order` är 1-indexerad och konsekutiv.
- Alla obligatoriska fält finns.

Vid valideringsfel: visa felmeddelande med specifik path (`waypoints[3].coordinates`), erbjud "Kopiera felmeddelandet" så användaren kan klistra in i sin AI och be om en korrigerad fil.

---

## 8. Ett minimalt exempel (tre waypoints)

```json
{
  "schema_version": "1.0",
  "tour": {
    "id": "lisboa-pessoa-mini",
    "title": "Pessoas Lissabon — mini",
    "city": "Lisboa",
    "country": "PT",
    "language": "sv",
    "theme": "Litteraturhistoria",
    "duration_minutes": 30,
    "distance_km": 1.1,
    "difficulty": "easy",
    "start_coordinates": [38.7108, -9.1431],
    "intro_narrative": "Fernando Pessoa levde nästan hela sitt liv inom en kvadratkilometer i Lissabon...",
    "outro_narrative": "Vi avslutar där vi började — i Pessoas stad."
  },
  "waypoints": [
    {
      "id": "wp-01",
      "order": 1,
      "title": "Café A Brasileira",
      "coordinates": [38.7108, -9.1431],
      "trigger_radius_m": 25,
      "short": "Pessoas dagliga café — brons-statyn sitter där ute.",
      "narrative": "Här satt Fernando Pessoa nästan varje dag mellan 1905 och 1935. Beställ en *bica*...",
      "images": [
        { "source": "wikipedia", "article": "A_Brasileira", "lang": "en" }
      ],
      "links": [
        { "label": "Wikipedia om caféet", "url": "https://en.wikipedia.org/wiki/A_Brasileira" }
      ],
      "walk_to_next": {
        "distance_m": 450,
        "estimated_minutes": 7,
        "directions_hint": "Gå nedför Rua Garrett mot Praça do Comércio."
      }
    },
    {
      "id": "wp-02",
      "order": 2,
      "title": "Casa Fernando Pessoa",
      "coordinates": [38.7160, -9.1620],
      "trigger_radius_m": 20,
      "short": "Huset där Pessoa bodde sina sista 15 år.",
      "narrative": "I huset på Rua Coelho da Rocha 16 bodde Pessoa från 1920 till sin död 1935...",
      "images": [
        { "source": "search_query", "query": "Casa Fernando Pessoa Lisboa" }
      ],
      "walk_to_next": {
        "distance_m": 660,
        "estimated_minutes": 9,
        "directions_hint": "Tillbaka mot Príncipe Real."
      }
    },
    {
      "id": "wp-03",
      "order": 3,
      "title": "Cemitério dos Prazeres",
      "coordinates": [38.7195, -9.1745],
      "trigger_radius_m": 40,
      "short": "Pessoas första gravplats — han flyttades senare till Jerónimos.",
      "narrative": "På Prazeres-kyrkogården vilade Pessoa från 1935 till 1985..."
    }
  ]
}
```

---

## 9. Appens vyer och UI-flöden

Appen har fyra primära vyer:

### 9.1 Startvyn (ingen tur laddad)

- Stort drag-and-drop-område: "Släpp en `tour.json` här, eller klicka för att välja".
- Lista över sparade turer (från `localStorage`), klickbara för att återöppna.
- Knapp "Hjälp / Hur skapar jag en tur?" som expanderar instruktioner inkl. var skillen finns.
- Knapp "Inställningar" för BYOK och språk.

### 9.2 Översiktsvyn (tur laddad, inte påbörjad)

- Header: turens titel, stad, längd, sträcka, svårighet.
- Karta (60 % höjd): alla waypoints som numrerade pins, polyline som drar promenadrutten.
- Lista under kartan: numrerad lista över waypoints, klickbar för att förhandsläsa.
- Primärknapp: **"Starta tur från första punkten"**.
- Sekundärknappar: **"Free-roam"**, **"Hoppa till valfri punkt"**.
- "Intro" expanderbart kort som visar/läser upp `tour.intro_narrative`.

### 9.3 Aktiv tur

- Top bar: "Stopp 3 av 8 — Casa Fernando Pessoa", progress-stapel.
- Live-distans: "192 m kvar" (uppdateras varje 5 s vid GPS-fix).
- Kompasspil mot nästa waypoint (om enhetens orientation-API är tillgängligt) — annars textriktning.
- Karta (medelstor): användarens position som blå prick, nästa waypoint highlightad, övriga punkter dämpade.
- Knappar: **"Navigera i Google Maps"** (deep-link), **"Jag är framme"** (manuell trigger om GPS bråkar), **"Hoppa över"**, **"Pausa tur"**.
- Nederst: minimerat kort med pågående waypoints titel och `short`.

När triggerradien nås:

- Vibrera (Vibration API om tillgängligt).
- Expandera waypoint-kortet till full skärm: bilder överst, titel, narrative-text, ev. trivia, länkar.
- Auto-spela TTS om aktiverat. Visuell indikator att uppläsning pågår, paus/play-knapp.
- Längst ner: **"Klar — gå vidare till nästa stopp"** + anteckningsfält.

### 9.4 Sammanfattningsvyn

- Visas efter sista waypoint (eller när användaren trycker "Avsluta tur").
- Outro-narrative.
- Lista: antal punkter besökta, total sträcka, total tid (clock-time, inte estimat).
- Anteckningar samlade per waypoint.
- Knappar: **"Exportera som markdown"**, **"Dela JSON-fil"**, **"Starta om turen"**, **"Tillbaka till startvyn"**.

### 9.5 Inställningsvyn

- Språk för UI (sv/en/etc).
- BYOK:
  - TTS-provider: `Ingen (Web Speech)`, `OpenAI`, `ElevenLabs`. Anthropic kan adderas senare när TTS-API:t mognar.
  - API-nyckel (lösenordsfält). Sparas i `localStorage`. Varning visas: "Nyckeln lagras lokalt i din webbläsare. Använd en separat nyckel med utgiftsgräns."
  - Röst-val (provider-specifik dropdown).
  - Förgenerera kommande waypoints (default på).
- Trigger-radie-multiplikator (1.0× default, kan ökas till 1.5× eller 2× om GPS är dålig).
- Vibrera vid trigger (default på).
- Wake Lock under aktiv tur (default på).
- "Rensa alla turer och inställningar".

---

## 10. Geolocation

- Använd `navigator.geolocation.watchPosition` med `enableHighAccuracy: true`, `maximumAge: 5000`, `timeout: 15000`.
- Spara senaste position i minne (inte localStorage, för privacy).
- Distansberäkning: Haversine-formel (skriv inline; ingen extern dependency).
- Trigger-logik per waypoint:
  - Aktiv waypoint = nästa i `order` som inte är markerad besökt.
  - Om `distance(user, waypoint) <= waypoint.trigger_radius_m * settings.radius_multiplier`: trigger.
  - Vid trigger, markera waypoint som *arrived*, men inte automatiskt *completed* — användaren bekräftar.
- Hantera `PositionError`:
  - `PERMISSION_DENIED`: visa banner "Geolocation nekat — du kan fortfarande använda manuella 'Jag är framme'-knappar".
  - `POSITION_UNAVAILABLE`: visa "GPS hittar dig inte — vänta eller använd manuell trigger".
  - `TIMEOUT`: tyst, försök igen.
- Visa GPS-osäkerhet (från `position.coords.accuracy`) som diskret indikator. Om accuracy > 50 m: föreslå manuellt läge.

---

## 11. Karta

- Leaflet, OSM-tiles.
- Waypoint-markörer: cirkel med nummer. Färgkodning: grå (ej besökt), blå (aktiv), grön (besökt), gul (valfri).
- Polyline mellan waypoints i `order`-ordning, semitransparent.
- Användarens position: blå prick med accuracy-cirkel.
- Tap på markör: visa popup med `short`, knapp "Öppna kort".
- Auto-fit till `tour.map_bounds` vid laddning, annars beräkna från waypoints.
- Tile-attribution synlig (krav från OSM).

---

## 12. Google Maps deep-link

Format för walking-navigation till specifik waypoint:

```
https://www.google.com/maps/dir/?api=1&destination={lat},{lng}&travelmode=walking
```

Inget origin anges — Google Maps använder enhetens position. På iOS öppnar systemet Maps-appen om installerad, annars Safari → maps.google.com. På Android: Maps-appen direkt.

Knappen "Navigera i Google Maps" finns på:

- Aktiv tur-vyn (riktning till nästa waypoint).
- Översiktsvyn när en waypoint är expanderad.

Eventuellt addera "Öppna i Apple Maps":

```
maps://maps.apple.com/?daddr={lat},{lng}&dirflg=w
```

renderas bara på Apple-enheter (UA-sniff är ok här).

---

## 13. BYOK — TTS

Två providers stöds i v1:

### OpenAI TTS

```
POST https://api.openai.com/v1/audio/speech
Authorization: Bearer {API_KEY}
{
  "model": "tts-1",
  "voice": "alloy",
  "input": "Här satt Fernando Pessoa..."
}
```

Returnerar `audio/mpeg`. Cache i IndexedDB med nyckel `{tour.id}::{waypoint.id}::{voice}::{hash(text)}`.

### ElevenLabs

```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
xi-api-key: {API_KEY}
```

Samma cache-strategi.

### Pre-generering

Aktiv tur:

- När en waypoint blir aktiv (användaren går mot den), starta TTS-genereringen för *nästa* waypoint i bakgrunden om inte cachad.
- Vid trigger på aktiv waypoint, spela från cache om möjligt.
- Vid första laddning av en tur, om användaren tryckt "Pre-generera alla", bygg cache för alla waypoints sekventiellt.

### Fallback: Web Speech API

Om ingen BYOK satt, använd `speechSynthesis.speak(new SpeechSynthesisUtterance(text))`. Kvaliteten varierar per plattform och språk. Tillåtet men varna i inställningarna: "Web Speech ger varierande kvalitet; för bästa resultat lägg in en BYOK-nyckel."

### Säkerhet

- API-nycklar aldrig loggas, aldrig skickas till annan dest än respektive provider.
- TTS-anrop går från klient direkt — appen har ingen proxy.
- Visa tydligt i UI när en nyckel är inställd ("OpenAI-nyckel aktiv — radera").

---

## 14. Wikipedia-bilder

Hämtning vid render:

```
GET https://{lang}.wikipedia.org/api/rest_v1/page/summary/{article_slug}
```

Svaret innehåller `thumbnail.source` (liten) och `originalimage.source` (full). Använd `originalimage` i fullskärms-vy, `thumbnail` i listor och översikt.

CORS: Wikipedia REST API har `Access-Control-Allow-Origin: *`, fungerar direkt från browser.

Hantering vid fel:

- 404 (artikel finns inte): hoppa över, visa nästa bildkälla.
- Network error: tyst.
- Bild laddar inte: dölj `<img>`-elementet via `onerror`.

Cache: lägg respons i `localStorage` med 30-dagars TTL nyckelad på `wiki::{lang}::{slug}`.

---

## 15. Länkar

Vid första laddning av en tur, försök en `fetch(url, { method: 'HEAD', mode: 'no-cors' })` för varje länk. `no-cors` ger opaque response — om den *inte* throws, betrakta länken som "troligen ok". Tysta fel hanteras som "kanske trasig".

Renderingsregler:

- Maximalt 4 länkar per waypoint i UI:t. Om fler: visa "och 3 till" som expandering.
- Externa länkar öppnas i ny flik (`target="_blank" rel="noopener noreferrer"`).
- Trasiga länkar visas grå-stilade med ikon, men är fortfarande klickbara.

---

## 16. Persistens

### `localStorage`

| Nyckel | Innehåll |
|---|---|
| `settings` | JSON: språk, TTS-provider, voice, radius_multiplier, vibrate, wake_lock, etc. |
| `byok::openai` | API-nyckel (klartext — varning visas) |
| `byok::elevenlabs` | API-nyckel |
| `tours::index` | Array av `{ id, title, city, imported_at }` |
| `tour::{id}::data` | Hela `tour.json` |
| `tour::{id}::progress` | `{ visited: [wp-ids], started_at, last_active_at, notes: { wp-id: text } }` |
| `wiki::{lang}::{slug}` | `{ data, fetched_at }` med 30d TTL |

### IndexedDB

- Databas `tour-audio`.
- Store `clips` med nyckel `{tour_id}::{wp_id}::{voice}::{hash}` och värde `Blob`.
- Eviction: när total storlek > 100 MB, ta bort äldst använda klipp.

---

## 17. UI/UX-detaljer

- **Mobile-first layout:** allt funktionellt nåbart med tumme. Primärknappar nederst, inte topp.
- **Mörkt/ljust läge:** följ `prefers-color-scheme`.
- **Text-storlek:** minst 16px body, 14px secondary.
- **Färgpalett (default):** neutralt, kartcentriskt. Aktiv waypoint accent-färg t.ex. `#2563eb`. Besökt: grön `#16a34a`. Varning: gul `#eab308`.
- **Wake Lock:** under aktiv tur, anropa `navigator.wakeLock.request('screen')`. Hantera revoke vid visibility change och re-acquire vid visibility return.
- **Vibration:** `navigator.vibrate([100, 50, 100])` vid trigger.
- **Fokus-management:** när waypoint-kort öppnas, sätt fokus på rubriken för skärmläsare.
- **Tangentbordsstöd:** `Space` paus/play TTS, `N` nästa, `P` föregående, `Esc` stäng modaler.

---

## 18. Felhantering — kritiska scenarier

| Scenario | Beteende |
|---|---|
| Användaren laddar trasig JSON | Visa exakt fel + path. Erbjud "Kopiera felmeddelande" för paste-back till AI. |
| GPS-tillstånd nekat | Banner + manuella triggers blir enda läget. Funktionalitet bibehålls. |
| Wikipedia API ner | Tyst skip av bilder. Inga error-popups. |
| BYOK-nyckel ogiltig | Vid första TTS-anrop: snackbar "Nyckeln verkar fel — kolla inställningar". Fall tillbaka till Web Speech. |
| Användaren är offline | Detektera via `navigator.onLine`. Disabla TTS-anrop och Wikipedia-fetch. Karta funkar tills cachen tar slut. Visa banner. |
| Användaren stänger appen mitt i tur | Re-open: visa "Återuppta `{tour.title}` från stopp 4?" |
| Skärmen släcks | Wake Lock håller den på under aktiv tur (om inställning på). Annars: bara fortsätta tracka i bakgrunden så länge browser tillåter. |
| Användaren passerar trigger-radien men appen sov | Vid uppvaknande, kolla `position` mot alla framtida waypoints. Om nu *inom* radien för en kommande punkt: trigger den. |
| Användaren hoppar manuellt över en waypoint | Markera som `skipped`. Visas i sammanfattningen. |

---

## 19. Acceptanskriterier

Funktionellt:

1. Användare kan ladda ett giltigt `tour.json` via drag-and-drop *och* filväljare.
2. Användare kan starta en tur och se sin position på kartan.
3. När användaren är inom triggerradien för en waypoint, triggas waypointens kort automatiskt inom 5 sekunder.
4. Knappen "Navigera i Google Maps" öppnar Google Maps med walking-mode och rätt destination.
5. Med en giltig OpenAI-nyckel inställd, läses waypoint-narrative upp inom 2 sekunder från trigger (efter eventuell pre-generering).
6. Wikipedia-bilder för minst en testpunkt renderas korrekt.
7. Användaren kan markera en waypoint som besökt och fortsätta till nästa.
8. Vid återöppning av appen efter stängning, kan användaren återuppta en pågående tur.
9. Trasiga länkar och saknade bilder bryter aldrig UI:t.
10. Ogiltig JSON ger ett begripligt felmeddelande, inte en blank skärm.

Icke-funktionellt:

11. Appen är *en* HTML-fil. Inga externa filer förutom CDN-imports.
12. Inga byggsteg krävs för att köra appen.
13. Inga API-nycklar krävs för att starta och köra en tur (utan röst).
14. Appen är användbar på iPhone Safari och Android Chrome.
15. Appen följer `prefers-color-scheme` för mörkt/ljust läge.

Skill-paketet:

16. AI:n kan med skillen läst som kontext leverera ett giltigt `tour.json` för en testförfrågan ("90 minuter Lissabon med fokus på Pessoa") som validerar mot schemat och har minst 6 waypoints.
17. Alla tre exempel-turer i `references/examples/` validerar mot schemat.
18. Skillens `description` triggar AI:n korrekt när användaren ber om en "stadstur", "walking tour", "guidad promenad", "stadsvandring".

---

## 20. Out of scope för v1

Bygg *inte* följande i första versionen — de är listade för att Claude Code ska veta att de är medvetna val:

- Realtime voice ("prata med en lokal guide") — kan adderas i v2 när TTS-flödet är stabilt.
- Egen tile-server eller offline-tile-cache.
- Inbäddad Google Maps (med API-nyckel). Deep-link räcker.
- Turn-by-turn-navigering inom appen. Google Maps-handoff ersätter detta.
- Marketplace / publicering av turer. Användare delar JSON-filer manuellt.
- Användarkonton, sign-in, cloud sync.
- Multi-user / synkron grupp-tur ("vi går turen tillsammans"). Möjligt i v3 via WebRTC.
- AR-overlay vid waypoints.
- Översättning av befintliga turer ("översätt denna engelska tur till svenska") — användaren ber AI:n om det istället.
- Analytics och telemetri.

---

## 21. Designbeslut som låsts (varför, kort)

- **Leaflet + OSM över Google Maps Embed.** Ingen nyckel, ingen kostnad, ren single-file.
- **Google Maps deep-link för navigering.** Användaren har redan Maps installerat. Vi bygger inte om hjulet.
- **Skill levereras separat från appen.** Appen ska kunna distribueras till någon som redan har en tur-fil utan att skillen installeras.
- **JSON, inte YAML, för tur-paket.** Bredare verktygsstöd, lättare att validera, AI:er gör färre fel.
- **`order`-fält explicit.** Mer robust än att lita på array-ordning vid kopiering och redigering.
- **Wikipedia REST API före egen image-host.** Gratis, CORS-friendly, hög kvalitet.
- **OpenAI TTS först, ElevenLabs efter.** Bredare användarbas har OpenAI-nyckel.
- **Pre-generering av TTS.** Latens vid trigger förstör upplevelsen.
- **Skill `description` riktar in sig brett.** Vi vill att den triggas för "promenad i Berlin", "guided tour of Rome", "stadsvandring i Malmö" — inte bara exakta fraser.

---

## 22. Frågor som Claude Code får svara på under bygget

Dessa är *inte* fel i specen — de är medvetet öppna och vill ha Claude Codes bedömning:

- Exakt CSS-strategi: minimal vanilla, eller Pico.css från CDN för snabb baseline?
- Hur ska "free-roam"-läget visuellt skilja sig från aktiv tur? Färg eller distinkt UI-state?
- Default voice för OpenAI TTS — `alloy`, `nova`, eller `shimmer`? Skapa ett snabbt A/B-test i UI.
- Hur stor borde IndexedDB-cachen vara innan eviction? 100 MB är en gissning.
- Ska sammanfattningen-vyn också erbjuda export som GPX (för att importera till andra friluftsappar)?

---

## 23. README.md (för slutanvändaren)

Generera också en `README.md` som ligger bredvid leveransfilerna. Den ska kort förklara:

1. Vad detta är.
2. Hur man installerar skillen i Claude/Codex.
3. Hur man ber AI:n om en tur.
4. Hur man öppnar appen och importerar JSON.
5. Hur man (frivilligt) lägger in en API-nyckel.
6. Kända begränsningar.

Hålls under 200 rader.
