from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
PACCHETTO = ROOT / "addon" / "formafacile_3d"
if str(PACCHETTO) not in sys.path:
    sys.path.insert(0, str(PACCHETTO))

from configuration import imposta_interfaccia_italiana


class TestLinguaPredefinita(unittest.TestCase):
    def test_imposta_italiano_nella_sessione(self):
        lingua = SimpleNamespace(identifier="it_IT")
        vista = SimpleNamespace(
            bl_rna=SimpleNamespace(
                properties={"language": SimpleNamespace(enum_items=[lingua])}
            ),
            language="en_US",
            use_translate_interface=False,
            use_translate_tooltips=False,
            use_translate_reports=False,
            use_translate_new_dataname=False,
        )
        bpy_finto = SimpleNamespace(
            context=SimpleNamespace(preferences=SimpleNamespace(view=vista))
        )

        self.assertTrue(imposta_interfaccia_italiana(bpy_finto))
        self.assertEqual(vista.language, "it_IT")
        self.assertTrue(vista.use_translate_interface)
        self.assertTrue(vista.use_translate_tooltips)
        self.assertTrue(vista.use_translate_reports)
        self.assertTrue(vista.use_translate_new_dataname)

    def test_gestisce_preferenze_non_disponibili(self):
        bpy_finto = SimpleNamespace(
            context=SimpleNamespace(preferences=SimpleNamespace())
        )

        self.assertFalse(imposta_interfaccia_italiana(bpy_finto))


if __name__ == "__main__":
    unittest.main()
