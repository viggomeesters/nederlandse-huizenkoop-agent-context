#!/usr/bin/env python3
"""Indicatieve Nederlandse aankoopbudget- en hypotheekcalculator.

Geen financieel advies. De calculator gebruikt expliciete inputvariabelen.
Voor de hypotheekindicatie rekent hij met een opgegeven financieringslastpercentage
(woonquote) en een standaard annuïteitenformule. De officiële Nibud/tabellen,
bankregels en uitzonderingen moeten buiten deze tool worden vastgesteld.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def money(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def round_euro(value: float) -> int:
    return int(round(value))


def format_euro(value: Any) -> str:
    return "€" + f"{round_euro(money(value)):,}".replace(",", ".")


def sum_bucket(bucket: Any) -> float:
    if not bucket:
        return 0.0
    if isinstance(bucket, (int, float)):
        return float(bucket)
    if not isinstance(bucket, dict):
        return 0.0
    if "totaal" in bucket:
        return money(bucket.get("totaal"))
    return sum(money(v) for v in bucket.values() if isinstance(v, (int, float)))


def annuity_principal_from_payment(monthly_payment: float, annual_interest: float, years: int) -> float:
    months = years * 12
    if months <= 0:
        raise ValueError("looptijd_jaren must be positive")
    monthly_interest = annual_interest / 12
    if monthly_interest == 0:
        return monthly_payment * months
    return monthly_payment * (1 - (1 + monthly_interest) ** (-months)) / monthly_interest


def calculate_hypotheek(payload: dict[str, Any]) -> dict[str, Any]:
    h = payload.get("hypotheek_input") or {}
    explicit = payload.get("maximale_hypotheek_bankindicatie")

    if explicit is not None:
        return {
            "bron": "bankindicatie_input",
            "maximale_hypotheek_indicatief": round_euro(money(explicit)),
            "maximale_bruto_maandlast": None,
            "gebruikte_financieringslastpercentage": None,
            "gebruikte_hypotheekrente": None,
            "looptijd_jaren": None,
            "scenario_key": payload.get("key"),
            "toelichting": payload.get("toelichting"),
        }

    if not h:
        return {
            "bron": "niet_opgegeven",
            "maximale_hypotheek_indicatief": 0,
            "maximale_bruto_maandlast": None,
            "gebruikte_financieringslastpercentage": None,
            "gebruikte_hypotheekrente": None,
            "looptijd_jaren": None,
            "scenario_key": payload.get("key"),
            "toelichting": payload.get("toelichting"),
        }

    gross_income = money(h.get("bruto_jaarinkomen")) + money(h.get("bruto_jaarinkomen_partner"))
    load_pct = money(h.get("financieringslastpercentage"))
    annual_interest = money(h.get("hypotheekrente"))
    years = int(h.get("looptijd_jaren", 30))
    monthly_obligations = money(h.get("maandelijkse_verplichtingen"))

    gross_yearly_housing_cost = gross_income * load_pct
    max_monthly_payment = max(0.0, gross_yearly_housing_cost / 12 - monthly_obligations)
    principal = annuity_principal_from_payment(max_monthly_payment, annual_interest, years)

    cap = h.get("woningwaarde_cap")
    if cap is not None:
        principal = min(principal, money(cap))

    return {
        "bron": "annuiteit_op_basis_van_input_woonquote",
        "maximale_hypotheek_indicatief": round_euro(principal),
        "maximale_bruto_maandlast": round_euro(max_monthly_payment),
        "gebruikte_financieringslastpercentage": load_pct,
        "gebruikte_hypotheekrente": annual_interest,
        "looptijd_jaren": years,
        "scenario_key": payload.get("key"),
        "toelichting": payload.get("toelichting"),
    }


def choose_hypotheek(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = payload.get("hypotheek_scenarios") or []
    if not scenarios:
        return calculate_hypotheek(payload), {}

    calculated: dict[str, Any] = {}
    for index, scenario in enumerate(scenarios):
        key = str(scenario.get("key") or f"scenario_{index + 1}")
        scenario_payload = dict(payload)
        scenario_payload.update(scenario)
        scenario_payload["key"] = key
        calculated[key] = calculate_hypotheek(scenario_payload)

    selected_key = payload.get("hypotheek_scenario_key") or next(iter(calculated))
    if selected_key not in calculated:
        raise ValueError(f"unknown hypotheek_scenario_key: {selected_key}")
    return calculated[selected_key], calculated


def risk_class(ltv: float | None) -> str | None:
    if ltv is None:
        return None
    if ltv <= 60:
        return "<=60%"
    if ltv <= 70:
        return "<=70%"
    if ltv <= 80:
        return "<=80%"
    if ltv <= 90:
        return "<=90%"
    if ltv <= 100:
        return "<=100%"
    return ">100%"


def calculate_target_woning(payload: dict[str, Any], mortgage_amount: float) -> dict[str, Any] | None:
    target = payload.get("target_woning") or {}
    if not target:
        return None
    value = money(target.get("taxatiewaarde") or target.get("marktwaarde") or target.get("aankoopprijs"))
    ltv = round(mortgage_amount / value * 100, 1) if value else None
    return {
        "aankoopprijs": round_euro(money(target.get("aankoopprijs"))) if target.get("aankoopprijs") is not None else None,
        "taxatiewaarde": round_euro(money(target.get("taxatiewaarde"))) if target.get("taxatiewaarde") is not None else None,
        "marktwaarde": round_euro(money(target.get("marktwaarde"))) if target.get("marktwaarde") is not None else None,
        "energielabel": target.get("energielabel"),
        "extra_leenruimte_op_basis_target": round_euro(money(target.get("extra_leenruimte_op_basis_target"))),
        "loan_to_value_pct": ltv,
        "risicoklasse_indicatief": risk_class(ltv),
    }


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    hypotheek, hypotheek_scenarios = choose_hypotheek(payload)
    max_mortgage = money(hypotheek["maximale_hypotheek_indicatief"])

    current_home = payload.get("huidige_woning") or {}
    sale_price = money(current_home.get("verwachte_verkoopprijs"))
    remaining_mortgage = money(current_home.get("resterende_hypotheek"))
    sale_costs = money(current_home.get("verkoopkosten"))
    bridge_pct = money(current_home.get("overbruggingspercentage"), 1.0)

    gross_equity = max(0.0, sale_price - remaining_mortgage)
    bridge = max(0.0, sale_price * bridge_pct - remaining_mortgage - sale_costs)
    unreleased_margin = max(0.0, gross_equity - bridge)

    own = payload.get("eigen_middelen") or {}
    own_funds = money(own.get("spaargeld_in_te_zetten")) + money(own.get("overige_middelen"))
    buyer_costs = sum_bucket(payload.get("kosten_koper"))
    extra_costs = sum_bucket(payload.get("extra_kosten"))
    buffer_after = money(payload.get("gewenste_buffer_na_aankoop"))

    available = max_mortgage + bridge + own_funds
    max_purchase = available - buyer_costs - extra_costs - buffer_after

    result = {
        "hypotheek": hypotheek,
        "hypotheek_scenarios": hypotheek_scenarios,
        "overwaarde": {
            "bruto_overwaarde": round_euro(gross_equity),
            "verkoopkosten_in_mindering_op_overbrugging": round_euro(sale_costs),
            "indicatieve_overbrugging": round_euro(bridge),
            "niet_direct_vrijgegeven_marge": round_euro(unreleased_margin),
        },
        "kosten": {
            "kosten_koper": round_euro(buyer_costs),
            "extra_kosten": round_euro(extra_costs),
            "gewenste_buffer_na_aankoop": round_euro(buffer_after),
        },
        "budget": {
            "beschikbaar_voor_aankoop_en_kosten": round_euro(available),
            "indicatieve_maximale_aankoopprijs": round_euro(max_purchase),
        },
        "waarschuwingen": [
            "Indicatief model: vervangt geen hypotheekadvies of bankacceptatie.",
            "Financieringslastpercentage moet uit actuele normen/adviseur komen; deze tool kiest het niet automatisch.",
            "Kosten koper en veel extra kosten komen meestal uit overwaarde/eigen middelen, niet automatisch uit extra hypotheek.",
            "Overbrugging hangt af van verkoopstatus, taxatie/verkoopprijs, bankvoorwaarden en verkoopkosten.",
            "Doelwoning, energielabel en loan-to-value kunnen rente/risicoklasse en extra leenruimte beïnvloeden; voer die expliciet in.",
        ],
    }
    target_woning = calculate_target_woning(payload, max_mortgage)
    if target_woning:
        result["target_woning"] = target_woning
    return result


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.json:
        return json.loads(args.json)
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    raise SystemExit("Use --json '{...}' or --input path.json")


def format_text_output(result: dict[str, Any]) -> str:
    hypotheek = result["hypotheek"]
    overwaarde = result["overwaarde"]
    kosten = result["kosten"]
    budget = result["budget"]
    target = result.get("target_woning") or {}

    max_after_costs = (
        budget["indicatieve_maximale_aankoopprijs"]
        + kosten.get("gewenste_buffer_na_aankoop", 0)
    )
    practical = budget["indicatieve_maximale_aankoopprijs"] - kosten.get("kosten_koper", 0)
    practical_floor = max(0, round_euro(practical / 5000) * 5000)
    practical_ceiling = max(practical_floor, practical_floor + 5000)

    scenario = hypotheek.get("scenario_key")
    scenario_line = f"Scenario: {scenario}\n" if scenario else ""
    target_line = ""
    if target:
        bits = []
        if target.get("aankoopprijs"):
            bits.append(f"doelwoning {format_euro(target['aankoopprijs'])}")
        if target.get("energielabel"):
            bits.append(f"label {target['energielabel']}")
        if target.get("loan_to_value_pct") is not None:
            bits.append(f"LTV {target['loan_to_value_pct']:.1f}% ({target.get('risicoklasse_indicatief')})")
        target_line = "Target: " + ", ".join(bits) + "\n" if bits else ""

    return f"""AANKOOPBUDGET — INDICATIEF
{scenario_line}{target_line}
Input:
- Hypotheekruimte: {format_euro(hypotheek['maximale_hypotheek_indicatief'])}
- Bruto overwaarde: {format_euro(overwaarde['bruto_overwaarde'])}
- Verkoopkosten: {format_euro(overwaarde['verkoopkosten_in_mindering_op_overbrugging'])}
- Kosten koper/aankoopkosten: {format_euro(kosten['kosten_koper'])}
- Buffer/marge: {format_euro(kosten['gewenste_buffer_na_aankoop'])}

Overbrugging:
Indicatieve overbrugging = {format_euro(overwaarde['indicatieve_overbrugging'])}
Niet direct vrijgegeven marge = {format_euro(overwaarde['niet_direct_vrijgegeven_marge'])}
Verkoopkosten gaan standaard van de overbrugging af.

Budget:
Beschikbaar aankoop + kosten = {format_euro(budget['beschikbaar_voor_aankoop_en_kosten'])}
MAX woning na aankoopkosten: {format_euro(max_after_costs)}
Veiliger plafond met buffer: {format_euro(budget['indicatieve_maximale_aankoopprijs'])}
Zoekrange: rond {format_euro(practical_floor)}–{format_euro(practical_ceiling)}

Kort:
Max is {format_euro(max_after_costs)} als alles wordt geaccepteerd. Praktisch zoeken rond {format_euro(practical_floor)}–{format_euro(practical_ceiling)} houdt ruimte voor kosten koper, verkoopkosten, bankvoorwaarden en tegenvallers.
""".strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Indicatieve aankoopbudget- en hypotheekcalculator")
    parser.add_argument("--json", help="JSON input as string")
    parser.add_argument("--input", help="Path to JSON input file")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()
    result = calculate(load_payload(args))
    if args.format == "text":
        print(format_text_output(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
