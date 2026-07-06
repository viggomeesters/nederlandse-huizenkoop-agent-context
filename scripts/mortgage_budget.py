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


def calculate_hypotheek(payload: dict[str, Any]) -> dict[str, int | float | None]:
    h = payload.get("hypotheek_input") or {}
    explicit = payload.get("maximale_hypotheek_bankindicatie")

    if not h:
        return {
            "bron": "bankindicatie_input" if explicit is not None else "niet_opgegeven",
            "maximale_hypotheek_indicatief": round_euro(money(explicit)) if explicit is not None else 0,
            "maximale_bruto_maandlast": None,
            "gebruikte_financieringslastpercentage": None,
            "gebruikte_hypotheekrente": None,
            "looptijd_jaren": None,
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
    }


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    hypotheek = calculate_hypotheek(payload)
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

    return {
        "hypotheek": hypotheek,
        "overwaarde": {
            "bruto_overwaarde": round_euro(gross_equity),
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
        ],
    }


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.json:
        return json.loads(args.json)
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    raise SystemExit("Use --json '{...}' or --input path.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Indicatieve aankoopbudget- en hypotheekcalculator")
    parser.add_argument("--json", help="JSON input as string")
    parser.add_argument("--input", help="Path to JSON input file")
    args = parser.parse_args()
    print(json.dumps(calculate(load_payload(args)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
