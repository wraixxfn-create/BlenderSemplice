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

    def richiedi_selezione(self, context=None) -> set[str]:
        """Avvisa che serve una scelta, senza messaggi tecnici.

        È il messaggio che chiunque capisce: non dice "nessun oggetto attivo",
        dice cosa fare.
        """
        self.report({"WARNING"}, TESTI["ERRORE_NESSUNA_SCELTA"])
        if context is not None:
            self.annuncia(context, TESTI["ERRORE_NESSUNA_SCELTA"])
        return {"CANCELLED"}

    # ------------------------------------------------------------- contesto

    def con_attivo_salvo(self, context) -> "SalvaAttivo":
        """Restituisce un gestore che rimette a posto l'oggetto attivo.

        Durante un comando si può perdere l'oggetto attivo (per esempio
        eliminando o bloccando la scelta): chi comanda non deve ritrovarsi la
        scena cambiata oltre a quello che ha chiesto.
        """
        return SalvaAttivo(context)

    def annuncia_esito(
        self, context, esito, singolare: str, plurale: str, nome: str = "", nota: str = ""
    ) -> None:
        """Scrive il messaggio giusto per una, molte o nessuna modifica."""
        cambiati = esito.applicati
        gia_a_posto = getattr(esito, "invariati", 0)
        if cambiati == 0 and gia_a_posto:
            # Erano già nella posizione richiesta: il messaggio lo dice senza
            # far sembrare fallito il comando.
            cambiati = gia_a_posto
        if cambiati == 1 and nome:
            testo = TESTI[singolare].format(nome=nome)
        else:
            testo = TESTI[plurale].format(numero=cambiati)
        if getattr(esito, "bloccati", 0):
            testo = f"{testo} {TESTI['AVVISO_TRASFORMAZIONE_PARZIALE'].format(numero=esito.bloccati)}"
        if nota:
            testo = f"{testo} {nota}"
        self.annuncia(context, testo)


class SalvaAttivo:
    """Rimette l'oggetto attivo di prima, se esiste ancora."""

    def __init__(self, context) -> None:
        self._view_layer = getattr(context, "view_layer", None)
        self._attivo = getattr(self._view_layer, "objects", None)
        self._attivo = getattr(self._attivo, "active", None) if self._attivo else None

    def __enter__(self) -> "SalvaAttivo":
        return self

    def __exit__(self, tipo, valore, traccia) -> bool:
        if self._view_layer is None or self._attivo is None:
            return False
        try:
            if self._attivo.name and self._attivo.name in bpy.data.objects:
                if self._view_layer.objects.active is not self._attivo:
                    self._view_layer.objects.active = self._attivo
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            return False
        return False
