"""Spostamenti, rotazioni, dimensioni a passi e posizioni precise.

I comandi a passi muovono di poco, gli altri portano al centro o appoggiano
sul piano di lavoro. Tutti agiscono solo sugli oggetti scelti, rispettano i
blocchi messi in Blender (asse bloccato, dimensione bloccata) e lasciano al
suo posto l'oggetto attivo.
"""

from __future__ import annotations

import bpy

from .. import comandi, configuration
from ..blender import trasformazioni
from ..localization import TESTI
from ..scene.stato import stato_della_scena
from .base import OperatoreFormaFacile


def _passo(context) -> float:
    """Passo corrente, letto dallo stato della scena."""
    stato = stato_della_scena(getattr(context, "scene", None))
    if stato is None or stato.passo <= 0.0:
        return configuration.PASSO_PREDEFINITO
    return float(stato.passo)


def _voci_direzione():
    return tuple(
        (
            direzione,
            TESTI[comandi.TESTI_DIREZIONE[direzione]],
            TESTI[comandi.AIUTI_DIREZIONE[direzione]].format(
                passo=f"{configuration.PASSO_PREDEFINITO:g}".replace(".", ",")
            ),
        )
        for direzione in comandi.DIREZIONI
    )


def _voci_rotazione():
    return tuple(
        (
            verso,
            TESTI[comandi.TESTI_ROTAZIONE[verso]],
            TESTI[comandi.AIUTI_ROTAZIONE[verso]].format(
                gradi=f"{configuration.ANGOLO_PREDEFINITO_GRADI:g}".replace(".", ",")
            ),
        )
        for verso in comandi.VERSI_ROTAZIONE
    )


def _voci_dimensione():
    percentuale = int(round((configuration.FATTORE_SCALA_PREDEFINITO - 1.0) * 100))
    return tuple(
        (
            verso,
            TESTI[comandi.TESTI_DIMENSIONE[verso]],
            TESTI[comandi.AIUTI_DIMENSIONE[verso]].format(percentuale=percentuale),
        )
        for verso in comandi.VERSI_DIMENSIONE
    )


class _OperatoreTrasformazione(OperatoreFormaFacile):
    """Base per i comandi a passi che agiscono sugli oggetti scelti.

    Nessun comando tocca un oggetto che non è scelto: la lista arriva sempre
    dalla scelta di Blender, mai da `scene.objects`.
    """

    @classmethod
    def poll(cls, context):
        return OperatoreFormaFacile.in_modalita_oggetto(context) and bool(
            OperatoreFormaFacile.scelti(context)
        )

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        raise NotImplementedError

    def applica(self, context, azione) -> set[str]:
        """Esegue l'azione sugli oggetti scelti e scrive il messaggio italiano.

        `azione` riceve la lista degli oggetti scelti e restituisce l'esito del
        servizio di trasformazione. Gli errori conosciuti diventano un
        messaggio in italiano, non un errore tecnico.
        """
        scelti = self.scelti(context)
        if not scelti:
            return self.richiedi_selezione(context)
        nomi = [oggetto.name for oggetto in scelti]
        try:
            with self.con_attivo_salvo(context):
                esito = azione(scelti)
        except trasformazioni.ErroreTrasformazione as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        testo = self.messaggio(context, esito.applicati, nomi)
        if getattr(esito, "bloccati", 0):
            nota = TESTI["AVVISO_TRASFORMAZIONE_PARZIALE"].format(numero=esito.bloccati)
            testo = f"{testo} {nota}"
        self.annuncia(context, testo)
        return {"FINISHED"}


class FORMAFACILE_OT_sposta_passo(_OperatoreTrasformazione):
    """Sposta gli oggetti scelti nella direzione indicata."""

    bl_idname = comandi.ID_SPOSTA_PASSO
    bl_label = TESTI["GRUPPO_SPOSTA"]
    bl_description = TESTI["AIUTO_VERSO_DESTRA"]

    direzione: bpy.props.EnumProperty(items=_voci_direzione(), default="destra", options={"HIDDEN"})

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        verso = TESTI[comandi.TESTI_DIREZIONE[self.direzione]].lower()
        if quanti == 1:
            return TESTI["MESSAGGIO_MOSSO"].format(nome=nomi[0], verso=verso)
        return TESTI["MESSAGGIO_MOSSI"].format(numero=quanti, verso=verso)

    def execute(self, context):
        passo = _passo(context)
        vettore = comandi.VETTORI_DIREZIONE[self.direzione]
        spostamento = (vettore[0] * passo, vettore[1] * passo, vettore[2] * passo)
        return self.applica(context, lambda scelti: trasformazioni.sposta(scelti, spostamento))


class FORMAFACILE_OT_ruota_passo(_OperatoreTrasformazione):
    """Ruota gli oggetti scelti attorno all'asse verticale."""

    bl_idname = comandi.ID_RUOTA_PASSO
    bl_label = TESTI["GRUPPO_RUOTA"]
    bl_description = TESTI["AIUTO_RUOTA_DESTRA"]

    verso: bpy.props.EnumProperty(items=_voci_rotazione(), default="destra", options={"HIDDEN"})

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        if quanti == 1:
            return TESTI["MESSAGGIO_RUOTATO"].format(nome=nomi[0])
        return TESTI["MESSAGGIO_RUOTATI"].format(numero=quanti)

    def execute(self, context):
        gradi = configuration.ANGOLO_PREDEFINITO_GRADI * comandi.SEGNI_ROTAZIONE[self.verso]
        radianti = trasformazioni.gradi_in_radianti(gradi)
        return self.applica(context, lambda scelti: trasformazioni.ruota(scelti, radianti))


class FORMAFACILE_OT_scala_passo(_OperatoreTrasformazione):
    """Ingrandisce o rimpicciolisce gli oggetti scelti."""

    bl_idname = comandi.ID_SCALA_PASSO
    bl_label = TESTI["GRUPPO_INGRANDISCI"]
    bl_description = TESTI["AIUTO_PIU_GRANDE"]

    verso: bpy.props.EnumProperty(items=_voci_dimensione(), default="grande", options={"HIDDEN"})

    def messaggio(self, context, quanti: int, nomi: list[str]) -> str:
        if quanti == 1:
            return TESTI["MESSAGGIO_SCALATO"].format(nome=nomi[0])
        return TESTI["MESSAGGIO_SCALATI"].format(numero=quanti)

    def execute(self, context):
        fattore = configuration.FATTORE_SCALA_PREDEFINITO
        if self.verso == "piccolo":
            fattore = 1.0 / configuration.FATTORE_SCALA_PREDEFINITO
        return self.applica(context, lambda scelti: trasformazioni.ingrandisci(scelti, fattore))


CLASSI = (
    FORMAFACILE_OT_sposta_passo,
    FORMAFACILE_OT_ruota_passo,
    FORMAFACILE_OT_scala_passo,
)


class _OperatorePosizione(_OperatoreTrasformazione):
    """Base dei comandi che spostano gli oggetti in una posizione precisa."""

    def esegui(self, context, azione, singolare: str, plurale: str, nota_esito=None) -> set[str]:
        """Applica lo spostamento e annuncia il risultato in italiano.

        `nota_esito`, se indicata, riceve l'esito e restituisce una frase da
        aggiungere quando serve (per esempio per gli oggetti senza una forma
        propria, appoggiati per il loro punto di riferimento).
        """
        scelti = self.scelti(context)
        if not scelti:
            return self.richiedi_selezione(context)
        nomi = [oggetto.name for oggetto in scelti]
        try:
            with self.con_attivo_salvo(context):
                esito = azione(scelti)
        except trasformazioni.ErroreTrasformazione as errore:
            self.report({"WARNING"}, str(errore))
            self.annuncia(context, str(errore))
            return {"CANCELLED"}
        nota = nota_esito(esito) if nota_esito is not None else ""
        self.annuncia_esito(context, esito, singolare, plurale, nomi[0] if nomi else "", nota)
        return {"FINISHED"}


class FORMAFACILE_OT_centra(_OperatorePosizione):
    """Porta gli oggetti scelti al centro della scena."""

    bl_idname = comandi.ID_CENTRA
    bl_label = TESTI["AZIONE_CENTRA"]
    bl_description = TESTI["AIUTO_CENTRA"]

    def execute(self, context):
        return self.esegui(
            context,
            trasformazioni.centra,
            "MESSAGGIO_CENTRATO",
            "MESSAGGIO_CENTRATI",
        )


class FORMAFACILE_OT_appoggia_sul_piano(_OperatorePosizione):
    """Appoggia gli oggetti scelti sul piano di lavoro."""

    bl_idname = comandi.ID_APPOGGIA_SUL_PIANO
    bl_label = TESTI["AZIONE_APPOGGIA_SUL_PIANO"]
    bl_description = TESTI["AIUTO_APPOGGIA_SUL_PIANO"]

    def execute(self, context):
        vettore = getattr(context, "view_layer", None)

        def azione(scelti):
            return trasformazioni.appoggia_sul_piano(scelti, vettore)

        def nota(esito) -> str:
            if getattr(esito, "senza_forma", 0):
                return TESTI["AVVISO_APPOGGIO_SENZA_FORMA"]
            return ""

        return self.esegui(
            context,
            azione,
            "MESSAGGIO_APPOGGIATO",
            "MESSAGGIO_APPOGGIATI",
            nota_esito=nota,
        )


CLASSI = (
    *CLASSI,
    FORMAFACILE_OT_centra,
    FORMAFACILE_OT_appoggia_sul_piano,
)
