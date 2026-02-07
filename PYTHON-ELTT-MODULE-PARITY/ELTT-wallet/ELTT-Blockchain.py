# PYTHON-ELTT-MODULE-PARITY/ELTT-wallet/ELTT-Blockchain.py

"""
Paritätisches Blockchain-Modul im Kontext der ELTT-Wallet-Sicht.
Deterministische, auditierbare und souveränitätsfokussierte Spiegelung der
Blockchain-Grundstruktur für Wallet-bezogene Operationen.

Die Owner-Wallet entsteht ausschließlich im Frontend, ist die einzige Genesis-Wallet,
besitzt TTTC, ELTT und ELTC, erzeugt Block 2 autonom und ist Ursprung aller Extensions.
Dieses Modul speichert keine Seeds und keine privaten Schlüssel und erzeugt keine
Genesis-Logik, sondern spiegelt nur einen bereits bestehenden Zustand.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import copy


@dataclass
class TransactionParity:
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    token_index: int
    kind: str
    memo: str
    energy: float


@dataclass
class BlockParity:
    index: int
    timestamp: str
    prev_hash: str
    hash: str
    transactions: List[TransactionParity] = field(default_factory=list)


@dataclass
class TokenTypeParity:
    index: int
    symbol: str
    name: str
    kind: str  # z.B. "NATIVE"


@dataclass
class BlockchainStateParity:
    blocks: List[BlockParity] = field(default_factory=list)
    tokens: List[TokenTypeParity] = field(default_factory=list)


class ELTTBlockchainParityForWallet:
    """
    Paritätische Blockchain-Sicht, wie sie aus Wallet-Perspektive benötigt wird.
    Keine Genesis-Erzeugung, keine Schlüsselverwaltung, nur deterministische Spiegelung.
    """

    def __init__(self) -> None:
        self._state: BlockchainStateParity = BlockchainStateParity()

    # -------------------------------------------------------------------------
    # Zustand setzen / holen
    # -------------------------------------------------------------------------

    def set_blockchain_state(self, state: BlockchainStateParity) -> None:
        """
        Setzt den vollständigen Blockchain-Zustand deterministisch.
        Erwartet eine bereits berechnete, vertrauenswürdige Spiegelung.
        """
        self._state = copy.deepcopy(state)

    def get_blockchain_state(self) -> BlockchainStateParity:
        """
        Liefert eine tiefe Kopie des aktuellen Blockchain-Zustands.
        """
        return copy.deepcopy(self._state)

    # -------------------------------------------------------------------------
    # Blöcke
    # -------------------------------------------------------------------------

    def get_block_by_index(self, index: int) -> Optional[BlockParity]:
        """
        Liefert einen Block anhand seines Index, falls vorhanden.
        """
        for b in self._state.blocks:
            if b.index == index:
                return copy.deepcopy(b)
        return None

    def list_blocks(self) -> List[BlockParity]:
        """
        Liefert eine Liste aller Blöcke in deterministischer Reihenfolge.
        """
        return copy.deepcopy(self._state.blocks)

    # -------------------------------------------------------------------------
    # Token-Typen
    # -------------------------------------------------------------------------

    def list_token_types(self) -> List[TokenTypeParity]:
        """
        Liefert alle bekannten Token-Typen (TTTC, ELTT, ELTC, …).
        """
        return copy.deepcopy(self._state.tokens)

    def get_token_type_by_index(self, index: int) -> Optional[TokenTypeParity]:
        """
        Liefert einen Token-Typ anhand seines Index.
        """
        for t in self._state.tokens:
            if t.index == index:
                return copy.deepcopy(t)
        return None

    # -------------------------------------------------------------------------
    # Export / Import
    # -------------------------------------------------------------------------

    def export_state(self) -> Dict[str, Any]:
        """
        Exportiert den Blockchain-Zustand deterministisch.
        Enthält keine Seeds, keine privaten Schlüssel und keine Genesis-Logik.
        """
        data: Dict[str, Any] = {
            "blocks": [],
            "tokens": [],
        }

        for b in self._state.blocks:
            data["blocks"].append(
                {
                    "index": b.index,
                    "timestamp": b.timestamp,
                    "prev_hash": b.prev_hash,
                    "hash": b.hash,
                    "transactions": [
                        {
                            "tx_id": tx.tx_id,
                            "from_address": tx.from_address,
                            "to_address": tx.to_address,
                            "amount": tx.amount,
                            "token_index": tx.token_index,
                            "kind": tx.kind,
                            "memo": tx.memo,
                            "energy": tx.energy,
                        }
                        for tx in b.transactions
                    ],
                }
            )

        for t in self._state.tokens:
            data["tokens"].append(
                {
                    "index": t.index,
                    "symbol": t.symbol,
                    "name": t.name,
                    "kind": t.kind,
                }
            )

        return data

    def import_state(self, data: Dict[str, Any]) -> None:
        """
        Importiert einen deterministisch erzeugten Blockchain-Zustand.
        Erwartet ein zuvor mit export_state() erzeugtes Objekt.
        """
        if not isinstance(data, dict):
            return

        blocks_raw = data.get("blocks") or []
        tokens_raw = data.get("tokens") or []

        blocks: List[BlockParity] = []
        tokens: List[TokenTypeParity] = []

        for b in blocks_raw:
            try:
                index = int(b.get("index"))
                timestamp = str(b.get("timestamp") or "")
                prev_hash = str(b.get("prev_hash") or "")
                hash_ = str(b.get("hash") or "")
            except (TypeError, ValueError):
                continue

            txs_raw = b.get("transactions") or []
            txs: List[TransactionParity] = []
            for tx in txs_raw:
                try:
                    tx_id = str(tx.get("tx_id") or "")
                    from_address = str(tx.get("from_address") or "")
                    to_address = str(tx.get("to_address") or "")
                    amount = float(tx.get("amount"))
                    token_index = int(tx.get("token_index"))
                    kind = str(tx.get("kind") or "")
                    memo = str(tx.get("memo") or "")
                    energy = float(tx.get("energy"))
                except (TypeError, ValueError):
                    continue
                txs.append(
                    TransactionParity(
                        tx_id=tx_id,
                        from_address=from_address,
                        to_address=to_address,
                        amount=amount,
                        token_index=token_index,
                        kind=kind,
                        memo=memo,
                        energy=energy,
                    )
                )

            blocks.append(
                BlockParity(
                    index=index,
                    timestamp=timestamp,
                    prev_hash=prev_hash,
                    hash=hash_,
                    transactions=txs,
                )
            )

        for t in tokens_raw:
            try:
                index = int(t.get("index"))
                symbol = str(t.get("symbol") or "")
                name = str(t.get("name") or "")
                kind = str(t.get("kind") or "")
            except (TypeError, ValueError):
                continue
            tokens.append(
                TokenTypeParity(
                    index=index,
                    symbol=symbol,
                    name=name,
                    kind=kind,
                )
            )

        self._state = BlockchainStateParity(blocks=blocks, tokens=tokens)


# Globale, paritätische Instanz für Wallet-bezogene Blockchain-Sicht
blockchain_parity_for_wallet = ELTTBlockchainParityForWallet()
