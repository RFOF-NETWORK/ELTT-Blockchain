# PYTHON-ELTT-MODULE-PARITY/ELTT-Blockchain/ELTT-Blockchain.py
#
# Paritätsmodul für die ELTT-Blockchain-Sicht.
# Diese Datei spiegelt die vollständige Blockchain-Logik,
# indem sie alle Klassen, Funktionen und Konstanten der
# zentralen ELTT-Blockchain-Implementierung importiert
# und unverändert re-exportiert.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.
# Logik ist identisch zur zentralen ELTT-Blockchain.py.

from ELTT-Blockchain import (  # type: ignore
    Blockchain,
    Block,
    Transaction,
    Wallet,
    TokenType,
    LiquidityPool,
    StakingPosition,
    TokenKind,
    TxKind,
    init_blockchain,
    create_genesis,
    append_block,
    compute_tx_energy,
    compute_block_hash,
)

__all__ = [
    "Blockchain",
    "Block",
    "Transaction",
    "Wallet",
    "TokenType",
    "LiquidityPool",
    "StakingPosition",
    "TokenKind",
    "TxKind",
    "init_blockchain",
    "create_genesis",
    "append_block",
    "compute_tx_energy",
    "compute_block_hash",
]
