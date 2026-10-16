"""Comando per inserire nella scena il modello selezionato nella libreria."""

from __future__ import annotations

import bpy

from .. import comandi
from ..blender import asset_library as servizio_libreria
from ..localization import TESTI
from ..scene import libreria
from .base import OperatoreFormaFacile


class FORMAFACILE_OT_aggiungi_asset(OperatoreFormaFacile):
    """Inserisce una raccolta di geometrie indipendenti e modificabili."""

    bl_idname = comandi.ID_AGGIUNGI_ASSET
    bl_label = TESTI["ASSET_AZIONE_AGGIUNGI"]
    bl_description = TESTI["ASSET_AIUTO_AGGIUNGI"]
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            OperatoreFormaFacile.in_modalita_oggetto(context)
            and getattr(context, "scene", None) is not None
            and getattr(context, "view_layer", None) is not None
        )

    def execute(self, context):
        scena = getattr(context, "scene", None)
        stato = getattr(scena, "formafacile", None) if scena is not None else None
        if stato is None:
            return self.errore("ERRORE_ASSET_SCENA", "LOG_ERRORE_ASSET", context)
        identificatore = str(getattr(stato, "asset_selezionato", libreria.ID_PREDEFINITO))
        try:
            istanza = servizio_libreria.crea_asset(context, identificatore, stato)
        except servizio_libreria.ErroreAsset as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        except Exception:  # noqa: BLE001 - un errore imprevisto non deve interrompere Blender
            return self.errore("ERRORE_ASSET_CREAZIONE", "LOG_ERRORE_ASSET", context)

        if len(istanza.oggetti) == 1:
            messaggio = TESTI["MESSAGGIO_ASSET_AGGIUNTO_UNO"].format(nome=istanza.nome)
        else:
            messaggio = TESTI["MESSAGGIO_ASSET_AGGIUNTO"].format(
                nome=istanza.nome,
                numero=len(istanza.oggetti),
            )
        self.annuncia(context, messaggio)
        self.report({"INFO"}, messaggio)
        return {"FINISHED"}


CLASSI = (FORMAFACILE_OT_aggiungi_asset,)
