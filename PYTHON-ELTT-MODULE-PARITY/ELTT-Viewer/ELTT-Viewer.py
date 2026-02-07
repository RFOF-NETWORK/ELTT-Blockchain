"""
PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/ELTT-Viewer.py

Master-Viewer – Parität zu ELTT-Viewer.c / eltt_viewer_live_snapshot
- reine Lese-Sichten
- keine Mutationen, keine Validierung, keine STATE-Schreiboperationen
- JSON-kompatible Ausgaben
- vollständig kompatibel mit ELTT-Viewer.json
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping

from c_parity.chaingrid import build_chain_grid_json
from c_parity.tokens_positions import build_token_positions_json
from c_parity.lp_positions import build_lp_positions_json
from c_parity.stakingandpools import build_staking_and_pools_json


# ---------------------------------------------------------------------------
# High-Level Snapshot-Struktur (Parität zu eltt_viewer_live_snapshot)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ViewerSnapshot:
    """
    Logische Entsprechung der JSON-Struktur von ELTT-Viewer.json.
    Alle Felder sind reine Anzeige-Sichten.
    """
    chains: List[Mapping[str, Any]]
    tokens: List[Mapping[str, Any]]
    lp_positions: List[Mapping[str, Any]]
    staking_and_pools: List[Mapping[str, Any]]

    def to_json(self) -> Dict[str, Any]:
        """
        JSON-kompatible Darstellung des gesamten Snapshots.
        """
        return {
            "chains": list(self.chains),
            "tokens": list(self.tokens),
            "lp_positions": list(self.lp_positions),
            "staking_and_pools": list(self.staking_and_pools),
        }


# ---------------------------------------------------------------------------
# Erwartete Portfolio-/State-Schnittstelle (read-only)
# ---------------------------------------------------------------------------
# Erwartet wird ein Objekt `portfolio` mit mindestens:
# - chains / chain_grid-Quelle (für build_chain_grid_json)
# - tokens (für build_token_positions_json)
# - lp_positions (für build_lp_positions_json)
# - staking_and_pools (für build_staking_and_pools_json)
#
# Die genaue interne Struktur wird nicht validiert; es erfolgen nur Lesezugriffe.


def build_viewer_snapshot(
    portfolio: Any,
    max_chains: int = 64,
    max_tokens: int = 256,
    max_lp_positions: int = 256,
    max_staking_and_pools: int = 256,
) -> ViewerSnapshot:
    """
    Parität zu eltt_viewer_live_snapshot (logische Sicht):
    Erzeugt einen vollständigen, reinen Lese-Snapshot für den Viewer.
    """

    chains_json = build_chain_grid_json(portfolio, max_chains)
    tokens_json = build_token_positions_json(portfolio, max_tokens)
    lp_json = build_lp_positions_json(portfolio, max_lp_positions)
    staking_json = build_staking_and_pools_json(portfolio, max_staking_and_pools)

    return ViewerSnapshot(
        chains=chains_json,
        tokens=tokens_json,
        lp_positions=lp_json,
        staking_and_pools=staking_json,
    )


def build_viewer_snapshot_json(
    portfolio: Any,
    max_chains: int = 64,
    max_tokens: int = 256,
    max_lp_positions: int = 256,
    max_staking_and_pools: int = 256,
) -> Dict[str, Any]:
    """
    JSON-kompatible Variante:
    Gibt ein Dict zurück, das direkt mit json.dumps() serialisiert werden kann.
    Parität zur Struktur von ELTT-Viewer.json.
    """
    snapshot = build_viewer_snapshot(
        portfolio=portfolio,
        max_chains=max_chains,
        max_tokens=max_tokens,
        max_lp_positions=max_lp_positions,
        max_staking_and_pools=max_staking_and_pools,
    )
    return snapshot.to_json()
