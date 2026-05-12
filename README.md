# Stadstur

En guidad stadstur-app som du själv (eller din AI) skapar innehåll till. Du ber din AI om en tur, du får en JSON-fil, du öppnar appen, du går turen.

## Vad är det?

Två delar:

1. **`tour-app.html`** — en *enda* HTML-fil. Öppna den i din webbläsare (helst på mobil), släpp en `tour.json` på den, och gå turen. Karta, GPS-trigger, uppläsning, Google Maps-handoff.
2. **`city-tour-creator/`** — ett skill-paket som du installerar i din AI (Claude Code, Claude Desktop, Codex, m.fl.) eller klistrar in i samtalet. Den hjälper AI:n att leverera en bra tur-fil.

Inga konton, ingen backend, ingen byggprocess.

## Snabbstart för slutanvändare

### 1. Installera skillen i din AI

- **Claude Code / Claude Desktop:** lägg `city-tour-creator/`-mappen i din skills-katalog.
- **Codex / övriga:** kopiera `city-tour-creator/SKILL.md` in i samtalet som första meddelande.

### 2. Be om en tur

> Skapa en 90-minuters litterär stadstur i Lissabon på svenska med fokus på Pessoa.

AI:n ställer kanske några korta frågor och levererar sedan en `.json`-fil. Spara den.

### 3. Öppna appen

- Ladda upp `tour-app.html` till valfri statisk hosting (Cloudflare Pages, GitHub Pages, Netlify drop) **eller** öppna den direkt från din lokala disk på telefonen.
- Släpp `tour.json` i drop-zonen (eller tryck för att välja).
- Tryck **Starta tur från första punkten** när du är där.

Appen ber om GPS-tillstånd. När du går in i triggerradien för en waypoint öppnas kortet och uppläsningen startar.

### 4. (Frivilligt) Lägg in en API-nyckel för bättre röst

Appen använder webbläsarens inbyggda röst som default. Det funkar — men på vissa enheter låter det robotiskt.

Öppna **Inställningar** i appen och lägg in:

- En **OpenAI API-nyckel** (om du har en), eller
- En **ElevenLabs API-nyckel** (om du har en).

Nyckeln sparas bara i din webbläsares localStorage. Skapa gärna en separat nyckel med utgiftsgräns; uppläsning av en tur kostar typiskt några öre.

## Hur skapar jag en egen tur utan AI?

Kopiera ett av exemplen i `city-tour-creator/references/examples/` och redigera. Schema-fil finns i `city-tour-creator/references/tour-schema.json`. Du behöver minst tre waypoints och en startkoordinat.

## Privacy

- Inga analytics, ingen telemetri, ingen tracker-kod.
- All data sparas lokalt i din webbläsare (localStorage + IndexedDB).
- Wikipedia-anrop, kart-tiles och TTS-anrop går direkt från din webbläsare — vi har ingen server.
- Din API-nyckel skickas bara till respektive provider (OpenAI / ElevenLabs).

## Kända begränsningar

- Geolocation kan vara opålitlig i bergiga städer, smala gränder eller inomhus. Manuella "Jag är framme"-knappar finns alltid.
- Wikipedia-bilder kräver internet. Karta funkar tills cachen tar slut.
- Wake Lock-API:t stöds inte i alla webbläsare — skärmen kan släckas under tur. Då måste du själv väcka mobilen.
- iPhones blockerar ibland TTS-uppspelning innan användaren har klickat på något. Tryck på "Läs upp"-knappen första gången.

## Teknisk översikt

- `tour-app.html` är **en** fil. Inga byggsteg. Dependencies (Leaflet) laddas från CDN.
- Vanilla JS (ES2022). Inga frameworks.
- Karta: Leaflet + OpenStreetMap.
- Navigering ut: Google Maps deep-link, Apple Maps på iOS.
- Persistens: localStorage för turer/inställningar, IndexedDB för audio-cache (planerat).

## Licens

MIT. Använd, modifiera, dela.
