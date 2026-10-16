"""Costruzione del piano dell'interfaccia.

Le regole su che cosa mostrare (selezione singola o multipla, nessuna
selezione, modalità semplice o completa, elenco lungo, oggetti nascosti o
rinominati) vivono qui e non dipendono da Blender. `ui/renderer.py` si limita
a disegnare il piano prodotto da questo modulo.
"""

from __future__ import annotations

from .. import comandi, configuration
from ..localization import TESTI
from . import icone
from .modello import Azione, Campo, Contesto, Etichetta, Gruppo, Oggetto, Pannello, Riga


def costruisci_piano(contesto: Contesto) -> tuple[Pannello, ...]:
    """Restituisce i pannelli da disegnare per il contesto indicato."""
    pannelli = [
        Pannello("principale", _pannello_principale(contesto)),
        Pannello("scena", _pannello_scena(contesto)),
        Pannello("oggetto", _pannello_oggetto(contesto)),
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
            _azione(comandi.ID_AGGIUNGI_PIANO, TESTI["AZIONE_AGGIUNGI_PIANO"], "MESH_PLANE"),
        ),
        _riga(_azione(comandi.ID_AGGIUNGI_LUCE, TESTI["AZIONE_AGGIUNGI_LUCE"], "LIGHT")),
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

    gruppi.extend(_gruppi_trasformazioni(contesto))
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


def _gruppi_trasformazioni(contesto: Contesto) -> list[Gruppo]:
    gradi = _numero_breve(contesto.gradi_rotazione)
    percentuale = contesto.percentuale_scala

    sposta = _gruppo(
        TESTI["GRUPPO_SPOSTA"],
        _riga(
            Etichetta(TESTI["ETICHETTA_PASSO"]),
            Campo(
                riferimento=configuration.RIFERIMENTO_SCENA,
                chiave=configuration.CHIAVE_SCENA,
                proprieta=configuration.CAMPO_PASSO,
            ),
        ),
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
    )
    ruota = _gruppo(
        TESTI["GRUPPO_RUOTA"],
        _riga(
            _azione(comandi.ID_RUOTA_PASSO, TESTI["AZIONE_RUOTA_SINISTRA"], "BACK", parametri=(("verso", "sinistra"),)),
            _azione(comandi.ID_RUOTA_PASSO, TESTI["AZIONE_RUOTA_DESTRA"], "FORWARD", parametri=(("verso", "destra"),)),
        ),
        _riga(Etichetta(TESTI["ETICHETTA_GRADI_ROTAZIONE"].format(gradi=gradi))),
    )
    scala = _gruppo(
        TESTI["GRUPPO_INGRANDISCI"],
        _riga(
            _azione(comandi.ID_SCALA_PASSO, TESTI["AZIONE_PIU_GRANDE"], "ADD", parametri=(("verso", "grande"),)),
            _azione(comandi.ID_SCALA_PASSO, TESTI["AZIONE_PIU_PICCOLO"], "REMOVE", parametri=(("verso", "piccolo"),)),
        ),
        _riga(Etichetta(TESTI["ETICHETTA_PERCENTUALE"].format(percentuale=percentuale))),
    )
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
            _azione(
                comandi.ID_DUPLICA,
                TESTI["AZIONE_DUPLICA"],
                "DUPLICATE",
            )
        ),
        _riga(
            _azione(
                comandi.ID_ELIMINA,
                TESTI["AZIONE_ELIMINA"],
                "TRASH",
            )
        ),
    ]
    return _gruppo(TESTI["GRUPPO_ALTRO"], *righe)


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


def _numero_breve(valore: float) -> str:
    """Scrive un numero senza zeri inutili: 15.0 diventa 15, 7.5 resta 7.5."""
    arrotondato = round(float(valore), 2)
    if arrotondato == int(arrotondato):
        return str(int(arrotondato))
    return str(arrotondato).replace(".", ",")


def elementi_totali(pannello: Pannello) -> int:
    """Numero di elementi disegnati in un pannello, usato dai test."""
    return sum(len(riga.elementi) for gruppo in pannello.gruppi for riga in gruppo.righe)
