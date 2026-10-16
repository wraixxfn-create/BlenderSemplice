"""Test d'integrazione da eseguire dentro Blender 4.5.x in modalità senza finestre."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "addon") not in sys.path:
    sys.path.insert(0, str(ROOT / "addon"))

import bpy
import formafacile_3d


assert bpy.app.version[:2] == (4, 5), f"Versione Blender non supportata: {bpy.app.version_string}"
bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    formafacile_3d.register()
    formafacile_3d.register()
    risultato = bpy.ops.formafacile.aggiungi_cubo()
    assert "FINISHED" in risultato, "L'operatore non ha completato l'azione."

    oggetto = bpy.context.active_object
    assert oggetto is not None, "Non è stato selezionato alcun oggetto."
    assert oggetto.type == "MESH", "L'oggetto creato non è una mesh."
    assert oggetto.name == "Cubo", "Il cubo non è stato rinominato correttamente."
    assert oggetto.data.name == "Geometria del cubo", "La geometria non è stata rinominata."
finally:
    formafacile_3d.unregister()
    formafacile_3d.unregister()

print("Test Blender superato: cubo creato, selezionato e rinominato.")
