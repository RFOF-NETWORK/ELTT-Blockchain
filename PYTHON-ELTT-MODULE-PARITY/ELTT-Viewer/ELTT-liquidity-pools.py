# PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/ELTT-liquidity-pools.py
#
# Paritätische Liquidity-Pool-Lese-Sicht im Kontext des ELTT-Viewer-Moduls.
# Reine Spiegelung, keine Mutationen, keine Validierung, keine STATE-Schreiboperationen.
# JSON-kompatible Ausgaben, deterministische Struktur.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from c_parity.lp_positions import build_lp_positions_json
from c_parity.stakingandpools import build_staking_and_pools_json


@dataclass(frozen=True)
class LiquidityPoolsViewerSnapshot:
    """
    JSON-kompatible Spiegelung der Liquidity-Pool-Sicht
    aus Perspektive des ELTT-Viewer-Moduls.
    """
    lp_positions: List[Mapping[str, Any]]
    staking_and_pools: List[Mapping[str, Any]]

    def to_json(self) -> Dict[str, Any]:
        return {
            "lp_positions": list(self.lp_positions),
            "staking_and_pools": list(self.staking_and_pools),
        }


def build_liquidity_pools_viewer_snapshot(
    portfolio: Any,
    max_lp_positions: int = 256,
    max_staking_and_pools: int = 256,
) -> LiquidityPoolsViewerSnapshot:
    """
    Erzeugt einen reinen Lese-Snapshot der Liquidity-Pool-Sicht.
    Parität zur Struktur von ELTT-Viewer.c / ELTT-Viewer.json.
    """
    lp_json = build_lp_positions_json(portfolio, max_lp_positions)
    staking_json = build_staking_and_pools_json(portfolio, max_staking_and_pools)

    return LiquidityPoolsViewerSnapshot(
        lp_positions=lp_json,
        staking_and_pools=staking_json,
    )


def build_liquidity_pools_viewer_snapshot_json(
    portfolio: Any,
    max_lp_positions: int = 256,
    max_staking_and_pools: int = 256,
) -> Dict[str, Any]:
    """
    JSON-kompatible Variante.
    """
    snapshot = build_liquidity_pools_viewer_snapshot(
        portfolio=portfolio,
        max_lp_positions=max_lp_positions,
        max_staking_and_pools=max_staking_and_pools,
    )
    return snapshot.to_json()
