# PYTHON-ELTT-MODULE-PARITY/ELTT-liquidity-pools/ELTT-launcher.py
#
# Paritätsmodul für die Launcher-Sicht im Liquidity-Pool-Kontext.
# Spiegelt deterministisch die zentrale ELTT-Blockchain-Logik.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.

from ELTT-Blockchain import (  # type: ignore
    Blockchain,
    LiquidityPool,
    Transaction,
    TokenType,
    TokenKind,
    TxKind,
    compute_tx_energy,
)


def create_pool(bc: Blockchain,
                token_x_index: int,
                token_y_index: int,
                lp_token_index: int) -> LiquidityPool:
    """
    Deterministische Erstellung eines Liquidity-Pools.
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


def add_liquidity(bc: Blockchain,
                  pool_index: int,
                  amount_x: float,
                  amount_y: float) -> None:
    """
    Deterministisches Hinzufügen von Liquidität.
    """
    if pool_index < 0 or pool_index >= len(bc.pools):
        return
    pool = bc.pools[pool_index]
    pool.reserve_x += amount_x
    pool.reserve_y += amount_y


def remove_liquidity(bc: Blockchain,
                     pool_index: int,
                     share_x: float,
                     share_y: float) -> None:
    """
    Deterministisches Entfernen von Liquidität.
    """
    if pool_index < 0 or pool_index >= len(bc.pools):
        return
    pool = bc.pools[pool_index]
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
    "Transaction",
    "TokenType",
    "TokenKind",
    "TxKind",
    "compute_tx_energy",
    "create_pool",
    "add_liquidity",
    "remove_liquidity",
    "build_add_liquidity_tx",
    "build_remove_liquidity_tx",
]
