# PYTHON-ELTT-MODULE-PARITY/ELTT-wallet/ELTT-liquidity-pools.py

"""
Paritätisches Liquidity-Pool-Modul im Kontext der ELTT-Wallet-Sicht.
Deterministische, auditierbare und souveränitätsfokussierte Spiegelung der
Liquidity-Pool-Struktur für Wallet-bezogene Operationen.

Die Owner-Wallet entsteht ausschließlich im Frontend, ist die einzige Genesis-Wallet,
besitzt TTTC, ELTT und ELTC, erzeugt Block 2 autonom und ist Ursprung aller Extensions.
Dieses Modul speichert keine Seeds und keine privaten Schlüssel und erzeugt keine
Genesis-Logik, sondern spiegelt nur einen bereits bestehenden Zustand.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import copy


@dataclass
class LiquidityPoolParity:
    pool_id: str
    token_x_index: int
    token_y_index: int
    lp_token_index: int
    reserve_x: float
    reserve_y: float


@dataclass
class WalletLiquidityPositionParity:
    address: str
    pool_id: str
    lp_amount: float


@dataclass
class LiquidityPoolsStateParity:
    pools: List[LiquidityPoolParity] = field(default_factory=list)
    positions: List[WalletLiquidityPositionParity] = field(default_factory=list)


class ELTTLiquidityPoolsParityForWallet:
    """
    Paritätische Liquidity-Pool-Sicht, wie sie aus Wallet-Perspektive benötigt wird.
    Keine Genesis-Erzeugung, keine Schlüsselverwaltung, nur deterministische Spiegelung.
    """

    def __init__(self) -> None:
        self._state: LiquidityPoolsStateParity = LiquidityPoolsStateParity()

    # -------------------------------------------------------------------------
    # Zustand setzen / holen
    # -------------------------------------------------------------------------

    def set_liquidity_pools_state(self, state: LiquidityPoolsStateParity) -> None:
        """
        Setzt den vollständigen Liquidity-Pool-Zustand deterministisch.
        Erwartet eine bereits berechnete, vertrauenswürdige Spiegelung.
        """
        self._state = copy.deepcopy(state)

    def get_liquidity_pools_state(self) -> LiquidityPoolsStateParity:
        """
        Liefert eine tiefe Kopie des aktuellen Liquidity-Pool-Zustands.
        """
        return copy.deepcopy(self._state)

    # -------------------------------------------------------------------------
    # Pools
    # -------------------------------------------------------------------------

    def list_pools(self) -> List[LiquidityPoolParity]:
        """
        Liefert alle bekannten Liquidity-Pools.
        """
        return copy.deepcopy(self._state.pools)

    def get_pool_by_id(self, pool_id: str) -> Optional[LiquidityPoolParity]:
        """
        Liefert einen Liquidity-Pool anhand seiner ID.
        """
        pid = (pool_id or "").strip()
        if not pid:
            return None
        for p in self._state.pools:
            if p.pool_id == pid:
                return copy.deepcopy(p)
        return None

    # -------------------------------------------------------------------------
    # Wallet-Positionen
    # -------------------------------------------------------------------------

    def list_positions_for_address(self, address: str) -> List[WalletLiquidityPositionParity]:
        """
        Liefert alle Liquidity-Positionen einer bestimmten Adresse.
        """
        addr = (address or "").strip()
        if not addr:
            return []
        result: List[WalletLiquidityPositionParity] = []
        for pos in self._state.positions:
            if pos.address == addr:
                result.append(copy.deepcopy(pos))
        return result

    def list_all_positions(self) -> List[WalletLiquidityPositionParity]:
        """
        Liefert alle Liquidity-Positionen aller Adressen.
        """
        return copy.deepcopy(self._state.positions)

    # -------------------------------------------------------------------------
    # Export / Import
    # -------------------------------------------------------------------------

    def export_state(self) -> Dict[str, Any]:
        """
        Exportiert den Liquidity-Pool-Zustand deterministisch.
        Enthält keine Seeds, keine privaten Schlüssel und keine Genesis-Logik.
        """
        data: Dict[str, Any] = {
            "pools": [],
            "positions": [],
        }

        for p in self._state.pools:
            data["pools"].append(
                {
                    "pool_id": p.pool_id,
                    "token_x_index": p.token_x_index,
                    "token_y_index": p.token_y_index,
                    "lp_token_index": p.lp_token_index,
                    "reserve_x": p.reserve_x,
                    "reserve_y": p.reserve_y,
                }
            )

        for pos in self._state.positions:
            data["positions"].append(
                {
                    "address": pos.address,
                    "pool_id": pos.pool_id,
                    "lp_amount": pos.lp_amount,
                }
            )

        return data

    def import_state(self, data: Dict[str, Any]) -> None:
        """
        Importiert einen deterministisch erzeugten Liquidity-Pool-Zustand.
        Erwartet ein zuvor mit export_state() erzeugtes Objekt.
        """
        if not isinstance(data, dict):
            return

        pools_raw = data.get("pools") or []
        positions_raw = data.get("positions") or []

        pools: List[LiquidityPoolParity] = []
        positions: List[WalletLiquidityPositionParity] = []

        for p in pools_raw:
            try:
                pool_id = str(p.get("pool_id") or "")
                token_x_index = int(p.get("token_x_index"))
                token_y_index = int(p.get("token_y_index"))
                lp_token_index = int(p.get("lp_token_index"))
                reserve_x = float(p.get("reserve_x"))
                reserve_y = float(p.get("reserve_y"))
            except (TypeError, ValueError):
                continue
            if not pool_id:
                continue
            pools.append(
                LiquidityPoolParity(
                    pool_id=pool_id,
                    token_x_index=token_x_index,
                    token_y_index=token_y_index,
                    lp_token_index=lp_token_index,
                    reserve_x=reserve_x,
                    reserve_y=reserve_y,
                )
            )

        for pos in positions_raw:
            try:
                address = str(pos.get("address") or "")
                pool_id = str(pos.get("pool_id") or "")
                lp_amount = float(pos.get("lp_amount"))
            except (TypeError, ValueError):
                continue
            if not address or not pool_id:
                continue
            positions.append(
                WalletLiquidityPositionParity(
                    address=address,
                    pool_id=pool_id,
                    lp_amount=lp_amount,
                )
            )

        self._state = LiquidityPoolsStateParity(pools=pools, positions=positions)


# Globale, paritätische Instanz für Wallet-bezogene Liquidity-Pool-Sicht
liquidity_pools_parity_for_wallet = ELTTLiquidityPoolsParityForWallet()
