# PYTHON-ELTT-MODULE-PARITY/ELTT-Blockchain/ELTT-wallet.py
#
# Paritätsmodul für die Wallet-Sicht der ELTT-Blockchain.
# Diese Datei stellt die vollständige Wallet-Logik als
# Perspektive auf die zentrale Blockchain-Implementierung dar.
#
# Keine Beispiele, keine Interpretationen, keine Abweichungen.
# Logik ist identisch zur zentralen ELTT-Blockchain.py.

from ELTT-Blockchain import (  # type: ignore
    Blockchain,
    Wallet,
    TokenType,
    TokenKind,
    Transaction,
    TxKind,
    init_blockchain,
    create_genesis,
    append_block,
    compute_tx_energy,
)


def create_wallet(bc: Blockchain, address: str) -> Wallet:
    """
    Deterministische Wallet-Erstellung.
    Die Ableitung der Adresse aus der 12-Wort-Phrase erfolgt ausschließlich im Frontend.
    Diese Funktion stellt nur sicher, dass eine Wallet-Struktur im Blockchain-Zustand existiert.
    """
    for w in bc.wallets:
        if w.address == address:
            return w
    w = Wallet(address=address)
    w.token_count = len(bc.token_types)
    w.tokens = list(bc.token_types)
    w.balances = [0.0 for _ in range(len(bc.token_types))]
    bc.wallets.append(w)
    return w


def get_wallet(bc: Blockchain, address: str) -> Wallet | None:
    """
    Deterministischer Zugriff auf eine Wallet.
    """
    for w in bc.wallets:
        if w.address == address:
            return w
    return None


def list_wallet_tokens(wallet: Wallet) -> list[tuple[TokenType, float]]:
    """
    Deterministische Auflistung aller Token-Bestände einer Wallet.
    """
    result: list[tuple[TokenType, float]] = []
    for t, bal in zip(wallet.tokens, wallet.balances):
        result.append((t, bal))
    return result


def build_transfer_tx(from_address: str,
                      to_address: str,
                      amount: float,
                      token_index: int,
                      memo: str = "") -> Transaction:
    """
    Deterministische Erstellung einer Transfer-Transaktion.
    """
    return Transaction(
        from_address=from_address,
        to_address=to_address,
        amount=amount,
        token_index=token_index,
        kind=TxKind.TRANSFER,
        memo=memo[:128],
    )


__all__ = [
    "Blockchain",
    "Wallet",
    "TokenType",
    "TokenKind",
    "Transaction",
    "TxKind",
    "init_blockchain",
    "create_genesis",
    "append_block",
    "compute_tx_energy",
    "create_wallet",
    "get_wallet",
    "list_wallet_tokens",
    "build_transfer_tx",
]
