"""Interfaccia finta condivisa dalle prove automatiche.

Riceve le stesse chiamate che i pannelli fanno a `bpy.types.UILayout`, le
annota in un registro e non disegna nulla. Serve a verificare che cosa
mostrerebbe l'interfaccia senza aprire Blender: le prove di unità usano questo
modulo da solo, quelle dentro Blender lo usano insieme ai controlli sull'API
reale (`bpy.types.UILayout`, operatori e loro proprietà).

`prepara_import_puro()` rende importabili i moduli dell'interfaccia anche fuori
da Blender: il pacchetto del componente aggiuntivo importa `bpy` appena viene
caricato, mentre i moduli dell'interfaccia no, quindi le prove di unità
caricano soltanto questi ultimi.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACCHETTO = ROOT / "addon" / "formafacile_3d"


def prepara_import_puro() -> None:
    """Rende importabili `formafacile_3d.ui.*` senza Blender.

    Il pacchetto principale viene sostituito da un contenitore vuoto: serve solo
    a far funzionare gli import relativi dei moduli puri dell'interfaccia.
    """
    for nome, percorso in (
        ("formafacile_3d", PACCHETTO),
        ("formafacile_3d.ui", PACCHETTO / "ui"),
    ):
        if nome in sys.modules:
            continue
        finto = types.ModuleType(nome)
        finto.__path__ = [str(percorso)]  # type: ignore[attr-defined]
        finto.__doc__ = "Pacchetto caricato dalle prove automatiche, senza Blender."
        sys.modules[nome] = finto


class BloccoFinto:
    """Blocco di interfaccia finto: annota chiamate e proprietà assegnate."""

    def __init__(self, registro: list[dict[str, Any]], profondita: int = 0):
        object.__setattr__(self, "registro", registro)
        object.__setattr__(self, "profondita", profondita)
        # I valori iniziali non sono modifiche: non finiscono nel registro.
        object.__setattr__(self, "enabled", True)
        object.__setattr__(self, "alert", False)

    def __setattr__(self, nome: str, valore: object) -> None:
        if nome.startswith("__"):
            object.__setattr__(self, nome, valore)
            return
        self.registro.append(
            {"tipo": "proprieta", "nome": nome, "valore": valore, "profondita": self.profondita}
        )
        object.__setattr__(self, nome, valore)

    # ------------------------------------------------------------ strutture

    def _argomenti_figlio(self) -> dict[str, Any]:
        """Argomenti in più da passare ai blocchi figli (nessuno, qui)."""
        return {}

    def _figlio(self) -> "BloccoFinto":
        """Un blocco figlio dello stesso tipo: anche i figli sanno fallire."""
        return type(self)(self.registro, self.profondita + 1, **self._argomenti_figlio())

    def row(self, **parametri: object) -> "BloccoFinto":
        return self._struttura("riga", parametri)

    def column(self, **parametri: object) -> "BloccoFinto":
        return self._struttura("colonna", parametri)

    def box(self, **parametri: object) -> "BloccoFinto":
        return self._struttura("riquadro", parametri)

    def split(self, **parametri: object) -> "BloccoFinto":
        return self._struttura("divisione", parametri)

    def separator(self, **parametri: object) -> None:
        self._struttura("separatore", parametri)

    def _struttura(self, tipo: str, parametri: dict[str, object]) -> "BloccoFinto":
        self.registro.append(
            {"tipo": tipo, "parametri": dict(parametri), "profondita": self.profondita}
        )
        return self._figlio()

    # ------------------------------------------------------------ contenuti

    def label(self, **parametri: object) -> None:
        self.registro.append(
            {"tipo": "etichetta", "parametri": dict(parametri), "profondita": self.profondita}
        )

    def operator(self, idname: str, **parametri: object) -> "ProprietaFinta":
        voce: dict[str, Any] = {
            "tipo": "comando",
            "idname": idname,
            "parametri": dict(parametri),
            "profondita": self.profondita,
            "valori": {},
        }
        self.registro.append(voce)
        return ProprietaFinta(idname, voce)

    def prop(self, data: object, property: str, **parametri: object) -> None:
        self.registro.append(
            {
                "tipo": "campo",
                "dati": data,
                "proprieta": property,
                "parametri": dict(parametri),
                "profondita": self.profondita,
            }
        )


class BloccoCheFallisce(BloccoFinto):
    """Blocco finto che fallisce su una chiamata precisa, come Blender a volte fa."""

    def __init__(
        self,
        registro: list[dict[str, Any]],
        profondita: int = 0,
        *,
        nome_metodo: str = "operator",
    ):
        super().__init__(registro, profondita)
        object.__setattr__(self, "nome_metodo", nome_metodo)

    def _argomenti_figlio(self) -> dict[str, Any]:
        return {"nome_metodo": self.nome_metodo}

    def operator(self, idname: str, **parametri: object) -> "ProprietaFinta":
        if self.nome_metodo == "operator":
            raise TypeError("Comando non disponibile")
        return super().operator(idname, **parametri)

    def prop(self, data: object, property: str, **parametri: object) -> None:
        if self.nome_metodo == "prop":
            raise TypeError("Campo non disponibile")
        return super().prop(data, property, **parametri)


class ProprietaFinta:
    """Proprietà di un comando: annota i valori assegnati nel registro."""

    def __init__(self, idname: str, voce: dict[str, Any]):
        object.__setattr__(self, "idname", idname)
        object.__setattr__(self, "voce", voce)

    @property
    def valori(self) -> dict[str, object]:
        return dict(self.voce["valori"])

    def __setattr__(self, nome: str, valore: object) -> None:
        self.voce["valori"][nome] = valore


class IstanzaFinta:
    """Sostituto dell'istanza di pannello: espone quello che serve al disegno."""

    def __init__(self, registro: list[dict[str, Any]], chiave_piano: str = ""):
        self.layout = BloccoFinto(registro)
        self.chiave_piano = chiave_piano
        self.bl_label = ""


def disegna(classe_pannello: Any, contesto: object) -> list[dict[str, Any]]:
    """Esegue il disegno di un pannello con il blocco finto.

    Restituisce il registro delle chiamate: se il disegno solleva un'eccezione,
    la prova non supera il controllo, perché un pannello non deve mai fallire.
    """
    registro: list[dict[str, Any]] = []
    istanza = IstanzaFinta(registro, getattr(classe_pannello, "chiave_piano", ""))
    classe_pannello.draw(istanza, contesto)
    return registro


# ------------------------------------------------------------------ lettura


def _voci(registro: list[dict[str, Any]], tipo: str) -> list[dict[str, Any]]:
    return [voce for voce in registro if voce["tipo"] == tipo]


def etichette(registro: list[dict[str, Any]]) -> list[str]:
    """Testi delle etichette disegnate, in ordine."""
    return [str(voce["parametri"].get("text", "")) for voce in _voci(registro, "etichetta")]


def comandi(registro: list[dict[str, Any]]) -> list[str]:
    """Identificatori dei comandi disegnati, in ordine."""
    return [str(voce["idname"]) for voce in _voci(registro, "comando")]


def testi_comandi(registro: list[dict[str, Any]]) -> list[str]:
    """Testi dei pulsanti disegnati, in ordine."""
    return [str(voce["parametri"].get("text", "")) for voce in _voci(registro, "comando")]


def icone_usate(registro: list[dict[str, Any]]) -> list[str]:
    """Icone usate nelle etichette e nei pulsanti."""
    return [
        str(voce["parametri"]["icon"])
        for voce in registro
        if voce["tipo"] in {"etichetta", "comando"} and voce["parametri"].get("icon")
    ]


def campi(registro: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Coppie (tipo del blocco dati, proprietà) dei campi disegnati."""
    return [
        (type(voce["dati"]).__name__, str(voce["proprieta"])) for voce in _voci(registro, "campo")
    ]


def valori(registro: list[dict[str, Any]], idname: str) -> list[dict[str, object]]:
    """Valori assegnati ai pulsanti di un comando."""
    return [
        voce["valori"]
        for voce in registro
        if voce["tipo"] == "comando" and voce["idname"] == idname
    ]


def proprieta_assegnate(registro: list[dict[str, Any]], nome: str) -> list[object]:
    """Valori assegnati a una proprietà dei blocchi (per esempio `enabled`)."""
    return [voce["valore"] for voce in _voci(registro, "proprieta") if voce["nome"] == nome]


def righe(registro: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Voci di tipo riga, in ordine di disegno."""
    return _voci(registro, "riga")


def riquadri(registro: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Voci di tipo riquadro (i gruppi con titolo), in ordine di disegno."""
    return _voci(registro, "riquadro")


def testi_disabilitati(registro: list[dict[str, Any]]) -> list[str]:
    """Testi disegnati al posto di campi non disponibili."""
    return etichette(registro)
