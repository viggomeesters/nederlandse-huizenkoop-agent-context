# Kosten koper en extra kosten

De vraagprijs is niet de totale cashbehoefte. In Nederland kun je meestal maximaal 100% van de woningwaarde financieren; de bijkomende kosten moeten meestal uit eigen geld, overwaarde of andere middelen komen.

## Kosten koper

Onder `kosten koper` vallen typisch:

- overdrachtsbelasting;
- notariskosten voor leveringsakte;
- notariskosten voor hypotheekakte;
- taxatiekosten;
- hypotheekadvies en bemiddeling;
- Kadasterkosten;
- eventuele bankgarantiekosten;
- eventuele aankoopmakelaar of biedcoach;
- bouwkundige keuring.

Belastingdienst is bron voor overdrachtsbelasting en actuele tarieven/vrijstellingen. Controleer altijd of startersvrijstelling, laag tarief of hoog tarief van toepassing is. Let op: bij vrijstellingen en grensbedragen telt vaak de volledige woningwaarde, niet alleen jouw gevoel van “mijn deel”.

## Extra kostenmodel

Gebruik naast kosten koper een apart `{extra_kosten}` model. Dat voorkomt dat verbouwing, verhuizing en dubbele lasten verdwijnen in optimistische praat.

```text
extra_kosten:
  directe_klus_minimum: €...
  verduurzaming_eerste_fase: €...
  verhuis_en_inrichting: €...
  dubbele_lasten: €...
  tuin/buitenruimte: €...
  bouwkundige_onvoorzien: €...
  buffer_na_aankoop: €...
```

## Liquiditeit

Een woning kan op papier haalbaar zijn maar praktisch krap als al het spaargeld verdwijnt in kosten koper, verbouwing en overbrugging. Een koper-side agent moet daarom altijd uitrekenen:

```text
beschikbaar_cash + vrij_te_maken_overwaarde - kosten_koper - extra_kosten - gewenste_buffer = vrije ruimte / tekort
```

Voor doorstromers met een huidige woning: gebruik het gestandaardiseerde variabelenmodel in [`20-aankoopbudget-variabelen-outputmodel.md`](20-aankoopbudget-variabelen-outputmodel.md). Daarin staat expliciet dat kosten koper, notaris, hypotheekadvies en veel extra kosten meestal uit overwaarde of eigen middelen komen, niet automatisch uit extra hypotheek.

## Niet meefinancieren zonder check

Verbouwingskosten, inrichting en verhuisuitgaven zijn meestal geen gewone hypotheekruimte. Energiebesparende maatregelen kunnen uitzonderingen hebben, maar moeten met hypotheekadviseur/bank worden bevestigd.

## Bronnen

- NVM — [Een huis kopen: het aankoopproces in 8 stappen](https://www.nvm.nl/wonen/kopen/alles-over-kopen/)
- NVM — [Bieden op een huis](https://www.nvm.nl/wonen/kopen/bieden-op-een-huis/)
- NVM — [Huis kopen: koopovereenkomst en bedenktijd](https://www.nvm.nl/wonen/kopen/bedenktijd/)
- Vereniging Eigen Huis — [Ontbindende voorwaarden: hoe werkt het?](https://www.eigenhuis.nl/huis-kopen/bestaande-bouw/koopovereenkomst-en-andere-zaken/ontbindende-voorwaarden-dit-zijn-de-belangrijkste)
- Vereniging Eigen Huis — [Koopovereenkomst en bedenktijd](https://www.eigenhuis.nl/huis-kopen/bestaande-bouw/koopovereenkomst-en-andere-zaken/koopcontract-getekend-start-bedenktijd)
- Nibud — [Hypotheek afsluiten: wat moet je weten](https://www.nibud.nl/onderwerpen/wonen/hypotheek/)
- NHG — [Prettig wonen en verantwoord lenen met NHG](https://www.nhg.nl/)
- Kadaster — [Eigendomsinformatie](https://www.kadaster.nl/producten/woning/eigendomsinformatie)
- Belastingdienst — [Overdrachtsbelasting betalen bij koop huis](https://www.belastingdienst.nl/wps/wcm/connect/nl/koopwoning/content/overdrachtsbelasting-betalen-bij-koop-huis)
- Rijksoverheid — [Huis kopen](https://www.rijksoverheid.nl/onderwerpen/huis-kopen)
