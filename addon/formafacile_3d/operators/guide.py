"""Guida passo passo: comandi che eseguono i passi di una guida.

I passi non contengono comandi nuovi: richiamano gli **stessi** comandi dei
pulsanti del pannello, con gli stessi parametri, presi dalla tabella centrale
`comandi.py` e dai testi di `localization.py`. Una guida, quindi, non può
promettere una funzione che il programma non ha.

Se un passo non riesce (un oggetto rinominato o bloccato, un comando che
Blender rifiuta), la guida si ferma su quel passo e lo dice: un passo non
riuscito non passa mai per riuscito, e la scena resta com'era.
"""

from __future__ import annotations

import bpy

from .. import comandi, configuration
from ..blender import selezione
from ..localization import TESTI
from ..scene import guide
from ..scene.stato import guida_della_scena, stato_della_scena
from .base import OperatoreFormaFacile


def _esegui_comando(idname: str, parametri: dict) -> set[str]:
    """Esegue un comando di FormaFacile come se fosse stato premuto nel pannello."""
    modulo, _, nome = str(idname).partition(".")
    gruppo = getattr(bpy.ops, modulo, None)
    operatore = getattr(gruppo, nome, None) if gruppo is not None else None
    if operatore is None:
        return set()
    try:
        return set(operatore(**parametri))
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return set()


def _valore(valore: object) -> object:
    """Valore di un parametro: i testi si risolvono nella mappa centrale."""
    if isinstance(valore, guide.Testo):
        return TESTI[valore.chiave]
    return valore


def _parametri(azione: guide.Azione) -> dict:
    return {chiave: _valore(valore) for chiave, valore in azione.parametri}


def _voci_guida():
    """Voci dei comandi di avanzamento della guida, con i testi italiani.

    Si costruiscono qui e non dentro l'annotazione della proprietà: Blender
    rilegge le annotazioni quando registra la classe.
    """
    return tuple(
        (modo, TESTI[comandi.TESTI_GUIDA[modo]], TESTI["AIUTO_GUIDA_AVANTI"])
        for modo in comandi.MODI_GUIDA
    )


class _OperatoreGuida(OperatoreFormaFacile):
    """Base della guida: legge e scrive lo stato della guida nella scena."""

    @classmethod
    def poll(cls, context):
        return getattr(context, "scene", None) is not None

    def avviso(self, context, testo: str, chiave_log: str = "LOG_ERRORE_GUIDA") -> set[str]:
        """Ferma la guida spiegando che cosa è successo, senza dettagli tecnici."""
        from ..logging_service import ottieni_logger

        ottieni_logger().warning(TESTI[chiave_log])
        self.report({"WARNING"}, testo)
        self.annuncia(context, testo)
        return {"CANCELLED"}

    def corrente(self, context):
        """Chiave della guida in corso e guida vera, oppure `None`."""
        chiave, _passo = guida_della_scena(getattr(context, "scene", None))
        return chiave, guide.guida(chiave)


class FORMAFACILE_OT_guida_apri(_OperatoreGuida):
    """Apre una guida passo passo, partendo dal primo passo."""

    bl_idname = comandi.ID_GUIDA_APRI
    bl_label = TESTI["AZIONE_GUIDA_INIZIA"]
    bl_description = TESTI["AIUTO_GUIDA_INIZIA"]

    guida: bpy.props.StringProperty(default=configuration.GUIDA_PRINCIPALE, options={"HIDDEN"})

    def execute(self, context):
        stato = stato_della_scena(getattr(context, "scene", None))
        scelta = guide.guida(self.guida)
        if stato is None or scelta is None:
            return self.avviso(context, TESTI["ERRORE_GUIDA_ASSENTE"])
        if not scelta.passi:
            return self.avviso(context, TESTI["ERRORE_GUIDA_ASSENTE"])
        stato.guida = scelta.chiave
        stato.passo_guida = 0
        testo = TESTI["MESSAGGIO_GUIDA_INIZIO"].format(totale=len(scelta.passi))
        self.annuncia(context, testo)
        self.report({"INFO"}, testo)
        return {"FINISHED"}


class FORMAFACILE_OT_guida_esegui(_OperatoreGuida):
    """Esegue il passo mostrato, con i comandi normali."""

    bl_idname = comandi.ID_GUIDA_ESEGUI
    bl_label = TESTI["AZIONE_GUIDA_ESEGUI"]
    bl_description = TESTI["AIUTO_GUIDA_ESEGUI"]

    def execute(self, context):
        stato = stato_della_scena(getattr(context, "scene", None))
        chiave, scelta = self.corrente(context)
        if stato is None or scelta is None:
            return self.avviso(context, TESTI["ERRORE_GUIDA_ASSENTE"])

        totale = len(scelta.passi)
        # Il passo mostrato resta dentro l'elenco dei passi, ma "guida finita"
        # si legge dal valore vero: altrimenti l'ultimo passo si ripeterebbe.
        if guide.completata(getattr(stato, "passo_guida", 0), totale):
            return self.avviso(context, TESTI["ERRORE_GUIDA_FINITA"])
        indice = guide.indice_valido(getattr(stato, "passo_guida", 0), totale - 1)
        passo = guide.passo_corrente(chiave, indice)
        if passo is None:
            return self.avviso(context, TESTI["ERRORE_GUIDA_ASSENTE"])

        if not self._prepara(context, stato, passo):
            return {"CANCELLED"}
        if not self._esegui(context, passo):
            return self.avviso(context, TESTI["ERRORE_GUIDA_PASSO"])

        stato.passo_guida = guide.prossimo_indice(indice, totale, comandi.MODO_GUIDA_AVANTI)
        if guide.completata(stato.passo_guida, totale):
            testo = TESTI["MESSAGGIO_GUIDA_FINE"]
        else:
            testo = TESTI["MESSAGGIO_GUIDA_PASSO_FATTO"].format(
                numero=stato.passo_guida + 1, totale=totale
            )
        self.annuncia(context, testo)
        self.report({"INFO"}, testo)
        return {"FINISHED"}

    def _prepara(self, context, stato, passo: guide.Passo) -> bool:
        """Prepara i valori della scena e la scelta richiesti dal passo."""
        for campo, valore in passo.impostazioni:
            numero = float(valore)  # type: ignore[arg-type]
            if campo == guide.STATO_GRANDEZZA_FORMA:
                stato.grandezza_forma = min(
                    max(numero, configuration.DIMENSIONE_FORMA_MINIMA),
                    configuration.DIMENSIONE_FORMA_MASSIMA,
                )
            elif campo == guide.STATO_PASSO:
                stato.passo = min(
                    max(numero, configuration.PASSO_MINIMO), configuration.PASSO_MASSIMO
                )
        if not passo.selezione:
            return True
        return self._scegli(context, tuple(TESTI[testo.chiave] for testo in passo.selezione))

    def _scegli(self, context, nomi: tuple[str, ...]) -> bool:
        """Sceglie gli oggetti del passo, come farebbe l'utente nell'elenco.

        Un oggetto che non c'è più (rinominato o eliminato) o bloccato ferma il
        passo con una spiegazione: la guida non deve lavorare su qualcosa che
        l'utente non ha scelto.
        """
        vettore = getattr(context, "view_layer", None)
        if vettore is None:
            return False
        oggetti = []
        for nome in nomi:
            oggetto = bpy.data.objects.get(nome)
            if oggetto is None:
                self.avviso(context, TESTI["ERRORE_GUIDA_SELEZIONE"].format(nome=nome))
                return False
            if selezione.bloccato(oggetto):
                self.avviso(context, TESTI["ERRORE_GUIDA_BLOCCATO"].format(nome=nome))
                return False
            oggetti.append(oggetto)
        try:
            for altro in vettore.objects:
                if altro.select_get():
                    altro.select_set(False)
            for oggetto in oggetti:
                oggetto.select_set(True)
            vettore.objects.active = oggetti[0]
        except (AttributeError, ReferenceError, RuntimeError):
            return False
        return True

    def _esegui(self, context, passo: guide.Passo) -> bool:
        """Esegue i comandi del passo; si ferma al primo che non riesce."""
        for azione in passo.azioni:
            esito = _esegui_comando(azione.comando, _parametri(azione))
            if "FINISHED" not in esito:
                return False
        return True


class FORMAFACILE_OT_guida_naviga(_OperatoreGuida):
    """Avanza, torna indietro o chiude la guida aperta."""

    bl_idname = comandi.ID_GUIDA_NAVIGA
    bl_label = TESTI["AZIONE_GUIDA_AVANTI"]
    bl_description = TESTI["AIUTO_GUIDA_AVANTI"]

    modo: bpy.props.EnumProperty(
        name=TESTI["ETICHETTA_GUIDA_PASSO"],
        description=TESTI["AIUTO_GUIDA_AVANTI"],
        items=_voci_guida(),
        default=comandi.MODO_GUIDA_AVANTI,
        options={"HIDDEN"},
    )

    def execute(self, context):
        stato = stato_della_scena(getattr(context, "scene", None))
        _chiave, scelta = self.corrente(context)
        if stato is None or scelta is None:
            return self.avviso(context, TESTI["ERRORE_GUIDA_ASSENTE"])

        if self.modo == comandi.MODO_GUIDA_CHIUDI:
            stato.guida = ""
            stato.passo_guida = 0
            self.annuncia(context, TESTI["MESSAGGIO_GUIDA_CHIUSA"])
            return {"FINISHED"}

        totale = len(scelta.passi)
        indice = guide.prossimo_indice(getattr(stato, "passo_guida", 0), totale, self.modo)
        stato.passo_guida = indice
        if guide.completata(indice, totale):
            testo = TESTI["ETICHETTA_GUIDA_FINITA"]
        else:
            testo = TESTI["ETICHETTA_GUIDA_PASSO"].format(numero=indice + 1, totale=totale)
        self.annuncia(context, testo)
        return {"FINISHED"}


CLASSI = (
    FORMAFACILE_OT_guida_apri,
    FORMAFACILE_OT_guida_esegui,
    FORMAFACILE_OT_guida_naviga,
)
