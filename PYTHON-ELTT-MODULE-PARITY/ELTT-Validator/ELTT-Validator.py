# ELTT-Validator.py
#
# Zentrale Python-Validator-Schnittstelle für die ELTT-Blockchain.
# Spiegel der C-Referenz ELTT-Validator.c:
# - keine STATE-Mutationen
# - keine UI-Logik
# - reine Konsistenz-/Integritätsprüfung
# - kann von allen Python-Sichten und Parity-Modulen importiert werden

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


ELTT_MAX_TOKEN_SYMBOL_LEN = 16
ELTT_MAX_TOKEN_NAME_LEN = 64
ELTT_MAX_ADDRESS_LEN = 64
ELTT_MAX_MEMO_LEN = 128
ELTT_MAX_TOKEN_TYPES = 64
ELTT_MAX_TX_PER_BLOCK = 256
ELTT_MAX_WALLETS = 1024
ELTT_MAX_POOLS = 256
ELTT_MAX_STAKES = 1024


class TokenKind(Enum):
    TTTC = "TTTC"
    ELTT = "ELTT"
    ELTC = "ELTC"
    GENERIC = "GENERIC"
    LP = "LP"


@dataclass(frozen=True)
class TokenType:
    name: str
    symbol: str
    decimals: int
    kind: TokenKind
    energy_binding_factor: float


@dataclass(frozen=True)
class Wallet:
    address: str
    token_count: int
    tokens: List[TokenType]
    balances: List[float]


class TxKind(Enum):
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


@dataclass(frozen=True)
class Transaction:
    from_address: str
    to_address: str
    amount: float
    token_index: int
    kind: TxKind
    memo: str


@dataclass(frozen=True)
class Block:
    index: int
    timestamp: int
    prev_hash: bytes
    hash: bytes
    txs: List[Transaction]


@dataclass(frozen=True)
class LiquidityPool:
    token_x_index: int
    token_y_index: int
    reserve_x: float
    reserve_y: float
    lp_token_index: int


@dataclass(frozen=True)
class StakingPosition:
    owner: str
    token_index: int
    amount: float
    start_timestamp: int
    lock_until: int
    accumulated_rewards: float


@dataclass(frozen=True)
class BlockchainState:
    blocks: List[Block]
    wallets: List[Wallet]
    token_types: List[TokenType]
    pools: List[LiquidityPool]
    stakes: List[StakingPosition]


class ValidatorError(Enum):
    OK = "OK"

    NULL_BLOCKCHAIN = "NULL_BLOCKCHAIN"
    NO_BLOCKS = "NO_BLOCKS"

    GENESIS_PREV_HASH = "GENESIS_PREV_HASH"
    BLOCK_INDEX_SEQUENCE = "BLOCK_INDEX_SEQUENCE"
    BLOCK_PREV_HASH_MISMATCH = "BLOCK_PREV_HASH_MISMATCH"
    BLOCK_HASH_MISMATCH = "BLOCK_HASH_MISMATCH"
    TIMESTAMP_NON_MONOTONIC = "TIMESTAMP_NON_MONOTONIC"

    TOKEN_SYMBOL_DUPLICATE = "TOKEN_SYMBOL_DUPLICATE"
    WALLET_ADDRESS_INVALID = "WALLET_ADDRESS_INVALID"
    WALLET_BALANCE_NEGATIVE = "WALLET_BALANCE_NEGATIVE"
    POOL_INDEX_INVALID = "POOL_INDEX_INVALID"
    POOL_RESERVE_NEGATIVE = "POOL_RESERVE_NEGATIVE"
    STAKE_OWNER_INVALID = "STAKE_OWNER_INVALID"
    STAKE_AMOUNT_NEGATIVE = "STAKE_AMOUNT_NEGATIVE"
    STAKE_TIME_INCONSISTENT = "STAKE_TIME_INCONSISTENT"

    TX_TOKEN_INDEX_INVALID = "TX_TOKEN_INDEX_INVALID"
    TX_AMOUNT_NEGATIVE = "TX_AMOUNT_NEGATIVE"
    TX_KIND_INVALID = "TX_KIND_INVALID"
    TX_REPLAY_DUPLICATE_IN_BLOCK = "TX_REPLAY_DUPLICATE_IN_BLOCK"

    UNKNOWN = "UNKNOWN"


def _is_address_valid(addr: str) -> bool:
    if addr is None:
        return False
    if len(addr) == 0 or len(addr) >= ELTT_MAX_ADDRESS_LEN:
        return False
    for ch in addr:
        c = ord(ch)
        if c < 32 or c == 127:
            return False
    return True


def _check_token_symbols_unique(state: BlockchainState) -> bool:
    symbols = [t.symbol for t in state.token_types]
    return len(symbols) == len(set(symbols))


def _check_wallets(state: BlockchainState) -> Optional[ValidatorError]:
    for w in state.wallets:
        if not _is_address_valid(w.address):
            return ValidatorError.WALLET_ADDRESS_INVALID
        if w.token_count > len(state.token_types):
            return ValidatorError.TX_TOKEN_INDEX_INVALID
        for bal in w.balances[: w.token_count]:
            if bal < 0.0:
                return ValidatorError.WALLET_BALANCE_NEGATIVE
    return None


def _check_pools(state: BlockchainState) -> Optional[ValidatorError]:
    token_len = len(state.token_types)
    for p in state.pools:
        if p.token_x_index < 0 or p.token_x_index >= token_len:
            return ValidatorError.POOL_INDEX_INVALID
        if p.token_y_index < 0 or p.token_y_index >= token_len:
            return ValidatorError.POOL_INDEX_INVALID
        if p.lp_token_index < 0 or p.lp_token_index >= token_len:
            return ValidatorError.POOL_INDEX_INVALID
        if p.reserve_x < 0.0 or p.reserve_y < 0.0:
            return ValidatorError.POOL_RESERVE_NEGATIVE
    return None


def _check_stakes(state: BlockchainState) -> Optional[ValidatorError]:
    token_len = len(state.token_types)
    for s in state.stakes:
        if not _is_address_valid(s.owner):
            return ValidatorError.STAKE_OWNER_INVALID
        if s.token_index < 0 or s.token_index >= token_len:
            return ValidatorError.TX_TOKEN_INDEX_INVALID
        if s.amount < 0.0:
            return ValidatorError.STAKE_AMOUNT_NEGATIVE
        if s.lock_until < s.start_timestamp:
            return ValidatorError.STAKE_TIME_INCONSISTENT
    return None


def _check_block_transactions(state: BlockchainState, blk: Block) -> Optional[ValidatorError]:
    if len(blk.txs) > ELTT_MAX_TX_PER_BLOCK:
        return ValidatorError.UNKNOWN

    seen_hashes: List[int] = []

    for tx in blk.txs:
        if tx.token_index < 0 or tx.token_index >= len(state.token_types):
            return ValidatorError.TX_TOKEN_INDEX_INVALID
        if tx.amount < 0.0:
            return ValidatorError.TX_AMOUNT_NEGATIVE
        if tx.kind not in TxKind:
            return ValidatorError.TX_KIND_INVALID
        if not _is_address_valid(tx.from_address):
            return ValidatorError.WALLET_ADDRESS_INVALID
        if not _is_address_valid(tx.to_address):
            return ValidatorError.WALLET_ADDRESS_INVALID

        h = hash(
            (
                tx.from_address,
                tx.to_address,
                tx.token_index,
                tx.amount,
                tx.kind.value,
                tx.memo,
            )
        )
        if h in seen_hashes:
            return ValidatorError.TX_REPLAY_DUPLICATE_IN_BLOCK
        seen_hashes.append(h)

    return None


def _check_chain(state: BlockchainState) -> Optional[ValidatorError]:
    if not state.blocks:
        return ValidatorError.NO_BLOCKS

    last_ts = 0

    for i, blk in enumerate(state.blocks):
        if i == 0:
            if blk.prev_hash != b"\x00" * 32:
                return ValidatorError.GENESIS_PREV_HASH
        else:
            prev = state.blocks[i - 1]
            if blk.index != prev.index + 1:
                return ValidatorError.BLOCK_INDEX_SEQUENCE
            if blk.prev_hash != prev.hash:
                return ValidatorError.BLOCK_PREV_HASH_MISMATCH

        if i > 0 and blk.timestamp < last_ts:
            return ValidatorError.TIMESTAMP_NON_MONOTONIC
        last_ts = blk.timestamp

        tx_err = _check_block_transactions(state, blk)
        if tx_err is not None:
            return tx_err

    return None


def validate_blockchain(state: Optional[BlockchainState]) -> ValidatorError:
    """
    Vollständige Blockchain-Prüfung (Python-Spiegel zu eltt_validator_check_blockchain):
    - Struktur
    - Token
    - Wallets
    - Pools
    - Stakes
    - Chain (Blöcke, Timestamps, TXs)
    Keine Mutationen, keine Korrekturen.
    """
    if state is None:
        return ValidatorError.NULL_BLOCKCHAIN

    if not _check_token_symbols_unique(state):
        return ValidatorError.TOKEN_SYMBOL_DUPLICATE

    err = _check_wallets(state)
    if err is not None:
        return err

    err = _check_pools(state)
    if err is not None:
        return err

    err = _check_stakes(state)
    if err is not None:
        return err

    err = _check_chain(state)
    if err is not None:
        return err

    return ValidatorError.OK
