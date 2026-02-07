# PYTHON-ELTT-MODULE-PARITY/ELTT-Blockchain/ELTT-launcher.py
#
# Paritätsmodul für die Launcher/DEX-Sicht der ELTT-Blockchain.
# Diese Datei stellt die deterministische DEX-/Swap-Logik als
# Perspektive auf die zentrale Blockchain-Implementierung dar.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.
# Logik ist identisch zur zentralen ELTT-Blockchain.py.

from ELTT-Blockchain import (  # type: ignore
    Blockchain,
    Transaction,
    LiquidityPool,
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


def add_liquidity(bc: Blockchain,
                  pool_index: int,
                  amount_x: float,
                  amount_y: float) -> None:
    """
    Deterministisches Hinzufügen von Liquidität zu einem Pool.
    Die tatsächliche Token-Übertragung erfolgt über Transaktionen
    in der zentralen Blockchain-Logik.
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
    Deterministisches Entfernen von Liquidität aus einem Pool.
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


def build_swap_tx(from_address: str,
                  to_address: str,
                  amount_in: float,
                  token_in_index: int,
                  token_out_index: int,
                  memo: str = "") -> Transaction:
    """
    Deterministische Erstellung einer Swap-Transaktion.
    Die konkrete Kursberechnung erfolgt deterministisch im Frontend
    und in der zentralen Logik, diese Funktion bildet nur den
    Transaktionstyp ab.
    """
    return Transaction(
        from_address=from_address,
        to_address=to_address,
        amount=amount_in,
        token_index=token_in_index,
        kind=TxKind.SWAP,
        memo=memo[:128],
    )


__all__ = [
    "Blockchain",
    "Transaction",
    "LiquidityPool",
    "TokenType",
    "TokenKind",
    "TxKind",
    "compute_tx_energy",
    "create_pool",
    "add_liquidity",
    "remove_liquidity",
    "build_swap_tx",
]
