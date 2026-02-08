"""
ELTT-Viewer.py

Zweck:
    Python-Viewer-Modul für das ELTT-Projekt.
    Rein lesend (Neutral-Matrix): keine STATE-Mutationen, keine Schreiboperationen auf die Blockchain.
    Dient dazu, Daten aus der ENGINE (ELTT-Blockchain.js / ELTT-Blockchain.py / ELTT-Blockchain.c)
    und ggf. aus Parity-/Validator-Schichten zu lesen, zu aggregieren und für UI/Tools aufzubereiten.

Autor:
    Auto-generated gemäß MASTER-DIRECTIVE.

Erstellungsdatum:
    YYYY-MM-DD (bitte bei Bedarf im Build-/Release-Prozess gesetzt).

Abhängigkeiten (logisch/architektonisch):
    - ELTT-Blockchain.py (lesende Schnittstelle zur Engine/Chain-State)
    - ELTT-Validator.py (optional: lesende Einsicht in Validierungsstatus / Fehler)
    - Parity-Module (Python/C) für konsistente Spiegelung, falls benötigt
    - Keine Schreibzugriffe, keine Mutationen, keine Positiv-Matrix-Logik

Matrix-Rolle:
    Neutral-Matrix (VIEWER) — ausschließlich Lesen, Anzeigen, Aggregieren.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple


# ---------------------------------------------------------------------------
# Datamodelle für lesende Views (Neutral-Matrix)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BlockView:
    """Repräsentation eines Blocks für Anzeigezwecke (rein lesend)."""
    height: int
    hash: str
    previous_hash: str
    timestamp: float
    tx_count: int
    producer: str


@dataclass(frozen=True)
class TransactionView:
    """Repräsentation einer Transaktion für Anzeigezwecke (rein lesend)."""
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    token_symbol: str
    timestamp: float
    status: str  # z.B. "confirmed", "pending", "failed"


@dataclass(frozen=True)
class WalletBalanceView:
    """Rein lesende Sicht auf Wallet-Balances."""
    address: str
    balances: Dict[str, float]  # token_symbol -> amount


@dataclass(frozen=True)
class PoolView:
    """Rein lesende Sicht auf einen Liquidity-Pool."""
    pool_id: str
    token_a: str
    token_b: str
    reserve_a: float
    reserve_b: float
    total_lp_tokens: float
    fee_bps: int


@dataclass(frozen=True)
class StakingPositionView:
    """Rein lesende Sicht auf eine Staking-Position."""
    position_id: str
    staker_address: str
    staked_amount: float
    token_symbol: str
    lock_until: float
    pending_rewards: float
    status: str  # z.B. "active", "unlocking", "closed"


# ---------------------------------------------------------------------------
# Schnittstellen-Adapter (lesend) zur Engine / Blockchain / Pools / Staking
# ---------------------------------------------------------------------------
# WICHTIG:
# - Diese Funktionen sind als reine Lese-Adapter gedacht.
# - Sie dürfen keine Mutationen auslösen.
# - Konkrete Implementierungen hängen von ELTT-Blockchain.py / Parity / Validator ab.
# - Hier werden nur neutrale, lesende Signaturen definiert.
# ---------------------------------------------------------------------------

class EngineReader:
    """
    Lesender Adapter zur Engine (ELTT-Blockchain.py / .js / .c).
    Diese Klasse darf nur lesende Operationen ausführen.
    """

    def __init__(self, engine_client: Any) -> None:
        """
        engine_client:
            Abstrakte Schnittstelle zur Engine (z.B. RPC-Client, In-Memory-Adapter, etc.).
            Die konkrete Implementierung wird außerhalb dieses Moduls bereitgestellt.
        """
        self._engine_client = engine_client

    def get_latest_blocks(self, limit: int = 20) -> List[BlockView]:
        """Liest die letzten N Blöcke aus der Engine (rein lesend)."""
        raw_blocks = self._engine_client.fetch_latest_blocks(limit=limit)
        return [
            BlockView(
                height=b["height"],
                hash=b["hash"],
                previous_hash=b["previous_hash"],
                timestamp=b["timestamp"],
                tx_count=b["tx_count"],
                producer=b.get("producer", "unknown"),
            )
            for b in raw_blocks
        ]

    def get_block_by_height(self, height: int) -> Optional[BlockView]:
        """Liest einen Block anhand seiner Höhe (rein lesend)."""
        raw = self._engine_client.fetch_block_by_height(height)
        if raw is None:
            return None
        return BlockView(
            height=raw["height"],
            hash=raw["hash"],
            previous_hash=raw["previous_hash"],
            timestamp=raw["timestamp"],
            tx_count=raw["tx_count"],
            producer=raw.get("producer", "unknown"),
        )

    def get_transactions_for_block(self, block_hash: str) -> List[TransactionView]:
        """Liest alle Transaktionen eines Blocks (rein lesend)."""
        raw_txs = self._engine_client.fetch_transactions_by_block_hash(block_hash)
        return [
            TransactionView(
                tx_id=t["tx_id"],
                from_address=t["from"],
                to_address=t["to"],
                amount=t["amount"],
                token_symbol=t["token_symbol"],
                timestamp=t["timestamp"],
                status=t.get("status", "confirmed"),
            )
            for t in raw_txs
        ]

    def get_wallet_balances(self, address: str) -> WalletBalanceView:
        """Liest die Balances eines Wallets (rein lesend)."""
        raw_balances = self._engine_client.fetch_wallet_balances(address)
        return WalletBalanceView(
            address=address,
            balances=dict(raw_balances),
        )


class PoolsReader:
    """
    Lesender Adapter für Liquidity-Pools.
    Neutral-Matrix: keine Mutationen, nur Anzeige/Aggregation.
    """

    def __init__(self, pools_client: Any) -> None:
        self._pools_client = pools_client

    def list_pools(self) -> List[PoolView]:
        """Liest alle Pools (rein lesend)."""
        raw_pools = self._pools_client.fetch_all_pools()
        return [
            PoolView(
                pool_id=p["pool_id"],
                token_a=p["token_a"],
                token_b=p["token_b"],
                reserve_a=p["reserve_a"],
                reserve_b=p["reserve_b"],
                total_lp_tokens=p["total_lp_tokens"],
                fee_bps=p["fee_bps"],
            )
            for p in raw_pools
        ]

    def get_pool(self, pool_id: str) -> Optional[PoolView]:
        """Liest einen spezifischen Pool (rein lesend)."""
        raw = self._pools_client.fetch_pool(pool_id)
        if raw is None:
            return None
        return PoolView(
                pool_id=raw["pool_id"],
                token_a=raw["token_a"],
                token_b=raw["token_b"],
                reserve_a=raw["reserve_a"],
                reserve_b=raw["reserve_b"],
                total_lp_tokens=raw["total_lp_tokens"],
                fee_bps=raw["fee_bps"],
        )


class StakingReader:
    """
    Lesender Adapter für Staking-Informationen.
    Neutral-Matrix: keine Mutationen, nur Anzeige/Aggregation.
    """

    def __init__(self, staking_client: Any) -> None:
        self._staking_client = staking_client

    def list_positions_for_address(self, address: str) -> List[StakingPositionView]:
        """Liest alle Staking-Positionen eines Adressaten (rein lesend)."""
        raw_positions = self._staking_client.fetch_positions_by_address(address)
        return [
            StakingPositionView(
                position_id=p["position_id"],
                staker_address=p["staker_address"],
                staked_amount=p["staked_amount"],
                token_symbol=p["token_symbol"],
                lock_until=p["lock_until"],
                pending_rewards=p["pending_rewards"],
                status=p["status"],
            )
            for p in raw_positions
        ]

    def get_position(self, position_id: str) -> Optional[StakingPositionView]:
        """Liest eine spezifische Staking-Position (rein lesend)."""
        raw = self._staking_client.fetch_position(position_id)
        if raw is None:
            return None
        return StakingPositionView(
            position_id=raw["position_id"],
            staker_address=raw["staker_address"],
            staked_amount=raw["staked_amount"],
            token_symbol=raw["token_symbol"],
            lock_until=raw["lock_until"],
            pending_rewards=raw["pending_rewards"],
            status=raw["status"],
        )


# ---------------------------------------------------------------------------
# Aggregations- und View-Funktionen für UI / Tools (Neutral-Matrix)
# ---------------------------------------------------------------------------

def build_wallet_overview(
    engine_reader: EngineReader,
    pools_reader: PoolsReader,
    staking_reader: StakingReader,
    address: str,
) -> Dict[str, Any]:
    """
    Baut eine rein lesende Übersicht für ein Wallet:
    - Balances
    - Liquidity-Pool-Beteiligungen (optional, falls über Pools ableitbar)
    - Staking-Positionen

    Keine Mutationen, keine Schreibzugriffe.
    """
    balances_view = engine_reader.get_wallet_balances(address)
    staking_positions = staking_reader.list_positions_for_address(address)

    # Pools können optional über andere Module/Heuristiken zugeordnet werden.
    # Hier nur ein neutraler Platzhalter für spätere Erweiterung.
    pools_summary: List[Dict[str, Any]] = []

    return {
        "address": balances_view.address,
        "balances": balances_view.balances,
        "staking_positions": [
            {
                "position_id": p.position_id,
                "token_symbol": p.token_symbol,
                "staked_amount": p.staked_amount,
                "pending_rewards": p.pending_rewards,
                "status": p.status,
                "lock_until": p.lock_until,
            }
            for p in staking_positions
        ],
        "pools": pools_summary,
    }


def build_block_explorer_view(
    engine_reader: EngineReader,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Baut eine rein lesende Übersicht für einen einfachen Block-Explorer:
    - Letzte N Blöcke
    - Metadaten pro Block
    - Anzahl Transaktionen pro Block

    Keine Mutationen, keine Schreibzugriffe.
    """
    blocks = engine_reader.get_latest_blocks(limit=limit)
    return {
        "blocks": [
            {
                "height": b.height,
                "hash": b.hash,
                "previous_hash": b.previous_hash,
                "timestamp": b.timestamp,
                "tx_count": b.tx_count,
                "producer": b.producer,
            }
            for b in blocks
        ]
    }


def build_block_detail_view(
    engine_reader: EngineReader,
    block_height: int,
) -> Optional[Dict[str, Any]]:
    """
    Baut eine rein lesende Detailansicht für einen Block:
    - Block-Metadaten
    - Transaktionen im Block

    Keine Mutationen, keine Schreibzugriffe.
    """
    block = engine_reader.get_block_by_height(block_height)
    if block is None:
        return None

    txs = engine_reader.get_transactions_for_block(block.hash)
    return {
        "block": {
            "height": block.height,
            "hash": block.hash,
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp,
            "tx_count": block.tx_count,
            "producer": block.producer,
        },
        "transactions": [
            {
                "tx_id": t.tx_id,
                "from": t.from_address,
                "to": t.to_address,
                "amount": t.amount,
                "token_symbol": t.token_symbol,
                "timestamp": t.timestamp,
                "status": t.status,
            }
            for t in txs
        ],
    }


# ---------------------------------------------------------------------------
# Hinweis:
# - Dieses Modul implementiert ausschließlich Neutral-Matrix-Logik (VIEWER).
# - Alle Funktionen sind rein lesend.
# - Mutationen, State-Änderungen oder Positiv-Matrix-Operationen sind hier verboten.
# - Validierungslogik (Negativ-Matrix) gehört in ELTT-Validator.c / ELTT-Validator.py.
# - Positiv-Matrix-Quelle bleibt die ENGINE (ELTT-Blockchain.js / .py / .c).
# ---------------------------------------------------------------------------
