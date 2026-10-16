"""Creazione dell'immagine finale: controlli, valori prudenti e salvataggio.

Questa è la parte delicata dell'estensione: qui si usano il processore, la
memoria e lo spazio su disco dell'utente. Le scelte sono quindi prudenti e in
chiaro:

* i valori di partenza sono quelli della scena (di solito 1920×1080) e i
  campioni consigliati dalla qualità scelta, mai i 4096 campioni del valore
  predefinito di Blender;
* prima di iniziare si controlla che ci sia una telecamera, che la cartella
  esista e si possa scrivere, che la memoria libera basti e che l'immagine non
  sia enorme;
* ogni errore diventa un testo italiano comprensibile: memoria insufficiente,
  cartella non valida, motore non disponibile, errore di Blender;
* il file scritto viene riaperto subito da Blender: se non si apre, il comando
  lo dice invece di dichiarare un successo che non c'è stato.

In una finestra vera Blender mostra il proprio avanzamento e si può interrompere
con Esc: la creazione passa dal comando nativo in modalità interattiva. Senza
finestra (o quando il disegno parte da uno script) si aspetta la fine del
lavoro, con la barra di avanzamento di Blender.
"""

from __future__ import annotations

import os
import shutil

import bpy

from .. import configuration
from ..localization import TESTI
from ..logging_service import ottieni_logger
from ..scene import aspetto


# Segnali di Blender registrati da `segui_esito`, con il loro elenco.
_SEGNALI_ESITO: list[tuple[str, object]] = []


class ErroreImmaginazione(RuntimeError):
    """Errore con un testo italiano pronto da mostrare all'utente."""

    def __init__(self, chiave_testo: str):
        super().__init__(chiave_testo)
        self.chiave_testo = chiave_testo

    @property
    def testo(self) -> str:
        """Frase da mostrare, presa dalla mappa centrale dei testi."""
        return TESTI[self.chiave_testo]


# ------------------------------------------------------------------ controlli


def memoria_disponibile_mb() -> float | None:
    """Memoria libera stimata, in megabyte; `None` quando non si può sapere.

    Su Windows e su alcuni sistemi la misura non è disponibile: in quel caso i
    controlli che la usano vengono semplicemente saltati, invece di bloccare il
    lavoro con un numero inventato.
    """
    for nome, fattore in (("SC_AVPHYS_PAGES", "SC_PAGE_SIZE"), ("SC_AVPHYS_PAGES", "SC_PAGESIZE")):
        try:
            pagine = os.sysconf(nome)
            dimensione = os.sysconf(fattore)
        except (AttributeError, OSError, ValueError):
            continue
        if pagine > 0 and dimensione > 0:
            return pagine * dimensione / (1024.0 * 1024.0)
    return None


def spazio_libero_mb(cartella: str) -> float | None:
    """Spazio libero su disco della cartella indicata, in megabyte."""
    try:
        uso = shutil.disk_usage(str(cartella))
    except (OSError, ValueError):
        return None
    return uso.free / (1024.0 * 1024.0)


def problema_cartella(cartella: str) -> str:
    """Chiave del testo da mostrare se la cartella non va bene, altrimenti vuoto."""
    problema = aspetto.cartella_problema(cartella)
    if problema:
        return problema
    libero = spazio_libero_mb(cartella)
    if libero is not None and libero < configuration.SPAZIO_MINIMO_MB:
        return "ERRORE_SPAZIO_INSUFFICIENTE"
    return ""


def pixel_dell_immagine(scena) -> int:
    """Pixel dell'immagine finale con i valori impostati adesso."""
    render = getattr(scena, "render", None)
    if render is None:
        return 0
    return aspetto.pixel_immagine(
        int(getattr(render, "resolution_x", 0) or 0),
        int(getattr(render, "resolution_y", 0) or 0),
        int(getattr(render, "resolution_percentage", 100) or 100),
    )


def problema_memoria(pixel: int) -> str:
    """Chiave del testo da mostrare quando la memoria libera non basta."""
    disponibile = memoria_disponibile_mb()
    if disponibile is None:
        return ""
    richiesta = aspetto.stima_memoria_mb(pixel)
    if disponibile < configuration.MEMORIA_MINIMA_MB:
        return "ERRORE_MEMORIA_INSUFFICIENTE"
    if richiesta > disponibile * configuration.MEMORIA_RISERVA_FATTORE:
        return "ERRORE_MEMORIA_INSUFFICIENTE"
    return ""


def controlla(context, cartella: str) -> str:
    """Controlli da fare *prima* di iniziare. Vuoto significa: si può procedere."""
    scena = getattr(context, "scene", None)
    if scena is None:
        return "ERRORE_RENDER_FALLITO"
    if getattr(scena, "camera", None) is None:
        return "ERRORE_TELECAMERA_MANCANTE"
    problema = problema_cartella(cartella)
    if problema:
        return problema
    pixel = pixel_dell_immagine(scena)
    if pixel > configuration.PIXEL_MASSIMI_IMMAGINE:
        return "ERRORE_PIXEL_TROPPI"
    problema = problema_memoria(pixel)
    if problema:
        return problema
    if getattr(context, "mode", "OBJECT") != "OBJECT":
        return "ERRORE_IMMAGINE_IN_MODIFICA"
    return ""


# ------------------------------------------------------------------ valori


def imposta_qualita(scena, chiave: str, percentuale: int | None = None,
                    campioni: int | None = None) -> aspetto.Qualita:
    """Applica la qualità scelta, con le correzioni delle impostazioni avanzate.

    I campioni vengono scritti sia per il motore veloce sia per quello preciso:
    cambiando motore il valore resta coerente, invece di tornare ai 4096
    campioni predefiniti di Blender.
    """
    qualita = aspetto.qualita(chiave)
    render = getattr(scena, "render", None)
    valore = qualita.percentuale if percentuale is None else aspetto.limita(
        percentuale, configuration.QUALITA_PERCENTUALE_MINIMA, configuration.QUALITA_PERCENTUALE_MASSIMA
    )
    try:
        render.resolution_percentage = int(round(float(valore)))
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass

    if campioni is None or int(campioni) == configuration.CAMPIONI_AUTOMATICI:
        campioni_eevee = qualita.campioni_eevee
        campioni_cycles = qualita.campioni_cycles
    else:
        valore_campioni = int(
            aspetto.limita(campioni, configuration.CAMPIONI_MINIMI, configuration.CAMPIONI_MASSIMI)
        )
        campioni_eevee = campioni_cycles = valore_campioni
    _imposta_campioni(scena, campioni_eevee, campioni_cycles)


def _imposta_campioni(scena, campioni_eevee: int, campioni_cycles: int) -> None:
    """Scrive i campioni nei due motori, dove le proprietà esistono."""
    eevee = getattr(scena, "eevee", None)
    for nome in ("taa_render_samples", "taa_samples"):
        if eevee is not None and hasattr(eevee, nome):
            try:
                setattr(eevee, nome, int(campioni_eevee))
            except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
                pass
    cicli = getattr(scena, "cycles", None)
    if cicli is not None:
        for nome, valore in (("samples", int(campioni_cycles)), ("use_denoising", True)):
            if not hasattr(cicli, nome):
                continue
            try:
                setattr(cicli, nome, valore)
            except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
                pass


def motore_della_scena(scena) -> str:
    """Identificatore del motore di Blender impostato nella scena."""
    return str(getattr(getattr(scena, "render", None), "engine", ""))


def imposta_motore(scena, chiave: str) -> bool:
    """Sceglie il motore che disegna l'immagine, se questa installazione lo ha.

    Non ci si fida dell'elenco dichiarato dei motori: alcuni motori di Blender
    arrivano da componenti aggiuntivi e l'elenco può non aggiornarsi. Si scrive
    il motore e si rilegge: se Blender non l'ha accettato, la risposta è no.
    """
    if chiave == aspetto.MOTORE_COME_IN_BLENDER:
        return True
    identificatore = aspetto.MOTORI_BLENDER.get(str(chiave), "")
    if not identificatore:
        return False
    try:
        scena.render.engine = identificatore
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    return motore_della_scena(scena) == identificatore


def imposta_formato(scena, chiave: str) -> None:
    """Imposta il formato del file e il modo colore giusto per quel formato."""
    formato = aspetto.FORMATI_BLENDER.get(str(chiave), aspetto.FORMATI_BLENDER[aspetto.FORMATO_PNG])
    impostazioni = getattr(getattr(scena, "render", None), "image_settings", None)
    if impostazioni is None:
        return
    try:
        impostazioni.file_format = formato
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return
    if not hasattr(impostazioni, "color_mode"):
        return
    try:
        # Il JPEG non ha trasparenza: chiedergliela farebbe fallire il salvataggio.
        impostazioni.color_mode = "RGB" if formato == "JPEG" else "RGBA"
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return


def prepara_file(context, percorso: str) -> None:
    """Scrive nel motore di Blender dove salvare l'immagine."""
    scena = getattr(context, "scene", None)
    if scena is not None:
        scena.render.filepath = str(percorso)


# ------------------------------------------------------------------ disegno


def _errore_da_eccezione(errore: BaseException) -> ErroreImmaginazione:
    """Traduce l'errore di Blender in un testo comprensibile."""
    testo = f"{errore}".casefold()
    for parola in ("memory", "memoria", "alloc"):
        if parola in testo:
            ottieni_logger().error(f"{TESTI['LOG_ERRORE_IMMAGINE']} {type(errore).__name__}")
            return ErroreImmaginazione("ERRORE_MEMORIA_DURANTE_IL_LAVORO")
    ottieni_logger().error(f"{TESTI['LOG_ERRORE_IMMAGINE']} {type(errore).__name__}")
    return ErroreImmaginazione("ERRORE_RENDER_FALLITO")


def disegna_immagine(context, percorso: str) -> None:
    """Crea l'immagine aspettando la fine del lavoro.

    È il modo senza finestra: la barra di avanzamento di Blender accompagna il
    lavoro e alla fine il file è già stato scritto. Gli errori di memoria e gli
    altri errori di Blender diventano testi comprensibili.
    """
    prepara_file(context, percorso)
    try:
        bpy.ops.wm.progress_begin(0, 100)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        pass
    try:
        esito = bpy.ops.render.render(write_still=True)
    except MemoryError as errore:
        raise _errore_da_eccezione(errore) from errore
    except (RuntimeError, ReferenceError, AttributeError, TypeError, ValueError) as errore:
        raise _errore_da_eccezione(errore) from errore
    finally:
        try:
            bpy.ops.wm.progress_update(100)
            bpy.ops.wm.progress_end()
        except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
            pass

    if esito is not None and "FINISHED" not in esito:
        raise ErroreImmaginazione("ERRORE_RENDER_FALLITO")
    if not os.path.isfile(percorso):
        raise ErroreImmaginazione("ERRORE_IMMAGINE_NON_SCRITTA")


def disegna_immagine_in_finestra() -> bool:
    """Chiede a Blender di creare l'immagine nella sua finestra di disegno.

    Così l'utente vede l'avanzamento con i campioni già calcolati e può
    interrompere con Esc, come per il comando nativo di Blender. Il file viene
    scritto alla fine del lavoro. Restituisce False quando la finestra non è
    disponibile: in quel caso chi chiama usa il disegno normale.
    """
    try:
        esito = bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False
    return esito is None or "FINISHED" in esito


# ------------------------------------------------------------ lettura del file


def dimensioni_immagine(percorso: str):
    """Apre il file creato e ne legge la grandezza; `None` se non si apre.

    È il controllo onesto di fine lavoro: un file può esistere e non essere
    un'immagine leggibile (disco pieno, scrittura interrotta). L'immagine viene
    aperta con Blender e subito rilasciata, senza restare nella scena.
    """
    if not os.path.isfile(percorso):
        return None
    immagine = None
    try:
        immagine = bpy.data.images.load(str(percorso), check_existing=False)
        larghezza, altezza = int(immagine.size[0]), int(immagine.size[1])
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError, OSError):
        larghezza = altezza = 0
    finally:
        if immagine is not None:
            try:
                bpy.data.images.remove(immagine)
            except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
                pass
    if larghezza <= 0 or altezza <= 0:
        return None
    return larghezza, altezza


def segui_esito(percorso: str) -> None:
    """Scrive il messaggio giusto quando il disegno nella finestra finisce.

    Il disegno nella finestra di Blender non tiene ferma l'interfaccia: quando
    finisce (o quando l'utente lo interrompe con Esc) servono due segnali di
    Blender per saperlo. I segnali registrati qui sono elencati a parte e si
    tolgono da soli, così non restano attivi sui lavori successivi e non
    toccano i segnali di altri componenti aggiuntivi.
    """
    smetti_di_seguire()

    def fine(*_argomenti) -> None:
        smetti_di_seguire()
        annuncia_esito(percorso)

    def interrotto(*_argomenti) -> None:
        smetti_di_seguire()
        annuncia_esito(percorso, interrotto=True)

    for nome, funzione in (("render_complete", fine), ("render_cancel", interrotto)):
        elenco = getattr(bpy.app.handlers, nome, None)
        if elenco is None:
            continue
        try:
            elenco.append(funzione)
        except (AttributeError, TypeError, ValueError):
            continue
        _SEGNALI_ESITO.append((nome, funzione))


def annuncia_esito(percorso: str, interrotto: bool = False, tentativi: int = 0) -> None:
    """Dice se l'immagine è stata salvata oppure no, senza fingere.

    Blender scrive il file prima di chiamare i segnali di fine, ma su un disco
    lento la scrittura può non essere ancora visibile: prima di dichiarare un
    problema il controllo viene ripetuto, poche volte e a intervalli brevi.
    All'ultimo tentativo il messaggio è quello vero, anche se scomodo.
    """
    from ..scene import messaggi

    stato = _stato_del_file(percorso)
    if stato == "leggibile":
        testo = TESTI["MESSAGGIO_IMMAGINE_CREATA"].format(percorso=percorso)
    elif interrotto:
        testo = TESTI["MESSAGGIO_IMMAGINE_ANNULLATA"]
    elif stato == "assente" and tentativi < configuration.TENTATIVI_ESITO:
        if _riprova_piu_tardi(percorso, tentativi + 1):
            return
        # Senza un modo per riprovare più tardi si aspetta qui, una volta sola:
        # è l'unico caso in cui il messaggio può aspettare la scrittura.
        testo = (
            TESTI["MESSAGGIO_IMMAGINE_CREATA"].format(percorso=percorso)
            if _attendere_file(percorso)
            else TESTI["ERRORE_IMMAGINE_NON_SCRITTA"]
        )
    elif stato == "assente":
        testo = TESTI["ERRORE_IMMAGINE_NON_SCRITTA"]
    else:
        testo = TESTI["ERRORE_IMMAGINE_NON_LEGGIBILE"]
    try:
        messaggi.annuncia(bpy.context, testo)
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        ottieni_logger().info(testo)


def _stato_del_file(percorso: str) -> str:
    """Come sta il file creato: leggibile, presente ma illeggibile, oppure assente."""
    if not os.path.exists(percorso):
        return "assente"
    return "leggibile" if dimensioni_immagine(percorso) is not None else "illeggibile"


def _riprova_piu_tardi(percorso: str, tentativi: int) -> bool:
    """Riprova il controllo fra poco, senza fermare l'interfaccia di Blender."""
    registra = getattr(getattr(bpy.app, "timers", None), "register", None)
    if registra is None:
        return False
    try:
        registra(
            lambda: (annuncia_esito(percorso, False, tentativi), None)[1],
            first_interval=configuration.PAUSA_ESITO,
        )
        return True
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        return False


def _attendere_file(percorso: str) -> bool:
    """Aspetta per pochi decimi di secondo che il file diventi leggibile."""
    import time

    scadenza = time.monotonic() + configuration.PAUSA_ESITO * configuration.TENTATIVI_ESITO
    while time.monotonic() < scadenza:
        if dimensioni_immagine(percorso) is not None:
            return True
        time.sleep(configuration.PAUSA_ESITO / 2.0)
    return dimensioni_immagine(percorso) is not None


def smetti_di_seguire() -> None:
    """Toglie i segnali registrati da FormaFacile, e solo quelli."""
    while _SEGNALI_ESITO:
        nome, funzione = _SEGNALI_ESITO.pop()
        elenco = getattr(bpy.app.handlers, nome, None)
        if elenco is None:
            continue
        try:
            elenco.remove(funzione)
        except (AttributeError, ValueError):
            continue


def prepara_render(context, qualita: str, motore: str, formato: str,
                   percentuale: int | None = None, campioni: int | None = None) -> None:
    """Mette insieme le impostazioni scelte, nell'ordine giusto.

    L'ordine conta: il motore decide i campioni consigliati, quindi prima si
    sceglie il motore e poi si applicano qualità e formato.
    """
    scena = getattr(context, "scene", None)
    if scena is None:
        raise ErroreImmaginazione("ERRORE_RENDER_FALLITO")
    if not imposta_motore(scena, motore):
        raise ErroreImmaginazione("ERRORE_MOTORE_ASSENTE")
    imposta_qualita(scena, qualita, percentuale, campioni)
    imposta_formato(scena, formato)
