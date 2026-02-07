# PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/ELTT-Blockchain.py
#
# Paritätische Blockchain-Lese-Sicht im Kontext des ELTT-Viewer-Moduls.
# Reine Spiegelung, keine Mutationen, keine Validierung, keine STATE-Schreiboperationen.
# JSON-kompatible Ausgaben, deterministische Struktur.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from c_parity.chaingrid import build_chain_grid_json


@dataclass(frozen=True)
class BlockchainViewerSnapshot:
    """
    JSON-kompatible Spiegelung der Blockchain-Sicht aus Perspektive des ELTT-Viewer-Moduls.
    """
    chains: List[Mapping[str, Any]]

    def to_json(self) -> Dict[str, Any]:
        return {
            "chains": list(self.chains),
        }


def build_blockchain_viewer_snapshot(
    portfolio: Any,
    max_chains: int = 64,
) -> BlockchainViewerSnapshot:
    """
    Erzeugt einen reinen Lese-Snapshot der Blockchain-Sicht.
    Parität zur Struktur von ELTT-Viewer.c / ELTT-Viewer.json.
    """
    chains_json = build_chain_grid_json(portfolio, max_chains)

    return BlockchainViewerSnapshot(
        chains=chains_json,
    )


def build_blockchain_viewer_snapshot_json(
    portfolio: Any,
    max_chains: int = 64,
) -> Dict[str, Any]:
    """
    JSON-kompatible Variante.
    """
    snapshot = build_blockchain_viewer_snapshot(
        portfolio=portfolio,
        max_chains=max_chains,
    )
    return snapshot.to_json()
