/* ELTT-Viewer.c
 *
 * Formale, deterministische Referenzimplementierung der Viewer-Logik
 * für die ELTT-Blockchain. Reines C, nur Standardbibliothek.
 *
 * Diese Datei stellt reine Lese- und Struktur-Funktionen bereit:
 * - Zugriff auf Blöcke, Transaktionen, Wallets, Token, Pools, Staking.
 * - Ableitung von Chain-Grid-, Token-/Energie- und Positions-Ansichten.
 * - BIP-ähnliche Vorschlags- und Governance-Sicht.
 *
 * Keine UI, keine Beispiele, keine externen Abhängigkeiten.
 */

#ifndef ELTT_VIEWER_H
#define ELTT_VIEWER_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ----------------------------------------------------------
 * Gemeinsame Typen (müssen mit ELTT-Blockchain.c übereinstimmen)
 * ---------------------------------------------------------- */

#define ELTT_MAX_TOKEN_SYMBOL_LEN 16
#define ELTT_MAX_TOKEN_NAME_LEN   64
#define ELTT_MAX_ADDRESS_LEN      64
#define ELTT_MAX_MEMO_LEN         128
#define ELTT_MAX_TOKEN_TYPES      64
#define ELTT_MAX_TX_PER_BLOCK     256
#define ELTT_MAX_WALLETS          1024
#define ELTT_MAX_POOLS            256
#define ELTT_MAX_STAKES           1024

typedef enum {
    ELTT_TOKEN_KIND_TTTC,
    ELTT_TOKEN_KIND_ELTT,
    ELTT_TOKEN_KIND_ELTC,
    ELTT_TOKEN_KIND_GENERIC,
    ELTT_TOKEN_KIND_LP
} eltt_token_kind;

typedef struct {
    char  name[ELTT_MAX_TOKEN_NAME_LEN];
    char  symbol[ELTT_MAX_TOKEN_SYMBOL_LEN];
    int   decimals;
    eltt_token_kind kind;
    double energy_binding_factor;
} eltt_token_type;

typedef struct {
    char  address[ELTT_MAX_ADDRESS_LEN];
    size_t token_count;
    eltt_token_type tokens[ELTT_MAX_TOKEN_TYPES];
    double balances[ELTT_MAX_TOKEN_TYPES];
} eltt_wallet;

typedef enum {
    ELTT_TX_KIND_TRANSFER,
    ELTT_TX_KIND_MINT,
    ELTT_TX_KIND_BURN,
    ELTT_TX_KIND_CREATE_TOKEN,
    ELTT_TX_KIND_CREATE_POOL,
    ELTT_TX_KIND_ADD_LIQUIDITY,
    ELTT_TX_KIND_REMOVE_LIQUIDITY,
    ELTT_TX_KIND_STAKE,
    ELTT_TX_KIND_UNSTAKE,
    ELTT_TX_KIND_CLAIM_REWARDS,
    ELTT_TX_KIND_SWAP,
    ELTT_TX_KIND_PROFILE_UPDATE,
    ELTT_TX_KIND_GOVERNANCE_PROPOSAL
} eltt_tx_kind;

typedef struct {
    char  from[ELTT_MAX_ADDRESS_LEN];
    char  to[ELTT_MAX_ADDRESS_LEN];
    double amount;
    int   token_index;
    eltt_tx_kind kind;
    char  memo[ELTT_MAX_MEMO_LEN];
} eltt_transaction;

typedef struct {
    uint32_t index;
    uint64_t timestamp;
    uint8_t  prev_hash[32];
    uint8_t  hash[32];
    size_t   tx_count;
    eltt_transaction txs[ELTT_MAX_TX_PER_BLOCK];
} eltt_block;

typedef struct {
    int token_x_index;
    int token_y_index;
    double reserve_x;
    double reserve_y;
    int lp_token_index;
} eltt_liquidity_pool;

typedef struct {
    char  owner[ELTT_MAX_ADDRESS_LEN];
    int   token_index;
    double amount;
    uint64_t start_timestamp;
    uint64_t lock_until;
    double accumulated_rewards;
} eltt_staking_position;

typedef struct {
    size_t block_count;
    eltt_block *blocks;
    size_t wallet_count;
    eltt_wallet wallets[ELTT_MAX_WALLETS];
    size_t token_count;
    eltt_token_type token_types[ELTT_MAX_TOKEN_TYPES];
    size_t pool_count;
    eltt_liquidity_pool pools[ELTT_MAX_POOLS];
    size_t stake_count;
    eltt_staking_position stakes[ELTT_MAX_STAKES];
} eltt_blockchain;

/* ----------------------------------------------------------
 * Viewer-spezifische Strukturen
 * ---------------------------------------------------------- */

typedef struct {
    uint32_t index;
    uint64_t timestamp;
    uint8_t  hash[32];
    uint8_t  prev_hash[32];
    size_t   tx_count;
} eltt_chain_grid_entry;

typedef struct {
    int token_index;
    double balance;
    double energy_value;
} eltt_token_position;

typedef struct {
    int lp_token_index;
    int pool_index;
    double lp_balance;
    double share_x;
    double share_y;
    double energy_value;
} eltt_lp_position;

typedef struct {
    int stake_index;
    int token_index;
    double amount;
    uint64_t start_timestamp;
    uint64_t lock_until;
    double accumulated_rewards;
    double energy_value;
} eltt_staking_view_entry;

typedef struct {
    int pool_index;
    int token_x_index;
    int token_y_index;
    double reserve_x;
    double reserve_y;
    int lp_token_index;
} eltt_pool_view_entry;

typedef struct {
    size_t tx_index;
    uint32_t block_index;
    eltt_tx_kind kind;
} eltt_bip_like_entry;

/* ----------------------------------------------------------
 * Externe Energie-Funktion aus ELTT-Blockchain.c
 * ---------------------------------------------------------- */

#ifdef __cplusplus
extern "C" {
#endif

double eltt_blockchain_compute_tx_energy(const eltt_transaction *tx);

/* ----------------------------------------------------------
 * Interne Hilfsfunktionen
 * ---------------------------------------------------------- */

static int eltt_viewer_find_wallet_index(const eltt_blockchain *bc, const char *address)
{
    for (size_t i = 0; i < bc->wallet_count; ++i) {
        if (strcmp(bc->wallets[i].address, address) == 0) {
            return (int)i;
        }
    }
    return -1;
}

/* ----------------------------------------------------------
 * Chain-Grid-Ansicht
 * ---------------------------------------------------------- */

size_t eltt_viewer_build_chain_grid(const eltt_blockchain *bc,
                                    eltt_chain_grid_entry *out_entries,
                                    size_t max_entries)
{
    size_t count = (bc->block_count < max_entries) ? bc->block_count : max_entries;
    for (size_t i = 0; i < count; ++i) {
        const eltt_block *b = &bc->blocks[i];
        eltt_chain_grid_entry *e = &out_entries[i];
        e->index = b->index;
        e->timestamp = b->timestamp;
        memcpy(e->hash, b->hash, 32);
        memcpy(e->prev_hash, b->prev_hash, 32);
        e->tx_count = b->tx_count;
    }
    return count;
}

/* ----------------------------------------------------------
 * Token-/Energie-Ansicht für eine Wallet
 * ---------------------------------------------------------- */

size_t eltt_viewer_build_token_positions(const eltt_blockchain *bc,
                                         const char *wallet_address,
                                         eltt_token_position *out_positions,
                                         size_t max_positions)
{
    int widx = eltt_viewer_find_wallet_index(bc, wallet_address);
    if (widx < 0) {
        return 0;
    }
    const eltt_wallet *w = &bc->wallets[widx];

    size_t count = (w->token_count < max_positions) ? w->token_count : max_positions;
    for (size_t i = 0; i < count; ++i) {
        eltt_token_position *p = &out_positions[i];
        p->token_index = (int)i;
        p->balance = w->balances[i];
        p->energy_value = 0.0;
    }
    return count;
}

/* ----------------------------------------------------------
 * LP-Positionen für eine Wallet
 * ---------------------------------------------------------- */

size_t eltt_viewer_build_lp_positions(const eltt_blockchain *bc,
                                      const char *wallet_address,
                                      eltt_lp_position *out_positions,
                                      size_t max_positions)
{
    int widx = eltt_viewer_find_wallet_index(bc, wallet_address);
    if (widx < 0) {
        return 0;
    }
    const eltt_wallet *w = &bc->wallets[widx];

    size_t out_count = 0;
    for (size_t p = 0; p < bc->pool_count && out_count < max_positions; ++p) {
        const eltt_liquidity_pool *pool = &bc->pools[p];
        int lp_idx = pool->lp_token_index;
        if (lp_idx < 0 || (size_t)lp_idx >= w->token_count) {
            continue;
        }
        double lp_balance = w->balances[lp_idx];
        if (lp_balance <= 0.0) {
            continue;
        }

        eltt_lp_position *pos = &out_positions[out_count++];
        pos->lp_token_index = lp_idx;
        pos->pool_index = (int)p;
        pos->lp_balance = lp_balance;

        double total_lp = 1.0;
        double share = (total_lp > 0.0) ? (lp_balance / total_lp) : 0.0;
        pos->share_x = pool->reserve_x * share;
        pos->share_y = pool->reserve_y * share;
        pos->energy_value = 0.0;
    }

    return out_count;
}

/* ----------------------------------------------------------
 * Staking-Ansicht für eine Wallet
 * ---------------------------------------------------------- */

size_t eltt_viewer_build_staking_view(const eltt_blockchain *bc,
                                      const char *wallet_address,
                                      eltt_staking_view_entry *out_entries,
                                      size_t max_entries)
{
    size_t out_count = 0;
    for (size_t i = 0; i < bc->stake_count && out_count < max_entries; ++i) {
        const eltt_staking_position *s = &bc->stakes[i];
        if (strcmp(s->owner, wallet_address) != 0) {
            continue;
        }
        eltt_staking_view_entry *e = &out_entries[out_count++];
        e->stake_index = (int)i;
        e->token_index = s->token_index;
        e->amount = s->amount;
        e->start_timestamp = s->start_timestamp;
        e->lock_until = s->lock_until;
        e->accumulated_rewards = s->accumulated_rewards;
        e->energy_value = 0.0;
    }
    return out_count;
}

/* ----------------------------------------------------------
 * Pool-Ansicht (Stats)
 * ---------------------------------------------------------- */

size_t eltt_viewer_build_pool_view(const eltt_blockchain *bc,
                                   eltt_pool_view_entry *out_entries,
                                   size_t max_entries)
{
    size_t count = (bc->pool_count < max_entries) ? bc->pool_count : max_entries;
    for (size_t i = 0; i < count; ++i) {
        const eltt_liquidity_pool *p = &bc->pools[i];
        eltt_pool_view_entry *e = &out_entries[i];
        e->pool_index = (int)i;
        e->token_x_index = p->token_x_index;
        e->token_y_index = p->token_y_index;
        e->reserve_x = p->reserve_x;
        e->reserve_y = p->reserve_y;
        e->lp_token_index = p->lp_token_index;
    }
    return count;
}

/* ----------------------------------------------------------
 * BIP-ähnliche Vorschläge (Governance-Transaktionen)
 * ---------------------------------------------------------- */

size_t eltt_viewer_collect_bip_like_entries(const eltt_blockchain *bc,
                                            eltt_bip_like_entry *out_entries,
                                            size_t max_entries)
{
    size_t out_count = 0;
    for (size_t b = 0; b < bc->block_count && out_count < max_entries; ++b) {
        const eltt_block *blk = &bc->blocks[b];
        for (size_t t = 0; t < blk->tx_count && out_count < max_entries; ++t) {
            const eltt_transaction *tx = &blk->txs[t];
            if (tx->kind == ELTT_TX_KIND_GOVERNANCE_PROPOSAL) {
                eltt_bip_like_entry *e = &out_entries[out_count++];
                e->tx_index = t;
                e->block_index = blk->index;
                e->kind = tx->kind;
            }
        }
    }
    return out_count;
}

/* ----------------------------------------------------------
 * Wallet-Aktivität (Transaktions-Historie)
 * ---------------------------------------------------------- */

size_t eltt_viewer_collect_wallet_activity(const eltt_blockchain *bc,
                                           const char *wallet_address,
                                           eltt_transaction *out_txs,
                                           uint32_t *out_block_indices,
                                           size_t max_entries)
{
    size_t out_count = 0;
    for (size_t b = 0; b < bc->block_count && out_count < max_entries; ++b) {
        const eltt_block *blk = &bc->blocks[b];
        for (size_t t = 0; t < blk->tx_count && out_count < max_entries; ++t) {
            const eltt_transaction *tx = &blk->txs[t];
            if (strcmp(tx->from, wallet_address) == 0 ||
                strcmp(tx->to, wallet_address) == 0) {
                out_txs[out_count] = *tx;
                out_block_indices[out_count] = blk->index;
                out_count++;
            }
        }
    }
    return out_count;
}

/* ----------------------------------------------------------
 * Chain-Viewer-Funktionen (Detailansichten)
 * ---------------------------------------------------------- */

const eltt_block *eltt_viewer_get_block_by_index(const eltt_blockchain *bc,
                                                 uint32_t index)
{
    for (size_t i = 0; i < bc->block_count; ++i) {
        if (bc->blocks[i].index == index) {
            return &bc->blocks[i];
        }
    }
    return NULL;
}

const eltt_transaction *eltt_viewer_get_transaction(const eltt_block *block,
                                                    size_t tx_index)
{
    if (!block) {
        return NULL;
    }
    if (tx_index >= block->tx_count) {
        return NULL;
    }
    return &block->txs[tx_index];
}

/* ----------------------------------------------------------
 * Live-Modus (logische Sicht)
 * ---------------------------------------------------------- */

void eltt_viewer_live_snapshot(const eltt_blockchain *bc,
                               eltt_chain_grid_entry *chain_entries,
                               size_t max_chain_entries,
                               eltt_pool_view_entry *pool_entries,
                               size_t max_pool_entries)
{
    eltt_viewer_build_chain_grid(bc, chain_entries, max_chain_entries);
    eltt_viewer_build_pool_view(bc, pool_entries, max_pool_entries);
}

#ifdef __cplusplus
}
#endif

#endif /* ELTT_VIEWER_H */
