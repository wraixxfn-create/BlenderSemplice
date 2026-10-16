"""Base comune degli operatori di FormaFacile 3D.

Raccoglie le parti ripetute: ricerca degli oggetti scelti, messaggi in
italiano, scrittura del messaggio di stato e controllo della modalità.
"""

from __future__ import annotations

import bpy

from ..localization import TESTI
from ..logging_service import ottieni_logger
from ..scene import messaggi


class OperatoreFormaFacile(bpy.types.Operator):
    """Operatore con registrazione nell'annullamento di Blender."""

    bl_options = {"REGISTER", "UNDO"}

    # ------------------------------------------------------------------ aiuti

    @staticmethod
    def scelti(context) -> list:
        """Oggetti scelti nella scena corrente."""
        vettore = getattr(context, "view_layer", None)
        if vettore is None:
            return []
        return [oggetto for oggetto in vettore.objects if oggetto.select_get()]

    @staticmethod
    def oggetto_attivo(context):
        """Oggetto attivo di Blender, utile per i comandi contestuali."""
        vettore = getattr(context, "view_layer", None)
        if vettore is None:
            return None
        return vettore.objects.active

    def risolvi_oggetto(self, context, nome: str):
        """Trova un oggetto dal nome salvato nell'interfaccia."""
        if not nome:
            return None
        scena = getattr(context, "scene", None)
        if scena is not None:
            trovato = bpy.data.objects.get(nome)
            if trovato is not None:
                return trovato
        return bpy.data.objects.get(nome)

    def bersagli(self, context, nome: str = "") -> list:
        """Oggetti su cui agire: quello indicato oppure tutti gli scelti."""
        oggetto = self.risolvi_oggetto(context, nome) if nome else None
        if oggetto is not None:
            return [oggetto]
        return self.scelti(context)

    # --------------------------------------------------------------- messaggi

    def annuncia(self, context, testo: str) -> None:
        """Scrive un messaggio breve nel pannello e nella barra di stato."""
        messaggi.annuncia(context, testo)

    def errore(
        self, chiave_testo: str, chiave_log: str = "LOG_ERRORE_CREAZIONE", context=None
    ) -> set[str]:
        """Segnala un errore comprensibile, anche nel pannello, senza dettagli tecnici."""
        ottieni_logger().error(TESTI[chiave_log])
        self.report({"WARNING"}, TESTI[chiave_testo])
        if context is not None:
            self.annuncia(context, TESTI[chiave_testo])
        return {"CANCELLED"}

    @staticmethod
    def in_modalita_oggetto(context) -> bool:
        """I comandi di creazione funzionano solo in modalità Oggetto."""
        return getattr(context, "mode", "OBJECT") == "OBJECT"

    def richiedi_modalita_oggetto(self) -> set[str]:
        """Avvisa che si deve prima uscire dalla modalità Modifica."""
        self.report({"WARNING"}, TESTI["ERRORE_CREAZIONE_IN_MODIFICA"])
        return {"CANCELLED"}
