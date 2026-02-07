"""
PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/c_parity/lp_positions.py

Parität zu: eltt_viewer_build_lp_positions in ELTT-Viewer.c
- reine Lese-Sicht auf Liquidity-Positionen (LPs)
- keine Mutationen, keine Validierung, keine STATE-Schreiboperationen
- JSON-kompatible Ausgabe
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence


# ---------------------------------------------------------------------------
# Datentypen – Parität zu "LP-Position"-Einträgen im C-Viewer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LPPositionEntry:
    chain_id: int              # z.B. EVM-Chain-ID
    pool_address: str          # Adresse des Pools (hex-String)
    token0_symbol: str         # Symbol Token0
    token1_symbol: str         # Symbol Token1
    share_percent: float       # Anteil des Users am Pool in %
    amount_token0: float       # rechnerischer Anteil Token0
    amount_token1: float       # rechnerischer Anteil Token1
    total_value: float         # Gesamtwert in Referenzwährung (Anzeigegröße)

    def to_json(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "pool_address": self.pool_address,
            "token0_symbol": self.token0_symbol,
            "token1_symbol": self.token1_symbol,
            "share_percent": self.share_percent,
            "amount_token0": self.amount_token0,
            "amount_token1": self.amount_token1,
            "total_value": self.total_value,
        }


# ---------------------------------------------------------------------------
# Erwartete Portfolio-/State-Schnittstelle (read-only)
# ---------------------------------------------------------------------------

def build_lp_positions(portfolio: Any, max_entries: int) -> List[LPPositionEntry]:
    lp_positions: Sequence[Any] = getattr(portfolio, "lp_positions", [])
    count = min(len(lp_positions), max_entries)

    entries: List[LPPositionEntry] = []
    for i in range(count):
        p = lp_positions[i]

        entry = LPPositionEntry(
            chain_id=int(getattr(p, "chain_id")),
            pool_address=str(getattr(p, "pool_address")),
            token0_symbol=str(getattr(p, "token0_symbol")),
            token1_symbol=str(getattr(p, "token1_symbol")),
            share_percent=float(getattr(p, "share_percent", 0.0)),
            amount_token0=float(getattr(p, "amount_token0", 0.0)),
            amount_token1=float(getattr(p, "amount_token1", 0.0)),
            total_value=float(getattr(p, "total_value", 0.0)),
        )
        entries.append(entry)

    return entries


def build_lp_positions_json(
    portfolio: Any,
    max_entries: int,
) -> List[Mapping[str, Any]]:
    return [entry.to_json() for entry in build_lp_positions(portfolio, max_entries)]
