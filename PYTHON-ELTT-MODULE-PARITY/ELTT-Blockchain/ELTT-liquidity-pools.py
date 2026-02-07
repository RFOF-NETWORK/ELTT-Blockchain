# PYTHON-ELTT-MODULE-PARITY/ELTT-Blockchain/ELTT-liquidity-pools.py
#
# Paritätsmodul für die Liquidity-Pool-Sicht der ELTT-Blockchain.
# Diese Datei stellt die deterministische Pool- und LP-Token-Logik
# als Perspektive auf die zentrale Blockchain-Implementierung dar.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.
# Logik ist identisch zur zentralen ELTT-Blockchain.py.

from ELTT-Blockchain import (  # type: ignore
    Blockchain,
    LiquidityPool,
    TokenType,
    TokenKind,
    Transaction,
    TxKind,
    compute_tx_energy,
)


def create_pool(bc: Blockchain,
                token_x_index: int,
                token_y_index: int,
                lp_token_index: int) -> LiquidityPool:
    """
    Deterministische Erstellung eines Liquidity-Pools.
    Der LP-Token-Typ muss bereits in bc.token_types existieren.
    """
    pool = LiquidityPool(
        token_x_index=token_x_index,
        token_y_index=token_y_index,
        reserve_x=0.0,
        reserve_y=0.0,
        lp_token_index=lp_token_index,
    )
    bc.pools.append(pool)
    return pool


def get_pool(bc: Blockchain, pool_index: int) -> LiquidityPool | None:
    """
    Deterministischer Zugriff auf einen Liquidity-Pool.
    """
    if pool_index < 0 or pool_index >= len(bc.pools):
        return None
    return bc.pools[pool_index]


def add_liquidity(bc: Blockchain,
                  pool_index: int,
                  amount_x: float,
                  amount_y: float) -> None:
    """
    Deterministisches Hinzufügen von Liquidität zu einem Pool.
    Die tatsächliche Token-Übertragung erfolgt über Transaktionen
    in der zentralen Blockchain-Logik.
    """
    pool = get_pool(bc, pool_index)
    if pool is None:
        return
    pool.reserve_x += amount_x
    pool.reserve_y += amount_y


def remove_liquidity(bc: Blockchain,
                     pool_index: int,
                     share_x: float,
                     share_y: float) -> None:
    """
    Deterministisches Entfernen von Liquidität aus einem Pool.
    """
    pool = get_pool(bc, pool_index)
    if pool is None:
        return
    pool.reserve_x -= share_x
    pool.reserve_y -= share_y
    if pool.reserve_x < 0.0:
        pool.reserve_x = 0.0
    if pool.reserve_y < 0.0:
        pool.reserve_y = 0.0


def build_add_liquidity_tx(from_address: str,
                           pool_address: str,
                           amount_x: float,
                           token_x_index: int,
                           memo: str = "") -> Transaction:
    """
    Deterministische Erstellung einer Add-Liquidity-Transaktion.
    """
    return Transaction(
        from_address=from_address,
        to_address=pool_address,
        amount=amount_x,
        token_index=token_x_index,
        kind=TxKind.ADD_LIQUIDITY,
        memo=memo[:128],
    )


def build_remove_liquidity_tx(from_address: str,
                              pool_address: str,
                              amount_lp: float,
                              lp_token_index: int,
                              memo: str = "") -> Transaction:
    """
    Deterministische Erstellung einer Remove-Liquidity-Transaktion.
    """
    return Transaction(
        from_address=from_address,
        to_address=pool_address,
        amount=amount_lp,
        token_index=lp_token_index,
        kind=TxKind.REMOVE_LIQUIDITY,
        memo=memo[:128],
    )


__all__ = [
    "Blockchain",
    "LiquidityPool",
    "TokenType",
    "TokenKind",
    "Transaction",
    "TxKind",
    "compute_tx_energy",
    "create_pool",
    "get_pool",
    "add_liquidity",
    "remove_liquidity",
    "build_add_liquidity_tx",
    "build_remove_liquidity_tx",
]
