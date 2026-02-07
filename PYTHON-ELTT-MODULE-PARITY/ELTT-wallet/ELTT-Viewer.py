"""
PYTHON-ELTT-MODULE-PARITY/ELTT-wallet/ELTT-Viewer.py

Viewer-Sicht aus dem Modul: ELTT-wallet
Parität zur logischen Struktur von ELTT-Viewer.c / ELTT-Viewer.json
- reine Lese-Sichten
- keine Mutationen, keine Validierung, keine STATE-Schreiboperationen
- JSON-kompatible Ausgaben
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from c_parity.chaingrid import build_chain_grid_json
from c_parity.tokens_positions import build_token_positions_json
from c_parity.lp_positions import build_lp_positions_json
from c_parity.stakingandpools import build_staking_and_pools_json


@dataclass(frozen=True)
class ViewerSnapshot:
    """
    Logische Entsprechung der JSON-Struktur von ELTT-Viewer.json
    aus Sicht des ELTT-wallet-Moduls.
    """
    chains: List[Mapping[str, Any]]
    tokens: List[Mapping[str, Any]]
    lp_positions: List[Mapping[str, Any]]
    staking_and_pools: List[Mapping[str, Any]]

    def to_json(self) -> Dict[str, Any]:
        return {
            "chains": list(self.chains),
            "tokens": list(self.tokens),
            "lp_positions": list(self.lp_positions),
            "staking_and_pools": list(self.staking_and_pools),
        }


def build_viewer_snapshot(
    portfolio: Any,
    max_chains: int = 64,
    max_tokens: int = 256,
    max_lp_positions: int = 256,
    max_staking_and_pools: int = 256,
) -> ViewerSnapshot:
    """
    Erzeugt einen vollständigen, reinen Lese-Snapshot für das ELTT-wallet-Modul.
    Parität zur Struktur von ELTT-Viewer.c / ELTT-Viewer.json.
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
    """
    snapshot = build_viewer_snapshot(
        portfolio=portfolio,
        max_chains=max_chains,
        max_tokens=max_tokens,
        max_lp_positions=max_lp_positions,
        max_staking_and_pools=max_staking_and_pools,
    )
    return snapshot.to_json()
