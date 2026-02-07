# PYTHON-ELTT-MODULE-PARITY/ELTT-wallet/ELTT-launcher.py

"""
Paritätisches Launcher-/DEX-Modul im Kontext der ELTT-Wallet-Sicht.
Deterministische, auditierbare und souveränitätsfokussierte Spiegelung der
Launcher- und DEX-Struktur für Wallet-bezogene Operationen.

Die Owner-Wallet entsteht ausschließlich im Frontend, ist die einzige Genesis-Wallet,
besitzt TTTC, ELTT und ELTC, erzeugt Block 2 autonom und ist Ursprung aller Extensions.
Dieses Modul speichert keine Seeds und keine privaten Schlüssel und erzeugt keine
Genesis-Logik, sondern spiegelt nur einen bereits bestehenden Zustand.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import copy


@dataclass
class SwapRouteParity:
    route_id: str
    from_token_index: int
    to_token_index: int
    path: List[int]  # Liste von Token-Indizes, die den Swap-Pfad bilden


@dataclass
class SwapQuoteParity:
    route_id: str
    input_token_index: int
    output_token_index: int
    input_amount: float
    output_amount: float
    fee_amount: float


@dataclass
class LauncherStateParity:
    routes: List[SwapRouteParity] = field(default_factory=list)


class ELTTLauncherParityForWallet:
    """
    Paritätische Launcher-/DEX-Sicht, wie sie aus Wallet-Perspektive benötigt wird.
    Keine Genesis-Erzeugung, keine Schlüsselverwaltung, nur deterministische Spiegelung.
    """

    def __init__(self) -> None:
        self._state: LauncherStateParity = LauncherStateParity()

    # -------------------------------------------------------------------------
    # Zustand setzen / holen
    # -------------------------------------------------------------------------

    def set_launcher_state(self, state: LauncherStateParity) -> None:
        """
        Setzt den vollständigen Launcher-/DEX-Zustand deterministisch.
        Erwartet eine bereits berechnete, vertrauenswürdige Spiegelung.
        """
        self._state = copy.deepcopy(state)

    def get_launcher_state(self) -> LauncherStateParity:
        """
        Liefert eine tiefe Kopie des aktuellen Launcher-/DEX-Zustands.
        """
        return copy.deepcopy(self._state)

    # -------------------------------------------------------------------------
    # Routen
    # -------------------------------------------------------------------------

    def list_routes(self) -> List[SwapRouteParity]:
        """
        Liefert alle bekannten Swap-Routen.
        """
        return copy.deepcopy(self._state.routes)

    def get_route_by_id(self, route_id: str) -> Optional[SwapRouteParity]:
        """
        Liefert eine Swap-Route anhand ihrer ID.
        """
        rid = (route_id or "").strip()
        if not rid:
            return None
        for r in self._state.routes:
            if r.route_id == rid:
                return copy.deepcopy(r)
        return None

    def find_routes_for_pair(self, from_token_index: int, to_token_index: int) -> List[SwapRouteParity]:
        """
        Liefert alle Routen, die von einem Token zu einem anderen führen.
        """
        result: List[SwapRouteParity] = []
        for r in self._state.routes:
            if r.from_token_index == from_token_index and r.to_token_index == to_token_index:
                result.append(copy.deepcopy(r))
        return result

    # -------------------------------------------------------------------------
    # Quotes (Spiegelung)
    # -------------------------------------------------------------------------

    def mirror_swap_quote(
        self,
        route: SwapRouteParity,
        input_amount: float,
        output_amount: float,
        fee_amount: float,
    ) -> SwapQuoteParity:
        """
        Spiegelt einen bereits berechneten Swap-Quote deterministisch.
        Diese Funktion berechnet nichts neu, sondern kapselt nur die Daten.
        """
        return SwapQuoteParity(
            route_id=route.route_id,
            input_token_index=route.from_token_index,
            output_token_index=route.to_token_index,
            input_amount=input_amount,
            output_amount=output_amount,
            fee_amount=fee_amount,
        )

    # -------------------------------------------------------------------------
    # Export / Import
    # -------------------------------------------------------------------------

    def export_state(self) -> Dict[str, Any]:
        """
        Exportiert den Launcher-/DEX-Zustand deterministisch.
        Enthält keine Seeds, keine privaten Schlüssel und keine Genesis-Logik.
        """
        data: Dict[str, Any] = {
            "routes": [],
        }

        for r in self._state.routes:
            data["routes"].append(
                {
                    "route_id": r.route_id,
                    "from_token_index": r.from_token_index,
                    "to_token_index": r.to_token_index,
                    "path": list(r.path),
                }
            )

        return data

    def import_state(self, data: Dict[str, Any]) -> None:
        """
        Importiert einen deterministisch erzeugten Launcher-/DEX-Zustand.
        Erwartet ein zuvor mit export_state() erzeugtes Objekt.
        """
        if not isinstance(data, dict):
            return

        routes_raw = data.get("routes") or []
        routes: List[SwapRouteParity] = []

        for r in routes_raw:
            try:
                route_id = str(r.get("route_id") or "")
                from_token_index = int(r.get("from_token_index"))
                to_token_index = int(r.get("to_token_index"))
                path_raw = r.get("path") or []
                path: List[int] = [int(x) for x in path_raw]
            except (TypeError, ValueError):
                continue
            if not route_id:
                continue
            routes.append(
                SwapRouteParity(
                    route_id=route_id,
                    from_token_index=from_token_index,
                    to_token_index=to_token_index,
                    path=path,
                )
            )

        self._state = LauncherStateParity(routes=routes)


# Globale, paritätische Instanz für Wallet-bezogene Launcher-/DEX-Sicht
launcher_parity_for_wallet = ELTTLauncherParityForWallet()
