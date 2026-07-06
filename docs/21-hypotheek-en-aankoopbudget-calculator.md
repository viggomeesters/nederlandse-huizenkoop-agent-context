# Hypotheek- en aankoopbudgetcalculator

Deze repo bevat een kleine lokale calculator voor gestandaardiseerde aankoopbudget-output. De tool is bedoeld voor agentgebruik: vaste inputvariabelen erin, dezelfde rekenstappen eruit. Verkoopkosten worden standaard als aparte input meegenomen en van de overbrugging afgetrokken.

> Let op: dit is geen hypotheekadvies en geen vervanging van bankacceptatie. De calculator rekent alleen met expliciete input. Het actuele financieringslastpercentage/woonquote moet uit actuele normen, adviseur of bank komen.

## Gebruik

```bash
python3 scripts/mortgage_budget.py --input examples/doorstromer-aankoopbudget-input.json
```

Of copy-pastebaar tekstblok:

```bash
python3 scripts/mortgage_budget.py --format text --input examples/doorstromer-scenarios-targetwoning-input.json
```

Of inline:

```bash
python3 scripts/mortgage_budget.py --json '{"maximale_hypotheek_bankindicatie":540000}'
```

## Hypotheekbedrag berekenen

Als `maximale_hypotheek_bankindicatie` bekend is, gebruikt de calculator dat bedrag als leidend. `hypotheek_input` is dan alleen achtergrond en overschrijft de bankindicatie niet. Als er geen bankindicatie is, kan de tool een indicatie berekenen uit:

```json
{
  "hypotheek_input": {
    "bruto_jaarinkomen": 90000,
    "bruto_jaarinkomen_partner": 0,
    "financieringslastpercentage": 0.30,
    "hypotheekrente": 0.04,
    "looptijd_jaren": 30,
    "maandelijkse_verplichtingen": 0
  }
}
```

Berekening:

```text
maximale bruto maandlast = bruto jaarinkomen × financieringslastpercentage / 12 - maandelijkse verplichtingen
maximale hypotheek indicatief = contante waarde van die maandlast via annuïteitenformule
```

De annuïteitenformule:

```text
hoofdsom = maandlast × (1 - (1 + maandrente)^(-aantal maanden)) / maandrente
```

Bij 0% rente valt dit terug op:

```text
hoofdsom = maandlast × aantal maanden
```

## Aankoopbudget berekenen

Daarna combineert de tool hypotheekruimte met huidige woning, overbrugging en kosten:

```text
bruto_overwaarde = verwachte_verkoopprijs - resterende_hypotheek

indicatieve_overbrugging =
  verwachte_verkoopprijs × overbruggingspercentage
  - resterende_hypotheek
  - verkoopkosten

beschikbaar_voor_aankoop_en_kosten =
  maximale_hypotheek_indicatief
  + indicatieve_overbrugging
  + eigen_middelen

indicatieve_maximale_aankoopprijs =
  beschikbaar_voor_aankoop_en_kosten
  - kosten_koper
  - extra_kosten
  - gewenste_buffer_na_aankoop
```

## Waarom het financieringslastpercentage input is

Officiële maximale hypotheekberekeningen gebruiken actuele financieringslastpercentages, inkomensnormen, rente, looptijd, verplichtingen, energielabel, uitzonderingen en aanbiederbeleid. Die normen veranderen. Daarom kiest deze tool niet zelf “de juiste” woonquote, maar maakt hem expliciet als inputvariabele.

Een agent kan dus veilig zeggen:

```text
Onder aanname van 30% financieringslastpercentage en 4,0% rente komt de annuïtaire hypotheekindicatie uit op €...
```

Niet:

```text
De bank zal exact €... lenen.
```

## Standaard plek voor rente-aannames

Gebruik `data/rente-scenarios.example.json` als vaste plek voor rente-aannames. Dit is bewust geen automatische live scrape: hypotheekrentes hangen af van aanbieder, rentevaste periode, NHG, energielabel, loan-to-value/risicoklasse en productvoorwaarden.

Werk het bestand handmatig bij met actuele bron of adviseur voordat je serieus rekent. Reken daarna minimaal met drie scenario's:

```text
laag  = optimistische actuele rente
midden = normale werkhypothese
hoog = voorzichtige stress-test
```

## Doelwoning, energielabel en risicoklasse

Neem de doelwoning apart op als `target_woning`:

```json
{
  "target_woning": {
    "aankoopprijs": 600000,
    "taxatiewaarde": 600000,
    "energielabel": "A",
    "extra_leenruimte_op_basis_target": 0
  }
}
```

Waarom dit nodig is:

- energielabel of verduurzaming kan invloed hebben op extra leenruimte of rentevoorwaarden;
- de verhouding hypotheek / woningwaarde bepaalt de indicatieve loan-to-value en risicoklasse;
- overwaarde/eigen inbreng verlaagt die loan-to-value, wat bij veel aanbieders een lagere rente kan betekenen;
- een aankoopprijs boven taxatiewaarde kan extra eigen geld vragen.

De tool rapporteert daarom `loan_to_value_pct` en `risicoklasse_indicatief`, maar claimt niet automatisch welke bankkorting geldt.

## Meerdere hypotheekroutes

Gebruik `hypotheek_scenarios` voor routes zoals bestaande hypotheek meenemen, niet openbreken, wel openbreken of herfinancieren:

```json
{
  "hypotheek_scenario_key": "openbreken",
  "hypotheek_scenarios": [
    {"key": "niet_openbreken", "maximale_hypotheek_bankindicatie": 500000},
    {"key": "openbreken", "maximale_hypotheek_bankindicatie": 540000}
  ]
}
```

Zo blijft zichtbaar welke route de aankoopruimte bepaalt.

## Outputvelden

De tool geeft JSON terug met:

- `hypotheek.maximale_hypotheek_indicatief`
- `hypotheek.maximale_bruto_maandlast`
- `hypotheek_scenarios`
- `target_woning.loan_to_value_pct` wanneer `target_woning` is opgegeven
- `target_woning.risicoklasse_indicatief` wanneer `target_woning` is opgegeven
- `target_woning.energielabel` wanneer `target_woning` is opgegeven
- `overwaarde.bruto_overwaarde`
- `overwaarde.verkoopkosten_in_mindering_op_overbrugging`
- `overwaarde.indicatieve_overbrugging`
- `overwaarde.niet_direct_vrijgegeven_marge`
- `kosten.kosten_koper`
- `kosten.extra_kosten`
- `budget.beschikbaar_voor_aankoop_en_kosten`
- `budget.indicatieve_maximale_aankoopprijs`
- `waarschuwingen`

## Bronnen

- Nibud — [Hypotheek afsluiten: wat moet je weten](https://www.nibud.nl/onderwerpen/wonen/hypotheek/)
- Nibud — [Rapport Advies hypotheeknormen 2026](https://www.nibud.nl/onderzoeksrapporten/rapport-advies-hypotheeknormen-2026-2025/)
- NHG — [Prettig wonen en verantwoord lenen met NHG](https://www.nhg.nl/)
- Consumentenbond — [Overbruggingshypotheek: hoe werkt het?](https://www.consumentenbond.nl/hypotheek/doorstromer/overbruggingskrediet)
- Rijksoverheid — [Huis kopen](https://www.rijksoverheid.nl/onderwerpen/huis-kopen)
