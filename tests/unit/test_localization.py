from __future__ import annotations

import re
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACCHETTO = ROOT / "addon" / "formafacile_3d"
if str(PACCHETTO) not in sys.path:
    sys.path.insert(0, str(PACCHETTO))

import comandi
from localization import TESTI


SEGNAPOSTO_INGLESE = re.compile(
    r"\b(?:TODO|Click here|Save|Cancel|Render|Error|Welcome)\b",
    re.IGNORECASE,
)


class TestLocalizzazioneItaliana(unittest.TestCase):
    def test_tutti_i_testi_centrali_sono_presenti(self):
        self.assertGreaterEqual(len(TESTI), 20)
        for chiave, valore in TESTI.items():
            with self.subTest(chiave=chiave):
                self.assertTrue(valore.strip(), f"Testo vuoto: {chiave}")
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(valore), f"Testo inglese non localizzato: {chiave}")

    def test_interfaccia_usa_la_risorsa_centrale(self):
        file_interfaccia = (PACCHETTO / "ui" / "panel.py").read_text(encoding="utf-8")
        file_operatore = (PACCHETTO / "operators" / "scene.py").read_text(encoding="utf-8")
        sorgenti = file_interfaccia + "\n" + file_operatore

        # Le etichette visibili sono recuperate dalla mappa italiana, non scritte
        # direttamente come stringhe nel codice dell'interfaccia.
        self.assertNotRegex(sorgenti, r"\bbl_label\s*=\s*[\"']")
        self.assertNotRegex(sorgenti, r"\bbl_description\s*=\s*[\"']")
        self.assertNotRegex(sorgenti, r"layout\.label\(\s*text\s*=\s*[\"']")
        self.assertNotRegex(sorgenti, r"layout\.operator\([^\n]*text\s*=\s*[\"']")

    def test_metadati_visibili_usano_testi_italiani(self):
        inizializzatore = (PACCHETTO / "__init__.py").read_text(encoding="utf-8")
        for campo in ("name", "author", "location", "description", "category"):
            with self.subTest(campo=campo):
                self.assertRegex(inizializzatore, rf'"{campo}"\s*:\s*TESTI\[')

        with (PACCHETTO / "blender_manifest.toml").open("rb") as manifesto:
            metadati = tomllib.load(manifesto)
        for campo in ("name", "tagline", "maintainer"):
            with self.subTest(campo=campo):
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(metadati[campo]))

    def test_tutte_le_chiavi_usate_esistono(self):
        """Nessun testo può essere richiesto con una chiave che non esiste.

        Un refuso in una chiave non si vedrebbe nei test dei pannelli senza
        Blender, ma in Blender farebbe fallire il disegno: qui si controllano
        tutti i file del progetto, compresi launcher e controlli.
        """
        chiave = re.compile(r"""TESTI\s*(?:\.get\s*)?\[\s*["']([A-Z0-9_]+)["']""")
        usate: set[str] = set()
        for cartella in (ROOT / "addon", ROOT / "scripts", ROOT / "tests"):
            for percorso in sorted(cartella.rglob("*.py")):
                if "__pycache__" in percorso.parts:
                    continue
                usate.update(chiave.findall(percorso.read_text(encoding="utf-8")))

        self.assertGreater(len(usate), 100)
        mancanti = sorted(usate - set(TESTI))
        self.assertEqual(mancanti, [], f"Chiavi di testo inesistenti: {mancanti}")

    def test_nessun_testo_dimenticato(self):
        """Ogni testo dichiarato deve essere nominato da qualche parte.

        Una chiave dichiarata e mai nominata è rimasta dopo una rinomina: o è
        codice morto o è una promessa a vuoto. Le chiavi usate indirettamente
        (tabelle dei comandi, argomenti passati per variabile) compaiono comunque
        come stringa nel sorgente, quindi basta cercarle come testo.
        """
        sorgenti = []
        for cartella in (ROOT / "addon", ROOT / "scripts", ROOT / "tests"):
            for percorso in sorted(cartella.rglob("*.py")):
                if "__pycache__" in percorso.parts:
                    continue
                sorgenti.append(percorso.read_text(encoding="utf-8"))
        for percorso in sorted((ROOT / "docs").glob("*.md")):
            sorgenti.append(percorso.read_text(encoding="utf-8"))
        tutto = "\n".join(sorgenti)

        dimenticate = [
            chiave
            for chiave in sorted(TESTI)
            if f'"{chiave}"' not in tutto and f"'{chiave}'" not in tutto
        ]
        self.assertEqual(dimenticate, [], f"Testi mai nominati: {dimenticate}")

    def test_le_tabelle_dei_comandi_puntano_a_testi_esistenti(self):
        for nome in dir(comandi):
            if not nome.startswith(("TESTI_", "AIUTI_")):
                continue
            tabella = getattr(comandi, nome)
            for chiave, valore in tabella.items():
                with self.subTest(tabella=nome, chiave=chiave):
                    self.assertIn(valore, TESTI)

    def test_documentazione_iniziale_non_contiene_segnaposto_ui_inglesi(self):
        documenti = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        for documento in documenti:
            testo = documento.read_text(encoding="utf-8")
            with self.subTest(file=documento.name):
                self.assertIsNone(SEGNAPOSTO_INGLESE.search(testo))


if __name__ == "__main__":
    unittest.main()
