import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mortgage_budget.py"


class MortgageBudgetCalculatorTest(unittest.TestCase):
    def run_calc(self, payload):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", json.dumps(payload)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_doorstromer_budget_with_given_hypotheek_indicatie(self):
        result = self.run_calc(
            {
                "maximale_hypotheek_bankindicatie": 540000,
                "huidige_woning": {
                    "verwachte_verkoopprijs": 450000,
                    "resterende_hypotheek": 315000,
                    "verkoopkosten": 5000,
                    "overbruggingspercentage": 0.95,
                },
                "kosten_koper": {"totaal": 20000},
                "extra_kosten": {"totaal": 0},
                "gewenste_buffer_na_aankoop": 12500,
            }
        )

        self.assertEqual(result["overwaarde"]["bruto_overwaarde"], 135000)
        self.assertEqual(result["overwaarde"]["verkoopkosten_in_mindering_op_overbrugging"], 5000)
        self.assertEqual(result["overwaarde"]["indicatieve_overbrugging"], 107500)
        self.assertEqual(result["budget"]["beschikbaar_voor_aankoop_en_kosten"], 647500)
        self.assertEqual(result["budget"]["indicatieve_maximale_aankoopprijs"], 615000)

    def test_hypotheek_indicatie_from_income_monthly_capacity_annuity(self):
        result = self.run_calc(
            {
                "hypotheek_input": {
                    "bruto_jaarinkomen": 90000,
                    "financieringslastpercentage": 0.30,
                    "hypotheekrente": 0.04,
                    "looptijd_jaren": 30,
                }
            }
        )

        self.assertEqual(result["hypotheek"]["maximale_bruto_maandlast"], 2250)
        self.assertGreaterEqual(result["hypotheek"]["maximale_hypotheek_indicatief"], 471000)
        self.assertLessEqual(result["hypotheek"]["maximale_hypotheek_indicatief"], 472000)

    def test_explicit_bank_indication_wins_over_income_estimate(self):
        result = self.run_calc(
            {
                "maximale_hypotheek_bankindicatie": 540000,
                "hypotheek_input": {
                    "bruto_jaarinkomen": 90000,
                    "financieringslastpercentage": 0.30,
                    "hypotheekrente": 0.04,
                    "looptijd_jaren": 30,
                },
            }
        )

        self.assertEqual(result["hypotheek"]["bron"], "bankindicatie_input")
        self.assertEqual(result["hypotheek"]["maximale_hypotheek_indicatief"], 540000)

    def test_scenario_inputs_and_target_house_ltv_are_reported(self):
        result = self.run_calc(
            {
                "hypotheek_scenario_key": "openbreken",
                "hypotheek_scenarios": [
                    {"key": "niet_openbreken", "maximale_hypotheek_bankindicatie": 500000},
                    {"key": "openbreken", "maximale_hypotheek_bankindicatie": 540000},
                ],
                "target_woning": {
                    "aankoopprijs": 600000,
                    "taxatiewaarde": 600000,
                    "energielabel": "A",
                    "extra_leenruimte_op_basis_target": 10000,
                },
                "huidige_woning": {
                    "verwachte_verkoopprijs": 450000,
                    "resterende_hypotheek": 315000,
                    "verkoopkosten": 5000,
                    "overbruggingspercentage": 0.95,
                },
                "kosten_koper": {"totaal": 20000},
                "gewenste_buffer_na_aankoop": 12500,
            }
        )

        self.assertEqual(result["hypotheek"]["scenario_key"], "openbreken")
        self.assertEqual(result["hypotheek_scenarios"]["niet_openbreken"]["maximale_hypotheek_indicatief"], 500000)
        self.assertEqual(result["target_woning"]["energielabel"], "A")
        self.assertEqual(result["target_woning"]["loan_to_value_pct"], 90.0)
        self.assertEqual(result["target_woning"]["risicoklasse_indicatief"], "<=90%")
        self.assertEqual(result["target_woning"]["extra_leenruimte_op_basis_target"], 10000)

    def test_text_output_is_compact_copy_pasteable(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--format", "text", "--input", "examples/doorstromer-scenarios-targetwoning-input.json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("AANKOOPBUDGET — INDICATIEF", proc.stdout)
        self.assertIn("MAX woning na aankoopkosten: €627.500", proc.stdout)
        self.assertIn("Zoekrange: rond €595.000–€600.000", proc.stdout)
        self.assertIn("Verkoopkosten gaan standaard van de overbrugging af", proc.stdout)
        self.assertLess(len(proc.stdout), 1400)


if __name__ == "__main__":
    unittest.main()
