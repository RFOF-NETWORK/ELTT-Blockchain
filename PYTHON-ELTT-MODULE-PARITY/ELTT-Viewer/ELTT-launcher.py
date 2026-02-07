# PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/ELTT-launcher.py
#
# Paritätische Launcher-/DEX-Lese-Sicht im Kontext des ELTT-Viewer-Moduls.
# Reine Spiegelung, keine Mutationen, keine Validierung, keine STATE-Schreiboperationen.
# JSON-kompatible Ausgaben, deterministische Struktur.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from c_parity.tokens_positions import build_token_positions_json
from c_parity.lp_positions import build_lp_positions_json


@dataclass(frozen=True)
class LauncherViewerSnapshot:
    """
    JSON-kompatible Spiegelung der Launcher-/DEX-Sicht
    aus Perspektive des ELTT-Viewer-Moduls.
    """
    tokens: List[Mapping[str, Any]]
    lp_positions: List[Mapping[str, Any]]

    def to_json(self) -> Dict[str, Any]:
        return {
            "tokens": list(self.tokens),
            "lp_positions": list(self.lp_positions),
        }


def build_launcher_viewer_snapshot(
    portfolio: Any,
    max_tokens: int = 256,
    max_lp_positions: int = 256,
) -> LauncherViewerSnapshot:
    """
    Erzeugt einen reinen Lese-Snapshot der Launcher-/DEX-Sicht.
    Parität zur Struktur von ELTT-Viewer.c / ELTT-Viewer.json.
    """
    tokens_json = build_token_positions_json(portfolio, max_tokens)
    lp_json = build_lp_positions_json(portfolio, max_lp_positions)

    return LauncherViewerSnapshot(
        tokens=tokens_json,
        lp_positions=lp_json,
    )


def build_launcher_viewer_snapshot_json(
    portfolio: Any,
    max_tokens: int = 256,
    max_lp_positions: int = 256,
) -> Dict[str, Any]:
    """
    JSON-kompatible Variante.
    """
    snapshot = build_launcher_viewer_snapshot(
        portfolio=portfolio,
        max_tokens=max_tokens,
        max_lp_positions=max_lp_positions,
    )
    return snapshot.to_json()
