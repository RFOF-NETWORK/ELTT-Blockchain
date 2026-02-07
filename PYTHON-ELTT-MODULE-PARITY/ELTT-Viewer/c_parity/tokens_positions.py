"""
PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/c_parity/tokens_positions.py

Parität zu: eltt_viewer_build_token_positions in ELTT-Viewer.c
- reine Lese-Sicht auf Token-Positionen
- keine Mutationen, keine Validierung, keine STATE-Schreiboperationen
- JSON-kompatible Ausgabe
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence


# ---------------------------------------------------------------------------
# Datentypen – Parität zu "Token-Position"-Einträgen im C-Viewer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TokenPositionEntry:
    chain_id: int              # z.B. EVM-Chain-ID
    token_address: str         # kanonische Adresse (hex-String)
    symbol: str                # Token-Symbol (z.B. "ELTT")
    decimals: int              # Anzahl Dezimalstellen
    wallet_balance: float      # reine Anzeigegröße
    pool_balance: float        # Anteil in Pools
    total_balance: float       # Summe aus wallet_balance + pool_balance

    def to_json(self) -> Dict[str, Any]:
        """
        JSON-kompatible Darstellung.
        """
        return {
            "chain_id": self.chain_id,
            "token_address": self.token_address,
            "symbol": self.symbol,
            "decimals": self.decimals,
            "wallet_balance": self.wallet_balance,
            "pool_balance": self.pool_balance,
            "total_balance": self.total_balance,
        }


# ---------------------------------------------------------------------------
# Erwartete Portfolio-/State-Schnittstelle (read-only)
# ---------------------------------------------------------------------------
# Erwartet wird ein Objekt `portfolio` mit:
# - Attribut `tokens`: Sequence[TokenLike]
# - jedes TokenLike-Objekt hat:
#     - chain_id: int
#     - address: str
#     - symbol: str
#     - decimals: int
#     - wallet_balance: float
#     - pool_balance: float
#
# Es werden ausschließlich Lesezugriffe durchgeführt.


def build_token_positions(portfolio: Any, max_entries: int) -> List[TokenPositionEntry]:
    """
    Parität zu:
        eltt_viewer_build_token_positions(
            const eltt_portfolio *pf,
            eltt_token_position_entry *out_entries,
            size_t max_entries
        );
    """
    tokens: Sequence[Any] = getattr(portfolio, "tokens", [])
    count = min(len(tokens), max_entries)

    entries: List[TokenPositionEntry] = []
    for i in range(count):
        t = tokens[i]

        wallet_balance = float(getattr(t, "wallet_balance", 0.0))
        pool_balance = float(getattr(t, "pool_balance", 0.0))
        total_balance = wallet_balance + pool_balance

        entry = TokenPositionEntry(
            chain_id=int(getattr(t, "chain_id")),
            token_address=str(getattr(t, "address")),
            symbol=str(getattr(t, "symbol")),
            decimals=int(getattr(t, "decimals")),
            wallet_balance=wallet_balance,
            pool_balance=pool_balance,
            total_balance=total_balance,
        )
        entries.append(entry)

    return entries


def build_token_positions_json(
    portfolio: Any,
    max_entries: int,
) -> List[Mapping[str, Any]]:
    """
    JSON-kompatible Variante.
    """
    return [entry.to_json() for entry in build_token_positions(portfolio, max_entries)]
