"""
PYTHON-ELTT-MODULE-PARITY/ELTT-Viewer/c_parity/stakingandpools.py

Parität zu: eltt_viewer_build_staking_and_pools in ELTT-Viewer.c
- reine Lese-Sicht auf Staking- und Pool-Positionen
- keine Mutationen, keine Validierung, keine STATE-Schreiboperationen
- JSON-kompatible Ausgabe
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence


# ---------------------------------------------------------------------------
# Datentypen – aggregierte Sicht auf Staking & Pools
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StakingAndPoolsEntry:
    chain_id: int               # z.B. EVM-Chain-ID
    protocol: str               # Name/ID des Protokolls (z.B. "ELTT-POOL")
    pool_address: str           # Pool-/Staking-Contract-Adresse
    staked_token_symbol: str    # Symbol des gestakten Tokens
    staked_amount: float        # Menge des gestakten Tokens
    reward_token_symbol: str    # Symbol des Reward-Tokens
    pending_rewards: float      # noch nicht abgeholte Rewards
    total_value: float          # Gesamtwert (Anzeigegröße, z.B. in Referenzwährung)

    def to_json(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "protocol": self.protocol,
            "pool_address": self.pool_address,
            "staked_token_symbol": self.staked_token_symbol,
            "staked_amount": self.staked_amount,
            "reward_token_symbol": self.reward_token_symbol,
            "pending_rewards": self.pending_rewards,
            "total_value": self.total_value,
        }


# ---------------------------------------------------------------------------
# Erwartete Portfolio-/State-Schnittstelle (read-only)
# ---------------------------------------------------------------------------
# Erwartet wird ein Objekt `portfolio` mit:
# - Attribut `staking_and_pools`: Sequence[StakingLike]
# - jedes StakingLike-Objekt hat:
#     - chain_id: int
#     - protocol: str
#     - pool_address: str
#     - staked_token_symbol: str
#     - staked_amount: float
#     - reward_token_symbol: str
#     - pending_rewards: float
#     - total_value: float
#
# Es werden ausschließlich Lesezugriffe durchgeführt.


def build_staking_and_pools(
    portfolio: Any,
    max_entries: int,
) -> List[StakingAndPoolsEntry]:
    """
    Parität zu:
        eltt_viewer_build_staking_and_pools(
            const eltt_portfolio *pf,
            eltt_staking_and_pools_entry *out_entries,
            size_t max_entries
        );
    """
    items: Sequence[Any] = getattr(portfolio, "staking_and_pools", [])
    count = min(len(items), max_entries)

    entries: List[StakingAndPoolsEntry] = []
    for i in range(count):
        s = items[i]

        entry = StakingAndPoolsEntry(
            chain_id=int(getattr(s, "chain_id")),
            protocol=str(getattr(s, "protocol")),
            pool_address=str(getattr(s, "pool_address")),
            staked_token_symbol=str(getattr(s, "staked_token_symbol")),
            staked_amount=float(getattr(s, "staked_amount", 0.0)),
            reward_token_symbol=str(getattr(s, "reward_token_symbol")),
            pending_rewards=float(getattr(s, "pending_rewards", 0.0)),
            total_value=float(getattr(s, "total_value", 0.0)),
        )
        entries.append(entry)

    return entries


def build_staking_and_pools_json(
    portfolio: Any,
    max_entries: int,
) -> List[Mapping[str, Any]]:
    """
    JSON-kompatible Variante.
    """
    return [entry.to_json() for entry in build_staking_and_pools(portfolio, max_entries)]
