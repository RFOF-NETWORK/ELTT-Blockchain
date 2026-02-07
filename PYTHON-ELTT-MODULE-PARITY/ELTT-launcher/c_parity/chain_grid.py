"""
PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/c_parity/chain_grid.py

Parität zu: eltt_viewer_build_chain_grid in ELTT-Viewer.c
- reine Lese-Sicht auf die Blockchain
- keine Mutationen, keine Validierung, keine STATE-Schreiboperationen
- JSON-kompatible Ausgabe
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Mapping, Sequence, Dict


# ---------------------------------------------------------------------------
# Datentypen – Parität zu eltt_chain_grid_entry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChainGridEntry:
    index: int          # uint32
    timestamp: int      # uint64
    hash: bytes         # 32 Bytes
    prev_hash: bytes    # 32 Bytes
    tx_count: int       # uint32

    def to_json(self) -> Dict[str, Any]:
        """
        JSON-kompatible Darstellung:
        - hash / prev_hash als hex-String
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "hash": self.hash.hex(),
            "prev_hash": self.prev_hash.hex(),
            "tx_count": self.tx_count,
        }


# ---------------------------------------------------------------------------
# Erwartete Blockchain-Schnittstelle (read-only)
# ---------------------------------------------------------------------------
# Erwartet wird ein Objekt `blockchain` mit:
# - Attribut `blocks`: Sequence[Block]
# - jeder Block hat:
#     - index: int
#     - timestamp: int
#     - hash: bytes (32)
#     - prev_hash: bytes (32)
#     - txs: Sequence[Any] (nur Länge relevant)
#
# Es werden ausschließlich Lesezugriffe durchgeführt.


def build_chain_grid(blockchain: Any, max_entries: int) -> List[ChainGridEntry]:
    """
    Erzeugt eine Liste von ChainGridEntry-Objekten.

    Parität zu:
        eltt_viewer_build_chain_grid(
            const eltt_blockchain *bc,
            eltt_chain_grid_entry *out_entries,
            size_t max_entries
        );

    - Schneidet bei max_entries ab.
    - Greift nur lesend auf blockchain.blocks zu.
    - Führt keine Validierung durch.
    """
    blocks: Sequence[Any] = getattr(blockchain, "blocks", [])
    count = min(len(blocks), max_entries)

    entries: List[ChainGridEntry] = []
    for i in range(count):
        b = blocks[i]
        entry = ChainGridEntry(
            index=int(getattr(b, "index")),
            timestamp=int(getattr(b, "timestamp")),
            hash=bytes(getattr(b, "hash")),
            prev_hash=bytes(getattr(b, "prev_hash")),
            tx_count=len(getattr(b, "txs", [])),
        )
        entries.append(entry)

    return entries


def build_chain_grid_json(blockchain: Any, max_entries: int) -> List[Mapping[str, Any]]:
    """
    JSON-kompatible Variante:
    Gibt eine Liste von Dicts zurück, direkt serialisierbar mit json.dumps().
    """
    return [entry.to_json() for entry in build_chain_grid(blockchain, max_entries)]
