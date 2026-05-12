# Routing — promenadlogik för en stadstur

## Grundprinciper

- **Hellre 8 starka stopp än 14 medioker.** Trötthet är fienden — både den fysiska och uppmärksamhetströttheten.
- **Loop eller linje, inte zigzag.** Användaren ska aldrig gå förbi samma butik två gånger.
- **Slutpunkt nära kollektivtrafik.** Tänk var personen är när turen tar slut. En tunnelbanestation eller spårvagnshållplats inom 200 m gör allt enklare.
- **Variera intensiteten.** Ett stort torg → en stilla bakgata → ett café → en kyrka. Mönstret håller uppe rytmen.

## Avstånd och tid

| Tur-längd | Total promenad | Antal stopp |
|---|---|---|
| 60 min | 2.0–2.8 km | 4–6 |
| 90 min | 3.0–4.5 km | 6–9 |
| 120 min | 4.5–6.0 km | 8–11 |
| 180 min | 6.0–9.0 km | 10–14 |

Räkna med promenadtempo **4 km/h** för `easy`, **4.5** för `moderate`, **5** för `demanding`. Lägg på 30–50 % för stopp.

## Mellan waypoints

- **Optimalt avstånd:** 200–600 m mellan stopp.
- **Under 150 m:** kombinera waypoints, eller låt den ena vara `optional`.
- **Över 800 m:** lägg in en mellan-waypoint, eller skriv en bra `directions_hint` som ger mening åt gången.

## Topografi och tillgänglighet

- För `easy`: undvik trappor, branta backar, kullerstensgator.
- Märk trappor i `accessibility_notes` även för `moderate`.
- Tänk på årstider — vissa parker stänger, vissa torg blir hala.

## Mat och paus

- En 90-min tur tjänar ofta på ett café-stopp i mitten. Det blir en naturlig vila, en del av upplevelsen, och något att skriva om.
- Lägg gärna slutet vid en plats där användaren *kan stanna* — bar, park, marknad — snarare än en hård avslutning vid en busshållplats.

## Vägval

- **Undvik** stora trafikleder, motorvägsavfarter, områden med dålig trottoar.
- **Föredra** sidogator parallellt med huvudstråk, parker, gågator.
- Om en huvudgata måste passeras: gör det vid övergångsställe och nämn det i hint.

## Trigger-radie per platstyp

**Tänk såhär:** koordinaten ligger ofta i mitten av en byggnad eller plats, men användaren är typiskt utanför entrén eller på motsatt trottoar när de "är framme". Radien måste täcka den realistiska anflygningspunkten — inte avståndet till koordinatens *exakta* punkt.

För byggnader: räkna `(byggnadens längsta halv-dimension) + 10–15 m buffert`. En 80 m × 30 m saluhall med koordinat i mitten kräver minst 50 m radie, annars triggar inte fronten på långsidan.

| Platstyp | Radie |
|---|---|
| Specifik bänk, brunn, staty | 15–20 m |
| Husfasad, dörr | 25 m |
| Café, butik, mindre museum | 25–30 m |
| Kyrka, normal byggnad | 40–50 m |
| Stor byggnad (saluhall, katedral, stort museum) | 50–70 m |
| Litet torg, gränd | 40 m |
| Stort torg | 60 m |
| Park, vy, kaj | 60–80 m |

**Tveka uppåt, inte nedåt.** För stor radie triggar några sekunder tidigare än optimalt — irriterande, men turen flyter. För liten triggar aldrig och bryter upplevelsen.

För osäker GPS (smala gator, höga byggnader): lägg på 5–10 m. Användaren kan också skala upp alla radier i appens inställningar.
