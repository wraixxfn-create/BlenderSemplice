"""Pulizia e controllo dei nomi degli oggetti.

Blender accetta nomi vuoti o con ritorni a capo e li tronca da solo a 63
caratteri: qui i nomi vengono sistemati *prima*, così l'utente vede subito il
nome che otterrà davvero. Questo modulo non dipende da Blender.
"""

from __future__ import annotations

from .. import configuration


CARATTERI_VIETATI = "\r\n\t\v\f"


def pulisci_nome(nome: str) -> str:
    """Sistema un nome scritto a mano prima di passarlo a Blender.

    I ritorni a capo e le tabulazioni diventano spazi (un nome incollato da un
    foglio di calcolo resta leggibile), i caratteri non stampabili spariscono,
    gli spazi esterni e doppi vengono tolti e il nome è troncato alla lunghezza
    massima accettata da Blender.
    """
    caratteri: list[str] = []
    for carattere in nome:
        if carattere in CARATTERI_VIETATI:
            caratteri.append(" ")
        elif carattere.isprintable():
            caratteri.append(carattere)
    ripulito = " ".join("".join(caratteri).split())
    return ripulito[: configuration.LUNGHEZZA_MASSIMA_NOME]


def nome_accettabile(nome: str) -> bool:
    """Indica se il nome contiene almeno un carattere utile."""
    return bool(pulisci_nome(nome))
