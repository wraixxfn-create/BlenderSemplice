"""Testi lunghi spezzati per la barra stretta laterale.

La barra laterale di Blender è larga poche decine di caratteri: un'etichetta
troppo lunga viene tagliata a metà parola e la spiegazione non si legge. Qui
stanno due sole funzioni, pure e verificabili senza Blender: una spezza un
testo in righe di lunghezza massima, l'altra accorda un nome troppo lungo.
Le usano i pannelli e le finestrelle di conferma dei comandi guidati, così le
spiegazioni si leggono per intero invece di sparire.
"""

from __future__ import annotations

# Carattere che segnala un testo accorciato: un solo carattere, come nelle
# liste di Blender.
SEGNO_ACCORCIATO = "…"


def righe_di_testo(testo: str, massimo: int) -> tuple[str, ...]:
    """Spezza un testo in righe di al massimo `massimo` caratteri.

    Le parole non vengono mai tagliate: una parola più lunga del massimo resta
    su una riga sua, perché spezzarla la renderebbe illeggibile. Gli a capo
    scritti nel testo vengono rispettati, le righe vuote no.
    """
    limite = max(int(massimo), 1)
    righe: list[str] = []
    for paragrafo in str(testo).splitlines():
        parole = paragrafo.split()
        if not parole:
            continue
        riga = parole[0]
        for parola in parole[1:]:
            candidata = f"{riga} {parola}"
            if len(candidata) <= limite:
                riga = candidata
                continue
            righe.append(riga)
            riga = parola
        righe.append(riga)
    return tuple(righe)


def accorcia(testo: str, massimo: int) -> str:
    """Accorcia un testo alla lunghezza indicata, segnalandolo con un carattere.

    Serve ai nomi scritti dall'utente (oggetti, gruppi, modifiche): un nome
    lunghissimo non deve allargare o rompere il pannello.
    """
    valore = " ".join(str(testo).split())
    limite = max(int(massimo), 1)
    if len(valore) <= limite:
        return valore
    if limite <= len(SEGNO_ACCORCIATO):
        return SEGNO_ACCORCIATO[:limite]
    return f"{valore[: limite - len(SEGNO_ACCORCIATO)].rstrip()}{SEGNO_ACCORCIATO}"
