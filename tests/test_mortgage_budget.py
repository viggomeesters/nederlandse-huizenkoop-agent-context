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
                    "overbruggingspercentage": 0.95,
                },
                "kosten_koper": {"totaal": 20000},
                "extra_kosten": {"totaal": 0},
                "gewenste_buffer_na_aankoop": 12500,
            }
        )

        self.assertEqual(result["overwaarde"]["bruto_overwaarde"], 135000)
        self.assertEqual(result["overwaarde"]["indicatieve_overbrugging"], 112500)
        self.assertEqual(result["budget"]["beschikbaar_voor_aankoop_en_kosten"], 652500)
        self.assertEqual(result["budget"]["indicatieve_maximale_aankoopprijs"], 620000)

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


if __name__ == "__main__":
    unittest.main()
