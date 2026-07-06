# Aankoopbudget variabelen voorbeeld

> Fictief voorbeeld. Bedragen zijn indicatief en bedoeld om het outputmodel te testen, niet als financieel advies.

```yaml
aankoopbudget_input:
  maximale_hypotheek_bankindicatie: 540000
  aankoopprijs_gewenst: null

  huidige_woning:
    verwachte_verkoopprijs: 450000
    resterende_hypotheek: 315000
    verkoopkosten: 5000
    overbruggingspercentage: 0.95
    verkoopstatus: verkocht_onder_voorbehoud

  eigen_middelen:
    spaargeld_in_te_zetten: 0
    overige_middelen: 0

  kosten_koper:
    overdrachtsbelasting: 12000
    notaris_levering: 900
    notaris_hypotheek: 900
    taxatie: 800
    hypotheekadvies: 3000
    bouwkundige_keuring: 500
    bankgarantie: 500
    aankoopmakelaar_of_biedcoach: 1400
    overige_kosten_koper: 0

  extra_kosten:
    verhuizing: 0
    directe_klus_minimum: 0
    verduurzaming_eerste_fase: 0
    inrichting: 0
    dubbele_lasten: 0
    tuin_buitenruimte: 0
    bouwkundige_onvoorzien: 0

  gewenste_buffer_na_aankoop: 12500
```

Gestandaardiseerde output:

```text
Aankoopbudget — indicatief

Input:
- Maximale hypotheek bankindicatie: €540.000
- Verwachte verkoopprijs huidige woning: €450.000
- Resterende hypotheek huidige woning: €315.000
- Overbruggingspercentage: 95%
- Eigen middelen in te zetten: €0

Overwaarde / overbrugging:
- Bruto overwaarde: €135.000
- Verkoopkosten in mindering op overbrugging: €5.000
- Indicatieve overbrugging: €107.500
- Niet direct vrijgegeven marge / onzekerheid: €27.500 inclusief €5.000 verkoopkosten

Kosten buiten aankoopprijs:
- Kosten koper: circa €20.000
- Extra kosten: €0
- Gewenste buffer na aankoop: €12.500

Uitkomst:
- Beschikbaar voor aankoop + kosten: €647.500
- Indicatieve maximale aankoopprijs: €615.000
- Praktisch veilig biedplafond: circa €595.000–€600.000 als je circa €20.000 apart houdt voor overdracht, notaris, hypotheekadvies en andere aankoopkosten

Let op:
- Kosten koper en veel extra kosten komen uit overwaarde/eigen middelen, niet automatisch uit extra hypotheek.
- Overbrugging is afhankelijk van bank, verkoopstatus, taxatie/verkoopprijs en verkoopkosten.
- Laat dit toetsen door hypotheekadviseur/bank voordat je zonder financieringsvoorbehoud of met krappe buffer biedt.
```
