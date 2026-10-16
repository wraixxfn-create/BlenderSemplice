"""Costruzione del piano dell'interfaccia.

Le regole su che cosa mostrare (selezione singola o multipla, nessuna
selezione, modalità semplice o completa, elenco lungo, oggetti nascosti o
rinominati) vivono qui e non dipendono da Blender. `ui/renderer.py` si limita
a disegnare il piano prodotto da questo modulo.
"""

from __future__ import annotations

from .. import comandi, configuration
from ..localization import TESTI
from ..scene import guide
from ..scene import misure
from ..scene import regole_modellazione as regole
from ..scene import testi as testi_lunghi
from . import icone
from .modello import Azione, Campo, Contesto, Etichetta, Gruppo, Oggetto, Pannello, Riga


def costruisci_piano(contesto: Contesto) -> tuple[Pannello, ...]:
    """Restituisce i pannelli da disegnare per il contesto indicato."""
    pannelli = [
        Pannello("principale", _pannello_principale(contesto)),
        Pannello("scena", _pannello_scena(contesto)),
        Pannello("oggetto", _pannello_oggetto(contesto)),
        Pannello("modella", _pannello_modella(contesto)),
    ]
    if contesto.modalita == configuration.MODALITA_COMPLETA:
        pannelli.append(Pannello("completo", _pannello_completo(contesto)))
    return tuple(pannelli)


def chiavi_azione(contesto: Contesto) -> tuple[str, ...]:
    """Elenco degli identificatori di comando presenti nel piano."""
    identificatori: list[str] = []
    for pannello in costruisci_piano(contesto):
        for gruppo in pannello.gruppi:
            for riga in gruppo.righe:
                for elemento in riga.elementi:
                    if isinstance(elemento, Azione):
                        identificatori.append(elemento.idname)
    return tuple(identificatori)


# ---------------------------------------------------------------- principale


def _pannello_principale(contesto: Contesto) -> tuple[Gruppo, ...]:
    gruppi: list[Gruppo] = []

    if contesto.messaggio and contesto.messaggio_recente:
        gruppi.append(_gruppo("", _riga(Etichetta(contesto.messaggio, icona="INFO"))))

    if not contesto.in_modalita_oggetto:
        gruppi.append(
            _gruppo(
                "",
                _riga(Etichetta(TESTI["ETICHETTA_MODALITA_MODIFICA"], icona="INFO", avviso=True)),
            )
        )

    gruppi.append(
        _gruppo(
            "",
            _riga(Etichetta(TESTI["ETICHETTA_MODALITA"])),
            _riga(
                Campo(
                    riferimento=configuration.RIFERIMENTO_SCENA,
                    chiave=configuration.CHIAVE_SCENA,
                    proprieta=configuration.CAMPO_MODALITA,
                    espanso=True,
                )
            ),
        )
    )

    creazione = (
        _riga(
            _azione(comandi.ID_AGGIUNGI_CUBO, TESTI["AZIONE_AGGIUNGI_CUBO"], "MESH_CUBE"),
            _azione(comandi.ID_AGGIUNGI_SFERA, TESTI["AZIONE_AGGIUNGI_SFERA"], "MESH_UVSPHERE"),
        ),
        _riga(
            _azione(comandi.ID_AGGIUNGI_CILINDRO, TESTI["AZIONE_AGGIUNGI_CILINDRO"], "MESH_CYLINDER"),
            _azione(comandi.ID_AGGIUNGI_CONO, TESTI["AZIONE_AGGIUNGI_CONO"], "MESH_CONE"),
        ),
        _riga(
            _azione(comandi.ID_AGGIUNGI_PIANO, TESTI["AZIONE_AGGIUNGI_PIANO"], "MESH_PLANE"),
            _azione(comandi.ID_AGGIUNGI_TORO, TESTI["AZIONE_AGGIUNGI_TORO"], "MESH_TORUS"),
        ),
        _riga(
            _azione(comandi.ID_AGGIUNGI_TESTO, TESTI["AZIONE_AGGIUNGI_TESTO"], "FONT_DATA"),
            _azione(comandi.ID_AGGIUNGI_LUCE, TESTI["AZIONE_AGGIUNGI_LUCE"], "LIGHT"),
        ),
        _riga(
            Etichetta(
                misure.etichetta_con_unita(
                    TESTI["ETICHETTA_GRANDEZZA"], contesto.unita_lunghezza
                )
            ),
            Campo(
                riferimento=configuration.RIFERIMENTO_SCENA,
                chiave=configuration.CHIAVE_SCENA,
                proprieta=configuration.CAMPO_GRANDEZZA_FORMA,
            ),
        ),
    )
    gruppi.append(
        _gruppo(
            TESTI["GRUPPO_COSTRUISCI"],
            *(
                Riga(riga.elementi, disabilitata=not contesto.in_modalita_oggetto)
                for riga in creazione
            ),
        )
    )

    gruppi.append(
        _gruppo(
            TESTI["GRUPPO_STORIA"],
            _riga(
                _azione(comandi.ID_ANNULLA, TESTI["AZIONE_ANNULLA"], "LOOP_BACK"),
                _azione(comandi.ID_RIPETI, TESTI["AZIONE_RIPETI"], "LOOP_FORWARDS"),
            ),
        )
    )

    vista = [
        _riga(
            _azione(
                comandi.ID_VISTA_INIZIALE,
                TESTI["AZIONE_VISTA_INIZIALE"],
                "HOME",
            )
        )
    ]
    if contesto.vista_disponibile:
        vista.append(
            _riga(
                _azione(
                    comandi.ID_INQUADRA_TUTTO,
                    TESTI["AZIONE_INQUADRA_TUTTO"],
                    "VIEWZOOM",
                ),
                disabilitata=not contesto.in_modalita_oggetto,
            )
        )
    gruppi.append(_gruppo(TESTI["GRUPPO_GUARDA"], *vista))

    consigli = [_riga(Etichetta(TESTI["CONSIGLIO_ROTAZIONE"], icona="INFO"))]
    if contesto.modalita == configuration.MODALITA_COMPLETA:
        consigli.insert(0, _riga(Etichetta(TESTI["ETICHETTA_AVANZATO_ATTIVO"], icona="INFO")))
    gruppi.append(_gruppo(TESTI["GRUPPO_AIUTO"], *consigli))

    return tuple(gruppi)


# --------------------------------------------------------------------- scena


def _pannello_scena(contesto: Contesto) -> tuple[Gruppo, ...]:
    gruppi: list[Gruppo] = []
    totale = len(contesto.oggetti)
    scelti = len(contesto.scelti)

    if totale:
        gruppi.append(
            _gruppo(
                "",
                _riga(
                    Etichetta(
                        _testo_conteggio(totale, scelti, len(contesto.nascosti)), evidenzia=True
                    )
                ),
            )
        )

    if totale > contesto.soglia_filtro or contesto.filtro.strip():
        gruppi.append(
            _gruppo(
                "",
                _riga(
                    Campo(
                        riferimento=configuration.RIFERIMENTO_SCENA,
                        chiave=configuration.CHIAVE_SCENA,
                        proprieta=configuration.CAMPO_FILTRO,
                        testo=TESTI["ETICHETTA_CERCA"],
                        icona="VIEWZOOM",
                    ),
                    _azione(comandi.ID_PULISCI_FILTRO, TESTI["AZIONE_PULISCI_FILTRO"], "X", solo_icona=True),
                ),
            )
        )

    righe_selezione = [
        _riga(
            _azione(comandi.ID_SCEGLI_TUTTO, TESTI["AZIONE_SELEZIONA_TUTTO"], "CHECKMARK"),
            _azione(comandi.ID_DESCEGLI_TUTTO, TESTI["AZIONE_DESCEGLI_TUTTO"]),
        ),
    ]
    if totale:
        seconda = [
            _azione(comandi.ID_INVERTI_SCELTA, TESTI["AZIONE_INVERTI_SCELTA"]),
        ]
        if contesto.attivo is not None:
            seconda.append(
                _azione(
                    comandi.ID_SCEGLI_STESSO_TIPO,
                    TESTI["AZIONE_SCEGLI_STESSO_TIPO"],
                )
            )
        righe_selezione.append(_riga(*seconda))
    gruppi.append(_gruppo(TESTI["GRUPPO_SELEZIONE"], *righe_selezione))

    gruppi.append(_gruppo(TESTI["GRUPPO_ELENCO"], *_righe_elenco(contesto)))
    return tuple(gruppi)


def _righe_elenco(contesto: Contesto) -> tuple[Riga, ...]:
    if not contesto.oggetti:
        return (
            _riga(Etichetta(TESTI["ETICHETTA_NESSUN_OGGETTO"], icona="INFO", evidenzia=True)),
            _riga(Etichetta(TESTI["AIUTO_NESSUN_OGGETTO"])),
        )

    visibili = contesto.filtrati()
    if not visibili:
        return (
            _riga(Etichetta(TESTI["ETICHETTA_FILTRO_VUOTO"], icona="VIEWZOOM", avviso=True)),
            _riga(
                _azione(
                    comandi.ID_PULISCI_FILTRO,
                    TESTI["AZIONE_PULISCI_FILTRO"],
                    "X",
                )
            ),
        )

    righe = [_riga_oggetto(oggetto) for oggetto in visibili[: contesto.limite_elenco]]

    if len(visibili) > contesto.limite_elenco:
        righe.append(
            _riga(
                Etichetta(
                    TESTI["ETICHETTA_MANCANO_OGGETTI"].format(
                        mostrati=contesto.limite_elenco, totali=len(visibili)
                    ),
                    icona="INFO",
                )
            )
        )

    if contesto.nascosti:
        righe.append(
            _riga(
                _azione(
                    comandi.ID_MOSTRA_TUTTI,
                    TESTI["AZIONE_MOSTRA_TUTTI"],
                    "HIDE_ON",
                )
            )
        )

    return tuple(righe)


def _riga_oggetto(oggetto: Oggetto) -> Riga:
    elementi = [
        _azione(
            comandi.ID_SCEGLI_OGGETTO,
            oggetto.nome,
            oggetto.icona,
            premuto=oggetto.attivo,
            parametri=(("oggetto", oggetto.chiave),),
        ),
        _azione(
            comandi.ID_ALTERNA_SCELTA,
            TESTI["AZIONE_ALTERNA_SCELTA"],
            "CHECKBOX_HLT" if oggetto.scelto else "CHECKBOX_DEHLT",
            solo_icona=True,
            parametri=(("oggetto", oggetto.chiave),),
        ),
        _azione(
            comandi.ID_ALTERNA_VISIBILITA,
            TESTI["AZIONE_ALTERNA_VISIBILITA"],
            "HIDE_ON" if oggetto.nascosto else "HIDE_OFF",
            solo_icona=True,
            parametri=(("oggetto", oggetto.chiave),),
        ),
        _azione(
            comandi.ID_BLOCCA_SCELTA,
            TESTI["AZIONE_BLOCCA_SCELTA"] if not oggetto.bloccato else TESTI["AZIONE_SBLOCCA_SCELTA"],
            "LOCKED" if oggetto.bloccato else "UNLOCKED",
            solo_icona=True,
            parametri=(
                ("oggetto", oggetto.chiave),
                ("blocca", not oggetto.bloccato),
            ),
        ),
    ]
    if oggetto.attivo:
        elementi.append(
            _azione(
                comandi.ID_RINOMINA,
                TESTI["AZIONE_RINOMINA"],
                "GREASEPENCIL",
                solo_icona=True,
                parametri=(("oggetto", oggetto.chiave),),
            )
        )
    return _riga(*elementi)


def _testo_conteggio(totale: int, scelti: int, nascosti: int = 0) -> str:
    oggetti = TESTI["ETICHETTA_OGGETTO_UNO"] if totale == 1 else TESTI["ETICHETTA_OGGETTI"].format(numero=totale)
    if scelti == 0:
        scelta = TESTI["ETICHETTA_SCELTI_NESSUNO"]
    elif scelti == 1:
        scelta = TESTI["ETICHETTA_SCELTI_UNO"]
    else:
        scelta = TESTI["ETICHETTA_SCELTI"].format(numero=scelti)
    conteggio = TESTI["ETICHETTA_CONTEGGIO"].format(oggetti=oggetti, scelti=scelta)
    if nascosti:
        conteggio = f"{conteggio}, {TESTI['ETICHETTA_OGGETTI_NASCOSTI'].format(numero=nascosti)}"
    return conteggio


# ------------------------------------------------------------------ oggetto


def _pannello_oggetto(contesto: Contesto) -> tuple[Gruppo, ...]:
    scelti = contesto.scelti
    if not scelti:
        return (
            _gruppo(
                "",
                _riga(Etichetta(TESTI["ETICHETTA_NESSUNA_SELEZIONE"], evidenzia=True)),
                _riga(Etichetta(TESTI["AIUTO_NESSUNA_SELEZIONE"])),
                _riga(
                    _azione(
                        comandi.ID_SCEGLI_TUTTO,
                        TESTI["AZIONE_SELEZIONA_TUTTO"],
                        "CHECKMARK",
                    )
                ),
            ),
        )

    if len(scelti) == 1:
        return _gruppi_oggetto_singolo(contesto, scelti[0])
    return _gruppi_oggetti_scelti(contesto, scelti)


def _gruppi_oggetto_singolo(contesto: Contesto, oggetto: Oggetto) -> tuple[Gruppo, ...]:
    completa = contesto.modalita == configuration.MODALITA_COMPLETA
    gruppi: list[Gruppo] = []

    tipo = oggetto.tipo_parola if not completa else f"{oggetto.tipo_parola} · {oggetto.tipo}"
    righe_descrizione = [
        _riga(Etichetta(oggetto.nome, icona=oggetto.icona, evidenzia=True)),
        _riga(Etichetta(tipo)),
    ]
    riga_nome: list[object] = [
        _azione(
            comandi.ID_RINOMINA,
            TESTI["AZIONE_RINOMINA"],
            "GREASEPENCIL",
            parametri=(("oggetto", oggetto.chiave),),
        )
    ]
    if completa:
        riga_nome.append(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=oggetto.chiave,
                proprieta="name",
                testo=TESTI["ETICHETTA_NOME"],
            )
        )
    gruppi.append(_gruppo("", *righe_descrizione, _riga(*riga_nome)))
    if oggetto.nascosto:
        gruppi.append(_gruppo_nascosto(oggetto))

    gruppi.extend(_gruppi_trasformazioni(contesto, oggetto))
    gruppi.append(_gruppo_altre_azioni(contesto, oggetto))
    gruppi.extend(_gruppi_per_tipo(contesto, oggetto, completo=completa))
    return tuple(gruppi)


def _gruppo_nascosto(oggetto: Oggetto) -> Gruppo:
    """Spiega che l'oggetto non si vede e, se si può, propone di mostrarlo.

    Il comando Mostra compare solo quando il nascondimento dipende
    dall'oggetto stesso: se è la sua raccolta a nasconderlo, il pulsante non
    avrebbe effetto e sarebbe una promessa falsa.
    """
    chiave = (
        "ETICHETTA_NASCOSTO"
        if oggetto.nascosto_direttamente
        else "ETICHETTA_NASCOSTO_CON_GRUPPO"
    )
    return _gruppo("", _riga(Etichetta(TESTI[chiave], icona="HIDE_ON", avviso=True)))


def _gruppi_oggetti_scelti(contesto: Contesto, scelti: tuple[Oggetto, ...]) -> tuple[Gruppo, ...]:
    gruppi: list[Gruppo] = [
        _gruppo(
            "",
            _riga(
                Etichetta(
                    TESTI["ETICHETTA_MULTI_SELEZIONE"].format(numero=len(scelti)), evidenzia=True
                )
            ),
            _riga(Etichetta(TESTI["AIUTO_MULTI_SELEZIONE"])),
            _riga(Etichetta(_riepilogo_tipi(scelti))),
        )
    ]
    if contesto.attivo is not None:
        gruppi[0] = _gruppo(
            "",
            *gruppi[0].righe,
            _riga(Etichetta(TESTI["ETICHETTA_OGGETTO_ATTIVO"].format(nome=contesto.attivo.nome))),
        )

    gruppi.extend(_gruppi_trasformazioni(contesto))
    gruppi.append(
        _gruppo(
            "",
            _riga(
                _azione(
                    comandi.ID_INQUADRA_SCELTI,
                    TESTI["AZIONE_INQUADRA_SCELTI"],
                    "ZOOM_SELECTED",
                )
            ),
        )
    )

    righe = [
        _riga(
            _azione(
                comandi.ID_ALTERNA_VISIBILITA,
                TESTI["AZIONE_NASCONDI_SCELTI"],
                "HIDE_OFF",
            ),
        ),
        _riga(
            _azione(comandi.ID_CENTRA, TESTI["AZIONE_CENTRA"], "PIVOT_BOUNDBOX"),
            _azione(
                comandi.ID_APPOGGIA_SUL_PIANO,
                TESTI["AZIONE_APPOGGIA_SUL_PIANO"],
                "SNAP_FACE",
            ),
        ),
        _riga(
            _azione(comandi.ID_COPIA, TESTI["AZIONE_COPIA"], "COPYDOWN"),
            _azione(comandi.ID_BLOCCA_SCELTA, TESTI["AZIONE_BLOCCA_SCELTA"], "LOCKED"),
        ),
        _riga(_azione(comandi.ID_DUPLICA, TESTI["AZIONE_DUPLICA_SCELTI"], "DUPLICATE")),
        _riga(
            _azione(
                comandi.ID_ELIMINA,
                TESTI["AZIONE_ELIMINA_SCELTI"].format(numero=len(scelti)),
                "TRASH",
            )
        ),
        _riga(_azione(comandi.ID_DESCEGLI_TUTTO, TESTI["AZIONE_DESCEGLI_SCELTI"], "CHECKBOX_DEHLT")),
    ]
    gruppi.append(_gruppo(TESTI["GRUPPO_OGGETTI_SCELTI"], *righe))
    return tuple(gruppi)


def _unita(contesto: Contesto, base: str, unita: str) -> str:
    """Etichetta di un gruppo di numeri, con l'unità fra parentesi se c'è."""
    return misure.etichetta_con_unita(base, unita)


def _riga_misure(oggetto: Oggetto, proprieta: str) -> Riga:
    """Una riga con i tre assi di una misura, collegati ai dati veri."""
    return _riga(
        *(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=oggetto.chiave,
                proprieta=proprieta,
                testo=TESTI[f"ASSE_{asse.upper()}"],
                indice=indice,
            )
            for indice, asse in enumerate(misure.ASSI)
        )
    )


def _righe_rotazione(contesto: Contesto, oggetto: Oggetto) -> tuple[Riga, ...]:
    """Campi della rotazione, nella forma che l'oggetto usa davvero."""
    modo = oggetto.modo_rotazione
    if modo == "QUATERNION":
        return (
            _riga(Etichetta(TESTI["ETICHETTA_ROTAZIONE_QUATERNIONE"])),
            _riga(
                Campo(
                    riferimento=configuration.RIFERIMENTO_OGGETTO,
                    chiave=oggetto.chiave,
                    proprieta="rotation_quaternion",
                    testo=TESTI["ETICHETTA_ROTAZIONE"],
                )
            ),
        )
    if modo == "AXIS_ANGLE":
        return (
            _riga(Etichetta(TESTI["ETICHETTA_ROTAZIONE_ASSE_ANGOLO"])),
            _riga(
                Campo(
                    riferimento=configuration.RIFERIMENTO_OGGETTO,
                    chiave=oggetto.chiave,
                    proprieta="rotation_axis_angle",
                    testo=TESTI["ETICHETTA_ROTAZIONE"],
                )
            ),
        )
    return (
        _riga(
            Etichetta(
                _unita(contesto, TESTI["ETICHETTA_ROTAZIONE"], contesto.unita_angolo)
            )
        ),
        _riga_misure(oggetto, "rotation_euler"),
    )


def _gruppi_trasformazioni(contesto: Contesto, oggetto: Oggetto | None = None) -> list[Gruppo]:
    """Spostamento, rotazione e dimensione: passi, numeri e maniglie.

    I campi numerici compaiono solo con un oggetto scelto: con più oggetti
    scelti i numeri di uno solo sarebbero fuorvianti, mentre i passi valgono
    per tutti e restano disponibili.
    """
    gradi = _numero_breve(contesto.gradi_rotazione)
    percentuale = contesto.percentuale_scala

    righe_sposta: list[Riga] = [
        _riga(
            Etichetta(TESTI["ETICHETTA_PASSO"]),
            Campo(
                riferimento=configuration.RIFERIMENTO_SCENA,
                chiave=configuration.CHIAVE_SCENA,
                proprieta=configuration.CAMPO_PASSO,
            ),
        )
    ]
    if oggetto is not None:
        righe_sposta.append(
            _riga(
                Etichetta(
                    _unita(
                        contesto, TESTI["ETICHETTA_POSIZIONE"], contesto.unita_lunghezza
                    )
                )
            )
        )
        righe_sposta.append(_riga_misure(oggetto, "location"))
    righe_sposta.extend(
        (
            _riga(
                _azione(comandi.ID_SPOSTA_PASSO, TESTI["AZIONE_VERSO_SINISTRA"], parametri=(("direzione", "sinistra"),)),
                _azione(comandi.ID_SPOSTA_PASSO, TESTI["AZIONE_VERSO_DESTRA"], parametri=(("direzione", "destra"),)),
                _azione(comandi.ID_SPOSTA_PASSO, TESTI["AZIONE_VERSO_SU"], parametri=(("direzione", "su"),)),
            ),
            _riga(
                _azione(comandi.ID_SPOSTA_PASSO, TESTI["AZIONE_VERSO_GIU"], parametri=(("direzione", "giu"),)),
                _azione(comandi.ID_SPOSTA_PASSO, TESTI["AZIONE_VERSO_AVANTI"], parametri=(("direzione", "avanti"),)),
                _azione(comandi.ID_SPOSTA_PASSO, TESTI["AZIONE_VERSO_INDIETRO"], parametri=(("direzione", "indietro"),)),
            ),
            _riga(_azione(comandi.ID_STRUMENTO_SPOSTA, TESTI["AZIONE_STRUMENTO_SPOSTA"], "OBJECT_ORIGIN")),
        )
    )
    sposta = _gruppo(TESTI["GRUPPO_SPOSTA"], *righe_sposta)

    righe_ruota: list[Riga] = []
    if oggetto is not None:
        righe_ruota.extend(_righe_rotazione(contesto, oggetto))
    righe_ruota.extend(
        (
            _riga(
                _azione(comandi.ID_RUOTA_PASSO, TESTI["AZIONE_RUOTA_SINISTRA"], "BACK", parametri=(("verso", "sinistra"),)),
                _azione(comandi.ID_RUOTA_PASSO, TESTI["AZIONE_RUOTA_DESTRA"], "FORWARD", parametri=(("verso", "destra"),)),
            ),
            _riga(Etichetta(TESTI["ETICHETTA_GRADI_ROTAZIONE"].format(gradi=gradi))),
            _riga(_azione(comandi.ID_STRUMENTO_RUOTA, TESTI["AZIONE_STRUMENTO_RUOTA"], "ORIENTATION_GIMBAL")),
        )
    )
    ruota = _gruppo(TESTI["GRUPPO_RUOTA"], *righe_ruota)

    righe_scala: list[Riga] = []
    if oggetto is not None:
        righe_scala.append(
            _riga(
                Etichetta(
                    _unita(
                        contesto, TESTI["ETICHETTA_DIMENSIONE"], contesto.unita_lunghezza
                    )
                )
            )
        )
        righe_scala.append(_riga_misure(oggetto, "dimensions"))
    righe_scala.extend(
        (
            _riga(
                _azione(comandi.ID_SCALA_PASSO, TESTI["AZIONE_PIU_GRANDE"], "ADD", parametri=(("verso", "grande"),)),
                _azione(comandi.ID_SCALA_PASSO, TESTI["AZIONE_PIU_PICCOLO"], "REMOVE", parametri=(("verso", "piccolo"),)),
            ),
            _riga(Etichetta(TESTI["ETICHETTA_PERCENTUALE"].format(percentuale=percentuale))),
            _riga(_azione(comandi.ID_STRUMENTO_SCALA, TESTI["AZIONE_STRUMENTO_SCALA"], "FULLSCREEN_ENTER")),
        )
    )
    scala = _gruppo(TESTI["GRUPPO_INGRANDISCI"], *righe_scala)

    mouse = _gruppo(
        TESTI["GRUPPO_MOUSE"],
        _riga(
            _azione(comandi.ID_MOUSE_SPOSTA, TESTI["AZIONE_MOUSE_SPOSTA"]),
            _azione(comandi.ID_MOUSE_RUOTA, TESTI["AZIONE_MOUSE_RUOTA"]),
            _azione(comandi.ID_MOUSE_INGRANDISCI, TESTI["AZIONE_MOUSE_INGRANDISCI"]),
        ),
        _riga(Etichetta(TESTI["ETICHETTA_CONSIGLIO_MOUSE"])),
    )
    return [sposta, ruota, scala, mouse]


def _gruppo_altre_azioni(contesto: Contesto, oggetto: Oggetto) -> Gruppo:
    """Comandi validi per l'oggetto scelto, senza promesse impossibili.

    Il pulsante Mostra/Nascondi compare solo se il nascondimento dipende
    dall'oggetto: quando è la raccolta a nasconderlo, il pulsante non lo
    farebbe ricomparire.
    """
    prima_riga = [
        _azione(
            comandi.ID_INQUADRA_OGGETTO,
            TESTI["AZIONE_INQUADRA_OGGETTO"],
            "ZOOM_SELECTED",
            parametri=(("oggetto", oggetto.chiave),),
        )
    ]
    if oggetto.nascosto == oggetto.nascosto_direttamente:
        prima_riga.insert(
            0,
            _azione(
                comandi.ID_ALTERNA_VISIBILITA,
                TESTI["AZIONE_MOSTRA"] if oggetto.nascosto else TESTI["AZIONE_NASCONDI"],
                "HIDE_OFF" if oggetto.nascosto else "HIDE_ON",
                parametri=(("oggetto", oggetto.chiave),),
            ),
        )
    righe = [
        _riga(*prima_riga),
        _riga(
            _azione(comandi.ID_CENTRA, TESTI["AZIONE_CENTRA"], "PIVOT_BOUNDBOX"),
            _azione(
                comandi.ID_APPOGGIA_SUL_PIANO,
                TESTI["AZIONE_APPOGGIA_SUL_PIANO"],
                "SNAP_FACE",
            ),
        ),
        _riga(
            _azione(comandi.ID_COPIA, TESTI["AZIONE_COPIA"], "COPYDOWN"),
            _azione(comandi.ID_INCOLLA, TESTI["AZIONE_INCOLLA"], "PASTEDOWN"),
        ),
        _riga(
            _azione(
                comandi.ID_DUPLICA,
                TESTI["AZIONE_DUPLICA"],
                "DUPLICATE",
            )
        ),
        _riga_blocco_scelta(oggetto),
        _riga(
            _azione(
                comandi.ID_ELIMINA,
                TESTI["AZIONE_ELIMINA"],
                "TRASH",
            )
        ),
    ]
    return _gruppo(TESTI["GRUPPO_ALTRO"], *righe)


def _riga_blocco_scelta(oggetto: Oggetto) -> Riga:
    """Blocca o sblocca la scelta dell'oggetto: il pulsante dice cosa farà."""
    bloccato = oggetto.bloccato
    return _riga(
        _azione(
            comandi.ID_BLOCCA_SCELTA,
            TESTI["AZIONE_SBLOCCA_SCELTA"] if bloccato else TESTI["AZIONE_BLOCCA_SCELTA"],
            "LOCKED" if bloccato else "UNLOCKED",
            parametri=(
                ("oggetto", oggetto.chiave),
                ("blocca", not bloccato),
            ),
        )
    )


def _gruppi_per_tipo(contesto: Contesto, oggetto: Oggetto, *, completo: bool) -> list[Gruppo]:
    gruppi: list[Gruppo] = []
    if oggetto.tipo == "LIGHT":
        righe = [
            _riga(
                _azione(comandi.ID_LUCE_PIU, TESTI["AZIONE_PIU_LUMINOSA"], "ADD"),
                _azione(comandi.ID_LUCE_MENO, TESTI["AZIONE_MENO_LUMINOSA"], "REMOVE"),
            )
        ]
        if completo:
            righe.append(
                _riga(
                    Campo(
                        riferimento=configuration.RIFERIMENTO_DATI,
                        chiave=oggetto.chiave,
                        proprieta="energy",
                        testo=TESTI["ETICHETTA_POTENZA"],
                    )
                )
            )
        gruppi.append(_gruppo(TESTI["GRUPPO_LUCE"], *righe))
    elif oggetto.tipo == "CAMERA":
        righe = [
            _riga(
                _azione(
                    comandi.ID_GUARDA_DA_CAMERA,
                    TESTI["AZIONE_GUARDA_DA_CAMERA"],
                    "CAMERA_DATA",
                )
            )
        ]
        if completo:
            righe.append(
                _riga(
                    _azione(
                        comandi.ID_TELECAMERA_PRINCIPALE,
                        TESTI["AZIONE_TELECAMERA_PRINCIPALE"],
                        "CHECKMARK" if not oggetto.telecamera_principale else "",
                        premuto=oggetto.telecamera_principale,
                    )
                )
            )
        gruppi.append(_gruppo(TESTI["GRUPPO_TELECAMERA"], *righe))
    elif oggetto.tipo == "FONT":
        righe = [
            _riga(
                Campo(
                    riferimento=configuration.RIFERIMENTO_DATI,
                    chiave=oggetto.chiave,
                    proprieta="body",
                    testo=TESTI["ETICHETTA_SCRITTA"],
                )
            ),
            _riga(
                Campo(
                    riferimento=configuration.RIFERIMENTO_DATI,
                    chiave=oggetto.chiave,
                    proprieta="size",
                    testo=TESTI["ETICHETTA_ALTEZZA_TESTO"],
                )
            ),
        ]
        gruppi.append(_gruppo(TESTI["GRUPPO_TESTO"], *righe))
    return gruppi


def _riepilogo_tipi(scelti: tuple[Oggetto, ...]) -> str:
    """Riassume una scelta multipla in parole semplici: "2 forme, 1 luce"."""
    conteggi: list[tuple[str, int]] = []
    for oggetto in scelti:
        for indice, (tipo, numero) in enumerate(conteggi):
            if tipo == oggetto.tipo:
                conteggi[indice] = (tipo, numero + 1)
                break
        else:
            conteggi.append((oggetto.tipo, 1))

    parole = []
    for tipo, numero in conteggi:
        if numero == 1:
            parole.append(icone.parola_tipo(tipo))
        else:
            parole.append(TESTI[icone.chiave_plurale_tipo(tipo)].format(numero=numero))
    return ", ".join(parole)


# ------------------------------------------------------------------- modella
# Il pannello "Dai forma": gli strumenti guidati e la guida passo passo.
# Ogni gruppo è un risultato ("spigoli tondi", "copie", "gruppo"), non un
# modificatore di Blender: chi inizia cerca il risultato, non lo strumento.


def _pannello_modella(contesto: Contesto) -> tuple[Gruppo, ...]:
    """Strumenti guidati di modellazione e guida passo passo."""
    gruppi: list[Gruppo] = []
    scelti = contesto.scelti

    gruppi.append(_testata_modella(contesto))
    gruppi.append(
        _gruppo(
            TESTI["GRUPPO_SPIGOLI"],
            _riga(
                _azione_strumento(
                    comandi.ID_AMMORBIDISCI_SPIGOLI, TESTI["AZIONE_AMMORBIDISCI_SPIGOLI"]
                ),
                disabilitata=not scelti,
            ),
            _riga(
                _azione_strumento(comandi.ID_FORMA_PIU_LISCIA, TESTI["AZIONE_FORMA_PIU_LISCIA"]),
                disabilitata=not scelti,
            ),
        )
    )
    liscia = bool(contesto.attivo is not None and contesto.attivo.liscio)
    gruppi.append(
        _gruppo(
            TESTI["GRUPPO_ASPETTO"],
            _riga(Etichetta(TESTI["NOTA_ASPETTO_SUPERFICIE"])),
            _riga(
                _azione(
                    comandi.ID_SUPERFICIE_LISCIA,
                    TESTI["AZIONE_SUPERFICIE_LISCIA"],
                    comandi.ICONE_STRUMENTI_GUIDATI[comandi.ID_SUPERFICIE_LISCIA],
                    premuto=liscia,
                ),
                _azione(
                    comandi.ID_SUPERFICIE_A_FACCE,
                    TESTI["AZIONE_SUPERFICIE_A_FACCE"],
                    comandi.ICONE_STRUMENTI_GUIDATI[comandi.ID_SUPERFICIE_A_FACCE],
                    premuto=not liscia,
                ),
                disabilitata=not scelti,
            ),
        )
    )
    gruppi.append(
        _gruppo(
            TESTI["GRUPPO_SPECCHIO"],
            *_testo_lungo(TESTI["NOTA_SPECCHIO"]),
            _riga(
                _azione_strumento(comandi.ID_SPECCHIA, TESTI["AZIONE_SPECCHIA"]),
                _azione_strumento(comandi.ID_SPESSORE_PARETE, TESTI["AZIONE_SPESSORE_PARETE"]),
                disabilitata=not scelti,
            ),
        )
    )
    gruppi.append(
        _gruppo(
            TESTI["GRUPPO_COPIE"],
            _riga(
                _azione_strumento(comandi.ID_RIPETI_COPIE, TESTI["AZIONE_RIPETI_COPIE"]),
                disabilitata=not scelti,
            ),
        )
    )
    gruppi.append(
        _gruppo(
            TESTI["GRUPPO_UNISCI"],
            *_testo_lungo(TESTI["NOTA_UNISCI_SCELTA"]),
            _riga(
                _azione_strumento(comandi.ID_UNISCI_FORME, TESTI["AZIONE_UNISCI"]),
                disabilitata=len(scelti) != configuration.UNISCI_OGGETTI_ESATTI,
            ),
            _riga(
                _azione_strumento(
                    comandi.ID_CONVERTI_IN_FORMA, TESTI["AZIONE_CONVERTI_IN_FORMA"]
                ),
                disabilitata=not _da_trasformare(scelti),
            ),
        )
    )
    gruppi.append(_gruppo_allinea(contesto, scelti))
    gruppi.append(_gruppo(TESTI["GRUPPO_GRUPPI"], *_righe_gruppi(contesto)))
    gruppi.append(_gruppo(TESTI["GRUPPO_MODIFICHE"], *_righe_modifiche(contesto)))
    gruppi.append(_gruppo(TESTI["GRUPPO_GUIDA"], *_righe_guida(contesto)))
    return tuple(gruppi)


def _testata_modella(contesto: Contesto) -> Gruppo:
    """Che cosa sta per essere modificato: la forma scelta, oppure nulla."""
    scelti = contesto.scelti
    if not scelti:
        return _gruppo(
            "",
            _riga(Etichetta(TESTI["ETICHETTA_MODELLA_NIENTE"], icona="INFO", evidenzia=True)),
            *_testo_lungo(TESTI["AIUTO_MODELLA_NIENTE"]),
        )
    if len(scelti) == 1:
        return _gruppo(
            "",
            _riga(Etichetta(TESTI["ETICHETTA_MODELLA_SCELTA"], evidenzia=True)),
            _riga(Etichetta(_nome_breve(scelti[0].nome), icona=scelti[0].icona)),
        )
    # Più oggetti scelti: gli strumenti lavorano sulla forma attiva, e va detto
    # invece di lasciar credere che tocchino tutte le forme scelte.
    return _gruppo(
        "",
        _riga(Etichetta(TESTI["ETICHETTA_MODELLA_SCELTI"], evidenzia=True)),
        *_testo_lungo(TESTI["NOTA_MODELLA_PIU_SCELTI"].format(numero=len(scelti))),
    )


def _gruppo_allinea(contesto: Contesto, scelti: tuple[Oggetto, ...]) -> Gruppo:
    """Allinea e Spazia, con le loro impostazioni sempre visibili."""
    righe = [
        _riga(Etichetta(TESTI["NOTA_ALLINEA"])),
        _riga(
            Etichetta(TESTI["ETICHETTA_ASSE_ALLINEA"]),
            _campo_scena(configuration.CAMPO_ASSE_ALLINEA),
        ),
        _riga(
            Etichetta(TESTI["ETICHETTA_BORDO_ALLINEA"]),
            _campo_scena(configuration.CAMPO_BORDO_ALLINEA),
        ),
    ]
    if contesto.modalita == configuration.MODALITA_COMPLETA:
        righe.append(
            _riga(
                Etichetta(TESTI["ETICHETTA_RIFERIMENTO_ALLINEA"]),
                _campo_scena(configuration.CAMPO_RIFERIMENTO_ALLINEA, espanso=False),
            )
        )
    righe.append(
        _riga(
            _azione_strumento(comandi.ID_ALLINEA, TESTI["AZIONE_ALLINEA"]),
            _azione_strumento(comandi.ID_SPAZIA, TESTI["AZIONE_SPAZIA"]),
            disabilitata=len(scelti) < configuration.ALLINEA_OGGETTI_MINIMI,
        )
    )
    return _gruppo(TESTI["GRUPPO_ALLINEA"], *righe)


def _righe_gruppi(contesto: Contesto) -> tuple[Riga, ...]:
    """Raggruppa, togli dal gruppo e l'elenco dei gruppi con i suoi interruttori."""
    righe = [
        _riga(Etichetta(TESTI["NOTA_GRUPPI"])),
        _riga(
            _azione_strumento(comandi.ID_RAGGRUPPA, TESTI["AZIONE_RAGGRUPPA"]),
            _azione_strumento(comandi.ID_TOGLI_DAL_GRUPPO, TESTI["AZIONE_TOGLI_DAL_GRUPPO"]),
            disabilitata=not contesto.scelti,
        ),
    ]
    if not contesto.raccolte:
        righe.append(_riga(Etichetta(TESTI["ETICHETTA_GRUPPI_VUOTA"], icona="INFO")))
        return tuple(righe)

    for raccolta in contesto.raccolte[: configuration.GRUPPO_LIMITE_ELENCO]:
        righe.append(
            _riga(
                Etichetta(
                    TESTI["ETICHETTA_GRUPPO_RIGA"].format(
                        nome=_nome_breve(raccolta.nome), numero=raccolta.quanti
                    ),
                    icona="OUTLINER_COLLECTION",
                ),
                _azione(
                    comandi.ID_SCEGLI_GRUPPO,
                    TESTI["AZIONE_SCEGLI_GRUPPO"],
                    "CHECKMARK",
                    solo_icona=True,
                    parametri=(("gruppo", raccolta.chiave),),
                ),
                _azione(
                    comandi.ID_ALTERNA_GRUPPO,
                    TESTI["AZIONE_ALTERNA_GRUPPO"],
                    "HIDE_ON" if raccolta.nascosto else "HIDE_OFF",
                    solo_icona=True,
                    parametri=(("gruppo", raccolta.chiave),),
                ),
            )
        )
    if len(contesto.raccolte) > configuration.GRUPPO_LIMITE_ELENCO:
        righe.append(
            _riga(
                Etichetta(
                    TESTI["ETICHETTA_MANCANO_GRUPPI"].format(totali=len(contesto.raccolte)),
                    icona="INFO",
                )
            )
        )
    return tuple(righe)


def _righe_modifiche(contesto: Contesto) -> tuple[Riga, ...]:
    """Elenco delle modifiche non applicate, ognuna con il suo pulsante Togli."""
    modifiche = contesto.modificatori
    if not modifiche:
        return (_riga(Etichetta(TESTI["NOTA_MODIFICHE_NIENTE"], icona="MODIFIER")),)

    righe = [
        _riga(
            Etichetta(
                TESTI["ETICHETTA_MODIFICHE"].format(numero=len(modifiche)), evidenzia=True
            )
        ),
        _riga(Etichetta(TESTI["NOTA_MODIFICHE"])),
    ]
    for modifica in modifiche:
        righe.append(
            _riga(
                Etichetta(_nome_breve(modifica.parola), icona=modifica.icona),
                _azione(
                    comandi.ID_TOGLI_MODIFICHE,
                    TESTI["AZIONE_TOGLI_MODIFICA"],
                    "X",
                    solo_icona=True,
                    parametri=(("modificatore", modifica.chiave),),
                ),
            )
        )
        if modifica.problema:
            righe.append(_riga(Etichetta(modifica.problema, icona="ERROR", avviso=True)))
    righe.append(
        _riga(_azione_strumento(comandi.ID_TOGLI_MODIFICHE, TESTI["AZIONE_TOGLI_MODIFICHE"]))
    )
    return tuple(righe)


def _righe_guida(contesto: Contesto) -> tuple[Riga, ...]:
    """La guida passo passo: avvio, passo mostrato e comandi di avanzamento."""
    avvio = _riga(_azione_strumento(comandi.ID_GUIDA_APRI, TESTI["AZIONE_GUIDA_INIZIA"]))
    if not contesto.guida:
        return (
            _riga(Etichetta(TESTI["NOTA_GUIDA_CASETTA"])),
            *_testo_lungo(TESTI["AIUTO_GUIDA_OGGETTI"]),
            avvio,
        )

    corrente = guide.guida(contesto.guida)
    if corrente is None or not corrente.passi:
        return (
            _riga(Etichetta(TESTI["ERRORE_GUIDA_ASSENTE"], icona="INFO", avviso=True)),
            avvio,
        )

    totale = len(corrente.passi)
    indice = guide.indice_valido(contesto.passo_guida, totale - 1)
    passo = guide.passo_corrente(contesto.guida, indice)
    righe = [
        _riga(
            Etichetta(
                TESTI["ETICHETTA_GUIDA_PASSO"].format(numero=indice + 1, totale=totale),
                icona="BOOKMARKS",
                evidenzia=True,
            )
        )
    ]
    if passo is not None:
        righe.append(_riga(Etichetta(TESTI[passo.titolo], evidenzia=True)))
        righe.extend(_testo_lungo(TESTI[passo.spiegazione]))

    if guide.completata(contesto.passo_guida, totale):
        righe.append(
            _riga(Etichetta(TESTI["ETICHETTA_GUIDA_FINITA"], icona="CHECKMARK", evidenzia=True))
        )
    else:
        righe.append(
            _riga(_azione_strumento(comandi.ID_GUIDA_ESEGUI, TESTI["AZIONE_GUIDA_ESEGUI"]))
        )
    righe.append(
        _riga(
            _azione(
                comandi.ID_GUIDA_NAVIGA,
                TESTI["AZIONE_GUIDA_AVANTI"],
                "FORWARD",
                parametri=(("modo", comandi.MODO_GUIDA_AVANTI),),
            ),
            _azione(
                comandi.ID_GUIDA_NAVIGA,
                TESTI["AZIONE_GUIDA_INDIETRO"],
                "BACK",
                parametri=(("modo", comandi.MODO_GUIDA_INDIETRO),),
            ),
            _azione(
                comandi.ID_GUIDA_NAVIGA,
                TESTI["AZIONE_GUIDA_CHIUDI"],
                "X",
                parametri=(("modo", comandi.MODO_GUIDA_CHIUDI),),
            ),
        )
    )
    return tuple(righe)


def _campo_scena(proprieta: str, *, espanso: bool = True) -> Campo:
    """Campo collegato a un valore dello stato della scena.

    Le scelte si mostrano come pulsanti (`espanso`): nella modalità semplice
    una scelta fra due o tre valori si fa con un clic, senza aprire elenchi.
    """
    return Campo(
        riferimento=configuration.RIFERIMENTO_SCENA,
        chiave=configuration.CHIAVE_SCENA,
        proprieta=proprieta,
        espanso=espanso,
    )


def _da_trasformare(scelti: tuple[Oggetto, ...]) -> bool:
    """Indica se c'è una scritta o una curva da trasformare in una forma."""
    return any(oggetto.tipo in regole.TIPI_CONVERTIBILI for oggetto in scelti)


def _nome_breve(nome: str) -> str:
    """Nome scritto dall'utente, accorciato per stare nella barra stretta."""
    return testi_lunghi.accorcia(nome, configuration.LUNGHEZZA_MASSIMA_ETICHETTA - 8)


def _testo_lungo(testo: str) -> tuple[Riga, ...]:
    """Spiegazione su più righe: nella barra stretta le frasi lunghe si tagliano."""
    return tuple(
        _riga(Etichetta(riga))
        for riga in testi_lunghi.righe_di_testo(testo, configuration.LUNGHEZZA_MASSIMA_ETICHETTA)
    )


# ------------------------------------------------------------------ completo


def _pannello_completo(contesto: Contesto) -> tuple[Gruppo, ...]:
    attivo = contesto.attivo
    if attivo is None:
        return (
            _gruppo(
                "",
                _riga(Etichetta(TESTI["ETICHETTA_NESSUNA_SELEZIONE"], evidenzia=True)),
                _riga(Etichetta(TESTI["AIUTO_NESSUNA_SELEZIONE"])),
            ),
        )

    righe = [
        _riga(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=attivo.chiave,
                proprieta="location",
                testo=TESTI["ETICHETTA_POSIZIONE"],
            )
        ),
        _riga(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=attivo.chiave,
                proprieta="rotation_mode",
                testo=TESTI["ETICHETTA_MODO_ROTAZIONE"],
            )
        ),
        _riga(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=attivo.chiave,
                proprieta=_campo_rotazione(attivo.modo_rotazione),
                testo=TESTI["ETICHETTA_ROTAZIONE"],
            )
        ),
        _riga(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=attivo.chiave,
                proprieta="scale",
                testo=TESTI["ETICHETTA_DIMENSIONE"],
            )
        ),
        _riga(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=attivo.chiave,
                proprieta="display_type",
                testo=TESTI["ETICHETTA_ASPETTO"],
            )
        ),
        _riga(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=attivo.chiave,
                proprieta="hide_select",
                testo=TESTI["ETICHETTA_BLOCCO_SCELTA"],
                interruttore=True,
            )
        ),
        _riga(
            Campo(
                riferimento=configuration.RIFERIMENTO_OGGETTO,
                chiave=attivo.chiave,
                proprieta="hide_render",
                testo=TESTI["ETICHETTA_NASCONDI_RENDER"],
                interruttore=True,
            )
        ),
    ]
    if attivo.tipo == "LIGHT":
        righe.append(
            _riga(
                Campo(
                    riferimento=configuration.RIFERIMENTO_DATI,
                    chiave=attivo.chiave,
                    proprieta="energy",
                    testo=TESTI["ETICHETTA_POTENZA"],
                )
            )
        )

    gruppi = [_gruppo(TESTI["GRUPPO_TECNICO"], *righe)]

    dati = [
        _riga(Etichetta(TESTI["ETICHETTA_TIPO_TECNICO"].format(tipo=attivo.tipo), icona=attivo.icona)),
    ]
    if attivo.nome_dati:
        dati.append(
            _riga(
                Campo(
                    riferimento=configuration.RIFERIMENTO_DATI,
                    chiave=attivo.chiave,
                    proprieta="name",
                    testo=TESTI["ETICHETTA_NOME_DATI"],
                )
            )
        )
    if attivo.tipo == "MESH":
        dati.append(
            _riga(
                Etichetta(
                    TESTI["ETICHETTA_DATI_MESH"].format(vertici=attivo.vertici, facce=attivo.facce)
                )
            )
        )
    gruppi.append(_gruppo(TESTI["GRUPPO_DATI"], *dati))
    gruppi.append(
        _gruppo(TESTI["GRUPPO_AIUTO"], _riga(Etichetta(TESTI["ETICHETTA_PUNTA_SCHEDA"], icona="INFO")))
    )
    return tuple(gruppi)


def _campo_rotazione(modo: str) -> str:
    if modo == "QUATERNION":
        return "rotation_quaternion"
    if modo == "AXIS_ANGLE":
        return "rotation_axis_angle"
    return "rotation_euler"


# ------------------------------------------------------------------- aiutanti


def _gruppo(titolo: str, *righe: Riga) -> Gruppo:
    return Gruppo(titolo, tuple(righe))


def _riga(*elementi: object, disabilitata: bool = False, distanziata: bool = False) -> Riga:
    return Riga(tuple(elementi), disabilitata=disabilitata, distanziata=distanziata)  # type: ignore[arg-type]


def _azione(
    idname: str,
    testo: str,
    icona: str = "",
    *,
    premuto: bool = False,
    solo_icona: bool = False,
    parametri: tuple[tuple[str, object], ...] = (),
) -> Azione:
    return Azione(
        idname=idname,
        testo=testo,
        icona=icona,
        premuto=premuto,
        solo_icona=solo_icona,
        parametri=parametri,
    )


def _azione_strumento(idname: str, testo: str) -> Azione:
    """Pulsante di uno strumento guidato, con l'icona dichiarata nella tabella."""
    return _azione(idname, testo, comandi.ICONE_STRUMENTI_GUIDATI.get(idname, ""))


def _numero_breve(valore: float) -> str:
    """Scrive un numero senza zeri inutili: 15.0 diventa 15, 7.5 resta 7.5."""
    arrotondato = round(float(valore), 2)
    if arrotondato == int(arrotondato):
        return str(int(arrotondato))
    return str(arrotondato).replace(".", ",")


def elementi_totali(pannello: Pannello) -> int:
    """Numero di elementi disegnati in un pannello, usato dai test."""
    return sum(len(riga.elementi) for gruppo in pannello.gruppi for riga in gruppo.righe)
