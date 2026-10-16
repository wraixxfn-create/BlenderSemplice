"""Impostazioni sicure e compatte del componente aggiuntivo."""

from __future__ import annotations

LINGUA_PREDEFINITA = "it_IT"


def imposta_interfaccia_italiana(bpy_module: object) -> bool:
    """Imposta l'italiano nella sessione corrente senza salvare preferenze globali."""
    try:
        vista = bpy_module.context.preferences.view
        vista.language = LINGUA_PREDEFINITA
        for nome in (
            "use_translate_interface",
            "use_translate_tooltips",
            "use_translate_reports",
            "use_translate_new_dataname",
        ):
            if hasattr(vista, nome):
                setattr(vista, nome, True)
        # Non viene chiamato bpy.ops.wm.save_userpref(): la modifica non viene
        # salvata deliberatamente nelle preferenze globali dell'utente.
        return True
    except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
        return False
