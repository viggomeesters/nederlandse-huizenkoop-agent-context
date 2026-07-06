# Aankoopbudget variabelen en outputmodel

Een hypotheekcalculator geeft meestal alleen een **maximale hypotheekindicatie**. Voor een doorstromer is dat niet hetzelfde als het bedrag dat veilig op een woning kan worden geboden. Een koper-side agent moet daarom een gestandaardiseerd budgetmodel gebruiken waarin hypotheekruimte, overbrugging, kosten koper, extra kosten en buffer apart zichtbaar blijven.

## Doel

Het doel van dit model is niet om hypotheekadvies te vervangen. Het doel is om elke budgetvraag dezelfde structuur te geven:

1. wat zegt de hypotheekcalculator of adviseur over de maximale hypotheek;
2. hoeveel overwaarde kan tijdelijk via overbrugging worden gebruikt;
3. welke aankoopkosten moeten uit overwaarde of eigen middelen komen;
4. welk bedrag blijft over als **maximale aankoopprijs / biedruimte**;
5. welke aannames moeten door hypotheekadviseur, bank, notaris of fiscalist worden bevestigd.

## Variabelen

Gebruik bij voorkeur deze namen, zodat agentoutputs vergelijkbaar blijven.

```yaml
aankoopbudget_input:
  maximale_hypotheek_bankindicatie: 0
  aankoopprijs_gewenst: null

  huidige_woning:
    verwachte_verkoopprijs: 0
    resterende_hypotheek: 0
    verkoopkosten: 0
    overbruggingspercentage: 0.95
    verkoopstatus: onbekend # niet_verkocht | verkocht_onder_voorbehoud | definitief_verkocht

  eigen_middelen:
    spaargeld_in_te_zetten: 0
    overige_middelen: 0

  kosten_koper:
    overdrachtsbelasting: 0
    notaris_levering: 0
    notaris_hypotheek: 0
    taxatie: 0
    hypotheekadvies: 0
    bouwkundige_keuring: 0
    bankgarantie: 0
    aankoopmakelaar_of_biedcoach: 0
    overige_kosten_koper: 0

  extra_kosten:
    verhuizing: 0
    directe_klus_minimum: 0
    verduurzaming_eerste_fase: 0
    inrichting: 0
    dubbele_lasten: 0
    tuin_buitenruimte: 0
    bouwkundige_onvoorzien: 0

  gewenste_buffer_na_aankoop: 0
```

## Afgeleide waarden

Gebruik deze berekeningen expliciet in de output.

```text
bruto_overwaarde = verwachte_verkoopprijs - resterende_hypotheek

indicatieve_overbrugging =
  verwachte_verkoopprijs × overbruggingspercentage
  - resterende_hypotheek
  - verkoopkosten

totaal_kosten_koper = som(kosten_koper)
totaal_extra_kosten = som(extra_kosten)

beschikbaar_voor_aankoop_en_kosten =
  maximale_hypotheek_bankindicatie
  + indicatieve_overbrugging
  + spaargeld_in_te_zetten
  + overige_middelen

maximale_aankoopprijs_indicatief =
  beschikbaar_voor_aankoop_en_kosten
  - totaal_kosten_koper
  - totaal_extra_kosten
  - gewenste_buffer_na_aankoop
```

Belangrijk: de **maximale hypotheek bankindicatie** is niet automatisch vrij besteedbaar boven de woningwaarde. De uiteindelijke hypotheek hangt af van inkomen, rente, toetsing, taxatiewaarde, voorwaarden van de bank en de concrete woning.

## Kosten koper komen vaak uit overwaarde of eigen middelen

Benoem dit altijd expliciet: `kosten_koper` zoals overdrachtsbelasting, notaris, taxatie, hypotheekadvies, bankgarantie, bouwkundige keuring en aankoopbegeleiding worden meestal niet bovenop de woningwaarde meegefinancierd in de gewone hypotheek. Ze drukken dus op:

- vrij te maken overwaarde / overbruggingsruimte;
- spaargeld of andere eigen middelen;
- de gewenste buffer na aankoop.

Een budget van bijvoorbeeld €620.000 betekent daarom niet automatisch dat de koper ook €620.000 kan bieden. Als ongeveer €20.000 nodig is voor overdracht, notaris, hypotheekadvies en andere aankoopkosten, is de praktische biedruimte eerder ongeveer €600.000 — vóór eventuele extra klussen, verhuizing of gewenste buffer.

## Gestandaardiseerde output

Gebruik deze outputvorm bij budgetvragen.

```text
Aankoopbudget — indicatief

Input:
- Maximale hypotheek bankindicatie: €...
- Verwachte verkoopprijs huidige woning: €...
- Resterende hypotheek huidige woning: €...
- Overbruggingspercentage: ...%
- Eigen middelen in te zetten: €...

Overwaarde / overbrugging:
- Bruto overwaarde: €...
- Indicatieve overbrugging: €...
- Niet direct vrijgegeven marge / onzekerheid: €...

Kosten buiten aankoopprijs:
- Kosten koper: €...
- Extra kosten: €...
- Gewenste buffer na aankoop: €...

Uitkomst:
- Beschikbaar voor aankoop + kosten: €...
- Indicatieve maximale aankoopprijs: €...
- Praktisch veilig biedplafond: €...

Let op:
- Kosten koper en veel extra kosten komen uit overwaarde/eigen middelen, niet automatisch uit extra hypotheek.
- Overbrugging is afhankelijk van bank, verkoopstatus, taxatie/verkoopprijs en verkoopkosten.
- Laat dit toetsen door hypotheekadviseur/bank voordat je zonder financieringsvoorbehoud of met krappe buffer biedt.
```

## Rekenvoorbeeld

Fictieve doorstromer:

```yaml
aankoopbudget_input:
  maximale_hypotheek_bankindicatie: 540000
  huidige_woning:
    verwachte_verkoopprijs: 450000
    resterende_hypotheek: 315000
    verkoopkosten: 0
    overbruggingspercentage: 0.95
  eigen_middelen:
    spaargeld_in_te_zetten: 0
    overige_middelen: 0
  kosten_koper:
    totaal: 20000
  extra_kosten:
    totaal: 0
  gewenste_buffer_na_aankoop: 0
```

Berekening:

```text
bruto_overwaarde = €450.000 - €315.000 = €135.000
indicatieve_overbrugging = €450.000 × 95% - €315.000 = €112.500
beschikbaar_voor_aankoop_en_kosten = €540.000 + €112.500 = €652.500
maximale_aankoopprijs_indicatief = €652.500 - €20.000 = €632.500
```

Als een koper daarnaast bewust €12.500 marge, extra kosten of buffer wil houden, wordt de praktische biedruimte ongeveer:

```text
€632.500 - €12.500 = €620.000
```

En als de totale overdracht, notaris, hypotheekadvies en andere aankoopkosten rond €20.000 liggen, geldt de nuchtere samenvatting:

```text
Indicatief totaalbudget rond €620.000 betekent: ongeveer €600.000 uitgeven aan de woning, en circa €20.000 apart houden voor kosten koper / aankoopkosten.
```

## Agent-waarschuwingen

- Verwar `bruto_overwaarde` niet met `indicatieve_overbrugging`.
- Verwar `beschikbaar_voor_aankoop_en_kosten` niet met `maximale_aankoopprijs_indicatief`.
- Maak kosten koper niet onzichtbaar door ze “wel ergens uit overwaarde” te laten komen zonder bedrag.
- Laat een hoge calculatoruitkomst niet automatisch het bod bepalen; taxatierisico, maandlasten, verkoopstatus en buffer blijven aparte checks.

## Bronnen

- Nibud — [Hypotheek afsluiten: wat moet je weten](https://www.nibud.nl/onderwerpen/wonen/hypotheek/)
- NHG — [Prettig wonen en verantwoord lenen met NHG](https://www.nhg.nl/)
- Belastingdienst — [Overdrachtsbelasting betalen bij koop huis](https://www.belastingdienst.nl/wps/wcm/connect/nl/koopwoning/content/overdrachtsbelasting-betalen-bij-koop-huis)
- Consumentenbond — [Overbruggingshypotheek: hoe werkt het?](https://www.consumentenbond.nl/hypotheek/doorstromer/overbruggingskrediet)
- Van Bruggen — [Overbruggingshypotheek: alles wat je moet weten](https://www.vanbruggen.nl/hypotheekadvies/hypotheekvormen/overbruggingshypotheek)
- Rijksoverheid — [Huis kopen](https://www.rijksoverheid.nl/onderwerpen/huis-kopen)
