# PYTHON-ELTT-MODULE-PARITY/ELTT-wallet/ELTT-wallet.py

"""
Paritätisches Wallet-Modul zur ELTT-Blockchain.
Deterministische, auditierbare und souveränitätsfokussierte Spiegelung der Wallet-Logik.
Die Owner-Wallet entsteht ausschließlich im Frontend, ist die einzige Genesis-Wallet,
besitzt TTTC, ELTT und ELTC, erzeugt Block 2 autonom und ist Ursprung aller Extensions.
Dieses Modul speichert keine Seeds und keine privaten Schlüssel.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import copy


@dataclass
class TokenBalance:
    token_index: int
    symbol: str
    amount: float


@dataclass
class WalletState:
    address: str
    balances: List[TokenBalance] = field(default_factory=list)


class ELTTWalletParity:
    """
    Paritätische Wallet-Sicht für die ELTT-Blockchain.
    Diese Klasse spiegelt deterministisch den Wallet-Zustand, ohne Seeds oder Schlüssel zu verwalten.
    """

    def __init__(self) -> None:
        self._current_address: Optional[str] = None
        self._wallets: Dict[str, WalletState] = {}

    # -------------------------------------------------------------------------
    # Souveräne Adresse
    # -------------------------------------------------------------------------

    def set_current_wallet_address(self, address: str) -> None:
        """
        Setzt die aktuelle Wallet-Adresse deterministisch.
        Erzeugt keinen neuen Schlüssel, keine Seed-Phrase und keine Genesis-Logik.
        """
        addr = (address or "").strip()
        if not addr:
            self._current_address = None
            return
        self._current_address = addr
        if addr not in self._wallets:
            self._wallets[addr] = WalletState(address=addr, balances=[])

    def get_current_wallet_address(self) -> Optional[str]:
        """
        Gibt die aktuell gesetzte Wallet-Adresse zurück.
        """
        return self._current_address

    # -------------------------------------------------------------------------
    # Wallet-Zustand
    # -------------------------------------------------------------------------

    def get_wallet_state(self, address: Optional[str] = None) -> Optional[WalletState]:
        """
        Liefert den deterministischen Wallet-Zustand für die angegebene Adresse.
        Wenn keine Adresse übergeben wird, wird die aktuelle Adresse verwendet.
        """
        addr = (address or self._current_address or "").strip()
        if not addr:
            return None
        state = self._wallets.get(addr)
        if state is None:
            return None
        return copy.deepcopy(state)

    def set_wallet_balances(self, address: str, balances: List[TokenBalance]) -> None:
        """
        Setzt deterministisch die Token-Bestände einer Wallet.
        Diese Funktion spiegelt nur einen bereits berechneten Zustand.
        """
        addr = (address or "").strip()
        if not addr:
            return
        self._wallets[addr] = WalletState(address=addr, balances=copy.deepcopy(balances))

    # -------------------------------------------------------------------------
    # Export / Import
    # -------------------------------------------------------------------------

    def export_state(self) -> Dict[str, Any]:
        """
        Exportiert den vollständigen Wallet-Zustand deterministisch.
        Enthält keine Seeds, keine privaten Schlüssel und keine Genesis-Logik.
        """
        data: Dict[str, Any] = {
            "current_address": self._current_address,
            "wallets": {},
        }
        for addr, state in self._wallets.items():
            data["wallets"][addr] = {
                "address": state.address,
                "balances": [
                    {
                        "token_index": b.token_index,
                        "symbol": b.symbol,
                        "amount": b.amount,
                    }
                    for b in state.balances
                ],
            }
        return data

    def import_state(self, data: Dict[str, Any]) -> None:
        """
        Importiert einen deterministisch erzeugten Wallet-Zustand.
        Erwartet ein zuvor mit export_state() erzeugtes Objekt.
        """
        if not isinstance(data, dict):
            return

        current_address = data.get("current_address")
        self._current_address = (current_address or "").strip() or None

        wallets_raw = data.get("wallets") or {}
        self._wallets.clear()

        for addr, w in wallets_raw.items():
            address = (w.get("address") or "").strip()
            if not address:
                continue
            balances_raw = w.get("balances") or []
            balances: List[TokenBalance] = []
            for b in balances_raw:
                try:
                    token_index = int(b.get("token_index"))
                    symbol = str(b.get("symbol") or "").strip()
                    amount = float(b.get("amount"))
                except (TypeError, ValueError):
                    continue
                balances.append(TokenBalance(token_index=token_index, symbol=symbol, amount=amount))
            self._wallets[address] = WalletState(address=address, balances=balances)


# Globale, paritätische Instanz
wallet_parity = ELTTWalletParity()
