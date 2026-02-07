# ELTT-Blockchain.py
#
# Formale, deterministische Referenzimplementierung der ELTT-Blockchain-Logik in Python.
# Keine Beispiele, keine Interpretationen, keine externen Abhängigkeiten.
# Nur Standardbibliothek, vollständig paritätisch zur C-Referenz.
#
# Enthält:
# - Datenstrukturen für Blöcke, Transaktionen, Wallets, Token, LP-Token, Pools, Staking.
# - Deterministische SHA-256-Hashing-Logik.
# - SI-Byte-System und binäres Byte-System als normative Tabellen.
# - Energie-Formel E(TX) = SI_Byte_Wert(TX) + Binär_Byte_Wert(TX) + (SHA256(TX_Daten) mod 1).
# - Deterministische Blockchain-Operationen (Genesis, Blöcke, Transaktionen, Validierung).
#
# Die Owner-Wallet, Genesis-Wallet, Phrasen und konkrete Initialzustände
# werden ausschließlich im Frontend bestimmt und hier nicht fest verdrahtet.

from __future__ import annotations
import hashlib
import struct
from dataclasses import dataclass, field
from typing import List, Optional


# ----------------------------------------------------------
# Konstanten und Limits (paritätisch zu C)
# ----------------------------------------------------------

ELTT_MAX_TOKEN_SYMBOL_LEN = 16
ELTT_MAX_TOKEN_NAME_LEN = 64
ELTT_MAX_ADDRESS_LEN = 64
ELTT_MAX_MEMO_LEN = 128
ELTT_MAX_TOKEN_TYPES = 64
ELTT_MAX_TX_PER_BLOCK = 256
ELTT_MAX_WALLETS = 1024
ELTT_MAX_POOLS = 256
ELTT_MAX_STAKES = 1024


# ----------------------------------------------------------
# Byte-Systeme (SI und binär) – normative Tabellen
# ----------------------------------------------------------

@dataclass(frozen=True)
class SIByteUnit:
    name: str
    symbol: str
    power10: float


ELTT_SI_BYTE_TABLE: List[SIByteUnit] = [
    SIByteUnit("Quecto", "qB", 1e-30),
    SIByteUnit("Ronto",  "rB", 1e-27),
    SIByteUnit("Yocto",  "yB", 1e-24),
    SIByteUnit("Zepto",  "zB", 1e-21),
    SIByteUnit("Atto",   "aB", 1e-18),
    SIByteUnit("Femto",  "fB", 1e-15),
    SIByteUnit("Pico",   "pB", 1e-12),
    SIByteUnit("Nano",   "nB", 1e-9),
    SIByteUnit("Mikro",  "µB", 1e-6),
    SIByteUnit("Milli",  "mB", 1e-3),
    SIByteUnit("Zenti",  "cB", 1e-2),
    SIByteUnit("Dezi",   "dB", 1e-1),
    SIByteUnit("Byte",   "B",  1e0),
    SIByteUnit("Deka",   "daB",1e1),
    SIByteUnit("Hekto",  "hB", 1e2),
    SIByteUnit("Kilo",   "kB", 1e3),
    SIByteUnit("Mega",   "MB", 1e6),
    SIByteUnit("Giga",   "GB", 1e9),
    SIByteUnit("Tera",   "TB", 1e12),
    SIByteUnit("Peta",   "PB", 1e15),
    SIByteUnit("Exa",    "EB", 1e18),
    SIByteUnit("Zetta",  "ZB", 1e21),
    SIByteUnit("Yotta",  "YB", 1e24),
    SIByteUnit("Quetta", "QB", 1e30),
]


@dataclass(frozen=True)
class BinaryByteUnit:
    name: str
    symbol: str
    power2: int
    approx_bytes: float


ELTT_BINARY_BYTE_TABLE: List[BinaryByteUnit] = [
    BinaryByteUnit("Quectibyte", "QiB",   0,   1.0),
    BinaryByteUnit("Rontibyte",  "RiB",  10,   1024.0),
    BinaryByteUnit("Yoctibyte",  "YiB",  20,   1048576.0),
    BinaryByteUnit("Zeptibyte",  "ZiB",  30,   1073741824.0),
    BinaryByteUnit("Attibyte",   "AiB",  40,   1099511627776.0),
    BinaryByteUnit("Femtoibyte", "FiB",  50,   1125899906842624.0),
    BinaryByteUnit("Picoibyte",  "PiB",  60,   1152921504606846976.0),
    BinaryByteUnit("Nanoibyte",  "NiB",  70,   1180591620717411303424.0),
    BinaryByteUnit("Microibyte", "µiB",  80,   1208925819614629174706176.0),
    BinaryByteUnit("Millibyte",  "miB",  90,   1.237e27),
    BinaryByteUnit("Centibyte",  "ciB", 100,   1.267e30),
    BinaryByteUnit("Decibyte",   "diB", 110,   1.298e33),
    BinaryByteUnit("Byte",       "B",   120,   1.330e36),
    BinaryByteUnit("Dekibyte",   "daiB",130,   1.363e39),
    BinaryByteUnit("Hektibyte",  "hiB", 140,   1.398e42),
    BinaryByteUnit("Kilobibyte", "KiB", 150,   1.433e45),
    BinaryByteUnit("Megabibyte", "MiB", 160,   1.470e48),
    BinaryByteUnit("Gigabibyte", "GiB", 170,   1.508e51),
    BinaryByteUnit("Terabibyte", "TiB", 180,   1.547e54),
    BinaryByteUnit("Petabibyte", "PiBiB",190,  1.587e57),
    BinaryByteUnit("Exbibibyte", "EiBiB",200,  1.628e60),
    BinaryByteUnit("Zebbibyte",  "ZiBiB",210,  1.670e63),
    BinaryByteUnit("Yobbibyte",  "YiBiB",220,  1.713e66),
    BinaryByteUnit("Quettibyte", "QiBiB",230,  1.757e69),
]


def _si_byte_value_from_size(size: int) -> float:
    if size <= 0:
        return 0.0
    return float(size)


def _binary_byte_value_from_size(size: int) -> float:
    if size <= 0:
        return 0.0
    return float(size)


# ----------------------------------------------------------
# Kern-Datenstrukturen
# ----------------------------------------------------------

class TokenKind:
    TTTC = "TTTC"
    ELTT = "ELTT"
    ELTC = "ELTC"
    GENERIC = "GENERIC"
    LP = "LP"


@dataclass
class TokenType:
    name: str
    symbol: str
    decimals: int
    kind: str
    energy_binding_factor: float


@dataclass
class Wallet:
    address: str
    token_count: int = 0
    tokens: List[TokenType] = field(default_factory=list)
    balances: List[float] = field(default_factory=list)


class TxKind:
    TRANSFER = "TRANSFER"
    MINT = "MINT"
    BURN = "BURN"
    CREATE_TOKEN = "CREATE_TOKEN"
    CREATE_POOL = "CREATE_POOL"
    ADD_LIQUIDITY = "ADD_LIQUIDITY"
    REMOVE_LIQUIDITY = "REMOVE_LIQUIDITY"
    STAKE = "STAKE"
    UNSTAKE = "UNSTAKE"
    CLAIM_REWARDS = "CLAIM_REWARDS"
    SWAP = "SWAP"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    GOVERNANCE_PROPOSAL = "GOVERNANCE_PROPOSAL"


@dataclass
class Transaction:
    from_address: str
    to_address: str
    amount: float
    token_index: int
    kind: str
    memo: str = ""


@dataclass
class Block:
    index: int
    timestamp: int
    prev_hash: bytes
    hash: bytes
    txs: List[Transaction] = field(default_factory=list)


@dataclass
class LiquidityPool:
    token_x_index: int
    token_y_index: int
    reserve_x: float
    reserve_y: float
    lp_token_index: int


@dataclass
class StakingPosition:
    owner: str
    token_index: int
    amount: float
    start_timestamp: int
    lock_until: int
    accumulated_rewards: float


@dataclass
class Blockchain:
    blocks: List[Block] = field(default_factory=list)
    wallets: List[Wallet] = field(default_factory=list)
    token_types: List[TokenType] = field(default_factory=list)
    pools: List[LiquidityPool] = field(default_factory=list)
    stakes: List[StakingPosition] = field(default_factory=list)


# ----------------------------------------------------------
# Hashing und Serialisierung
# ----------------------------------------------------------

def _serialize_transaction(tx: Transaction) -> bytes:
    from_bytes = tx.from_address.encode("utf-8") + b"\x00"
    to_bytes = tx.to_address.encode("utf-8") + b"\x00"
    memo_bytes = tx.memo.encode("utf-8") + b"\x00"
    data = b"".join([
        from_bytes,
        to_bytes,
        struct.pack("!d", float(tx.amount)),
        struct.pack("!i", int(tx.token_index)),
        struct.pack("!i", {
            TxKind.TRANSFER: 0,
            TxKind.MINT: 1,
            TxKind.BURN: 2,
            TxKind.CREATE_TOKEN: 3,
            TxKind.CREATE_POOL: 4,
            TxKind.ADD_LIQUIDITY: 5,
            TxKind.REMOVE_LIQUIDITY: 6,
            TxKind.STAKE: 7,
            TxKind.UNSTAKE: 8,
            TxKind.CLAIM_REWARDS: 9,
            TxKind.SWAP: 10,
            TxKind.PROFILE_UPDATE: 11,
            TxKind.GOVERNANCE_PROPOSAL: 12,
        }[tx.kind]),
        memo_bytes,
    ])
    return data


def _serialize_block_header(block: Block) -> bytes:
    return b"".join([
        struct.pack("!I", block.index),
        struct.pack("!Q", block.timestamp),
        block.prev_hash,
        struct.pack("!Q", len(block.txs)),
    ])


def compute_block_hash(block: Block) -> bytes:
    header = _serialize_block_header(block)
    return hashlib.sha256(header).digest()


# ----------------------------------------------------------
# Energie-Formel
# ----------------------------------------------------------

def compute_tx_energy(tx: Transaction) -> float:
    serialized = _serialize_transaction(tx)
    si_value = _si_byte_value_from_size(len(serialized))
    bin_value = _binary_byte_value_from_size(len(serialized))
    h = hashlib.sha256(serialized).digest()
    last8 = int.from_bytes(h[24:32], "big")
    frac = (last8 % 1_000_000_000) / 1_000_000_000.0
    return si_value + bin_value + frac


# ----------------------------------------------------------
# Wallet- und Token-Logik
# ----------------------------------------------------------

def _find_wallet_index(bc: Blockchain, address: str) -> int:
    for i, w in enumerate(bc.wallets):
        if w.address == address:
            return i
    return -1


def _add_wallet(bc: Blockchain, address: str) -> int:
    if len(bc.wallets) >= ELTT_MAX_WALLETS:
        return -1
    w = Wallet(address=address)
    w.token_count = len(bc.token_types)
    w.tokens = list(bc.token_types)
    w.balances = [0.0 for _ in range(len(bc.token_types))]
    bc.wallets.append(w)
    return len(bc.wallets) - 1


def _find_or_create_wallet(bc: Blockchain, address: str) -> int:
    idx = _find_wallet_index(bc, address)
    if idx >= 0:
        return idx
    return _add_wallet(bc, address)


def add_token_type(bc: Blockchain,
                   name: str,
                   symbol: str,
                   decimals: int,
                   kind: str,
                   energy_binding_factor: float) -> int:
    if len(bc.token_types) >= ELTT_MAX_TOKEN_TYPES:
        return -1
    t = TokenType(
        name=name[:ELTT_MAX_TOKEN_NAME_LEN],
        symbol=symbol[:ELTT_MAX_TOKEN_SYMBOL_LEN],
        decimals=decimals,
        kind=kind,
        energy_binding_factor=energy_binding_factor,
    )
    bc.token_types.append(t)
    for w in bc.wallets:
        w.tokens = list(bc.token_types)
        w.balances.append(0.0)
        w.token_count = len(bc.token_types)
    return len(bc.token_types) - 1


# ----------------------------------------------------------
# Transaktionsvalidierung und Anwendung
# ----------------------------------------------------------

def _validate_transaction(bc: Blockchain, tx: Transaction) -> bool:
    if tx.token_index < 0 or tx.token_index >= len(bc.token_types):
        return False
    if tx.amount < 0.0:
        return False

    from_idx = _find_wallet_index(bc, tx.from_address)
    to_idx = _find_wallet_index(bc, tx.to_address)

    if tx.kind in (TxKind.TRANSFER, TxKind.SWAP, TxKind.STAKE):
        if from_idx < 0:
            return False
        if bc.wallets[from_idx].balances[tx.token_index] < tx.amount:
            return False
        if tx.amount <= 0.0:
            return False
    elif tx.kind == TxKind.MINT:
        if to_idx < 0:
            return False
        if tx.amount <= 0.0:
            return False
    elif tx.kind == TxKind.BURN:
        if from_idx < 0:
            return False
        if bc.wallets[from_idx].balances[tx.token_index] < tx.amount:
            return False
        if tx.amount <= 0.0:
            return False
    else:
        pass

    return True


def _apply_transaction(bc: Blockchain, tx: Transaction) -> None:
    from_idx = _find_or_create_wallet(bc, tx.from_address)
    to_idx = _find_or_create_wallet(bc, tx.to_address)

    if tx.kind in (TxKind.TRANSFER, TxKind.SWAP):
        bc.wallets[from_idx].balances[tx.token_index] -= tx.amount
        bc.wallets[to_idx].balances[tx.token_index] += tx.amount
    elif tx.kind == TxKind.MINT:
        bc.wallets[to_idx].balances[tx.token_index] += tx.amount
    elif tx.kind == TxKind.BURN:
        bc.wallets[from_idx].balances[tx.token_index] -= tx.amount
    else:
        pass


# ----------------------------------------------------------
# Block-Validierung und Chain-Aufbau
# ----------------------------------------------------------

def _validate_block(bc: Blockchain, block: Block) -> bool:
    if block.index == 0:
        if block.prev_hash != b"\x00" * 32:
            return False
    else:
        if not bc.blocks:
            return False
        prev = bc.blocks[-1]
        if block.index != prev.index + 1:
            return False
        if block.prev_hash != prev.hash:
            return False

    tmp = Block(
        index=block.index,
        timestamp=block.timestamp,
        prev_hash=block.prev_hash,
        hash=b"",
        txs=list(block.txs),
    )
    tmp.hash = compute_block_hash(tmp)
    if tmp.hash != block.hash:
        return False

    for tx in block.txs:
        if not _validate_transaction(bc, tx):
            return False

    return True


def append_block(bc: Blockchain, block: Block) -> bool:
    if not _validate_block(bc, block):
        return False
    bc.blocks.append(block)
    for tx in block.txs:
        _apply_transaction(bc, tx)
    return True


# ----------------------------------------------------------
# Genesis-Block-Logik (ohne Owner-Hardcoding)
# ----------------------------------------------------------

def init_blockchain() -> Blockchain:
    bc = Blockchain()
    add_token_type(bc, "TTTC", "TTTC", 8, TokenKind.TTTC, 0.75)
    add_token_type(bc, "ELTT", "ELTT", 8, TokenKind.ELTT, 0.75)
    add_token_type(bc, "ELTC", "ELTC", 8, TokenKind.ELTC, 0.75)
    return bc


def build_genesis_block(owner_address: str, timestamp: int) -> Block:
    prev_hash = b"\x00" * 32
    block = Block(
        index=0,
        timestamp=timestamp,
        prev_hash=prev_hash,
        hash=b"",
        txs=[],
    )
    block.hash = compute_block_hash(block)
    return block


def create_genesis(bc: Blockchain, owner_address: str, timestamp: int) -> None:
    genesis = build_genesis_block(owner_address, timestamp)
    append_block(bc, genesis)


# ----------------------------------------------------------
# Öffentliche API
# ----------------------------------------------------------

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
