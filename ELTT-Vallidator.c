/* ELTT-Validator.c
 *
 * Formale, deterministische Referenzimplementierung der Validator-Logik
 * für die ELTT-Blockchain. Reines C, nur Standardbibliothek.
 *
 * Diese Datei:
 * - Mutiert keinen Zustand.
 * - Führt keine UI-Logik aus.
 * - Führt keine Korrekturen durch.
 * - Prüft nur Konsistenz, Integrität und Sicherheits-Invarianten.
 *
 * Sie ist als zentrales Sicherheits-/Paritätsmodul gedacht und kann
 * in jedem Parity-Modul, in c_parity und im UI-Spiegel verwendet werden.
 */

#ifndef ELTT_VALIDATOR_H
#define ELTT_VALIDATOR_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* ----------------------------------------------------------
 * Gemeinsame Typen (müssen mit ELTT-Blockchain.c / ELTT-Viewer.c übereinstimmen)
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
 * Externe Funktionen aus ELTT-Blockchain.c
 * ---------------------------------------------------------- */

#ifdef __cplusplus
extern "C" {
#endif

/* Hash-Funktion für Blöcke (muss mit ELTT-Blockchain.c übereinstimmen) */
void eltt_blockchain_compute_block_hash(eltt_block *block);

/* ----------------------------------------------------------
 * Fehlercodes für Validator
 * ---------------------------------------------------------- */

typedef enum {
    ELTT_VALIDATOR_OK = 0,

    /* Struktur / Basis */
    ELTT_VALIDATOR_ERR_NULL_BLOCKCHAIN,
    ELTT_VALIDATOR_ERR_NO_BLOCKS,

    /* Genesis / Chain */
    ELTT_VALIDATOR_ERR_GENESIS_PREV_HASH,
    ELTT_VALIDATOR_ERR_BLOCK_INDEX_SEQUENCE,
    ELTT_VALIDATOR_ERR_BLOCK_PREV_HASH_MISMATCH,
    ELTT_VALIDATOR_ERR_BLOCK_HASH_MISMATCH,
    ELTT_VALIDATOR_ERR_TIMESTAMP_NON_MONOTONIC,

    /* Token / Wallet / Pools / Stakes */
    ELTT_VALIDATOR_ERR_TOKEN_SYMBOL_DUPLICATE,
    ELTT_VALIDATOR_ERR_WALLET_ADDRESS_INVALID,
    ELTT_VALIDATOR_ERR_WALLET_BALANCE_NEGATIVE,
    ELTT_VALIDATOR_ERR_POOL_INDEX_INVALID,
    ELTT_VALIDATOR_ERR_POOL_RESERVE_NEGATIVE,
    ELTT_VALIDATOR_ERR_STAKE_OWNER_INVALID,
    ELTT_VALIDATOR_ERR_STAKE_AMOUNT_NEGATIVE,
    ELTT_VALIDATOR_ERR_STAKE_TIME_INCONSISTENT,

    /* Transaktionen */
    ELTT_VALIDATOR_ERR_TX_TOKEN_INDEX_INVALID,
    ELTT_VALIDATOR_ERR_TX_AMOUNT_NEGATIVE,
    ELTT_VALIDATOR_ERR_TX_KIND_INVALID,
    ELTT_VALIDATOR_ERR_TX_REPLAY_DUPLICATE_IN_BLOCK,

    /* Reserviert für Erweiterungen */
    ELTT_VALIDATOR_ERR_UNKNOWN
} eltt_validator_error;

/* ----------------------------------------------------------
 * Interne Hilfsfunktionen (static)
 * ---------------------------------------------------------- */

static int eltt_validator_is_address_valid(const char *addr)
{
    if (!addr) {
        return 0;
    }
    size_t len = strlen(addr);
    if (len == 0 || len >= ELTT_MAX_ADDRESS_LEN) {
        return 0;
    }
    /* Optional: einfache Zeichenprüfung (keine Steuerzeichen) */
    for (size_t i = 0; i < len; ++i) {
        unsigned char c = (unsigned char)addr[i];
        if (c < 32 || c == 127) {
            return 0;
        }
    }
    return 1;
}

static int eltt_validator_check_token_symbols_unique(const eltt_blockchain *bc)
{
    for (size_t i = 0; i < bc->token_count; ++i) {
        for (size_t j = i + 1; j < bc->token_count; ++j) {
            if (strncmp(bc->token_types[i].symbol,
                        bc->token_types[j].symbol,
                        ELTT_MAX_TOKEN_SYMBOL_LEN) == 0) {
                return 0;
            }
        }
    }
    return 1;
}

static int eltt_validator_check_wallets(const eltt_blockchain *bc,
                                        eltt_validator_error *out_err)
{
    for (size_t i = 0; i < bc->wallet_count; ++i) {
        const eltt_wallet *w = &bc->wallets[i];
        if (!eltt_validator_is_address_valid(w->address)) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_WALLET_ADDRESS_INVALID;
            return 0;
        }
        if (w->token_count > bc->token_count) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_TX_TOKEN_INDEX_INVALID;
            return 0;
        }
        for (size_t t = 0; t < w->token_count; ++t) {
            if (w->balances[t] < 0.0) {
                if (out_err) *out_err = ELTT_VALIDATOR_ERR_WALLET_BALANCE_NEGATIVE;
                return 0;
            }
        }
    }
    return 1;
}

static int eltt_validator_check_pools(const eltt_blockchain *bc,
                                      eltt_validator_error *out_err)
{
    for (size_t i = 0; i < bc->pool_count; ++i) {
        const eltt_liquidity_pool *p = &bc->pools[i];
        if (p->token_x_index < 0 || (size_t)p->token_x_index >= bc->token_count) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_POOL_INDEX_INVALID;
            return 0;
        }
        if (p->token_y_index < 0 || (size_t)p->token_y_index >= bc->token_count) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_POOL_INDEX_INVALID;
            return 0;
        }
        if (p->lp_token_index < 0 || (size_t)p->lp_token_index >= bc->token_count) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_POOL_INDEX_INVALID;
            return 0;
        }
        if (p->reserve_x < 0.0 || p->reserve_y < 0.0) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_POOL_RESERVE_NEGATIVE;
            return 0;
        }
    }
    return 1;
}

static int eltt_validator_check_stakes(const eltt_blockchain *bc,
                                       eltt_validator_error *out_err)
{
    for (size_t i = 0; i < bc->stake_count; ++i) {
        const eltt_staking_position *s = &bc->stakes[i];
        if (!eltt_validator_is_address_valid(s->owner)) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_STAKE_OWNER_INVALID;
            return 0;
        }
        if (s->token_index < 0 || (size_t)s->token_index >= bc->token_count) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_TX_TOKEN_INDEX_INVALID;
            return 0;
        }
        if (s->amount < 0.0) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_STAKE_AMOUNT_NEGATIVE;
            return 0;
        }
        if (s->lock_until < s->start_timestamp) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_STAKE_TIME_INCONSISTENT;
            return 0;
        }
    }
    return 1;
}

/* einfache Block-interne Replay-Erkennung:
 * Wir bilden aus (from,to,token_index,amount,kind,memo) einen simplen Hash
 * und prüfen auf Duplikate innerhalb desselben Blocks.
 * Keine Korrektur, nur Erkennung.
 */
static uint32_t eltt_validator_tx_simple_hash(const eltt_transaction *tx)
{
    /* sehr einfache, deterministische Hash-Funktion */
    uint32_t h = 2166136261u;
    const unsigned char *p;
    p = (const unsigned char *)tx->from;
    while (*p) { h ^= *p++; h *= 16777619u; }
    p = (const unsigned char *)tx->to;
    while (*p) { h ^= *p++; h *= 16777619u; }
    p = (const unsigned char *)tx->memo;
    while (*p) { h ^= *p++; h *= 16777619u; }

    /* token_index, kind, amount grob einmischen */
    h ^= (uint32_t)tx->token_index; h *= 16777619u;
    h ^= (uint32_t)tx->kind;        h *= 16777619u;

    /* amount als double-Bits */
    union { double d; uint64_t u; } conv;
    conv.d = tx->amount;
    h ^= (uint32_t)(conv.u & 0xffffffffu); h *= 16777619u;
    h ^= (uint32_t)(conv.u >> 32);         h *= 16777619u;

    return h;
}

static int eltt_validator_check_transaction_basic(const eltt_blockchain *bc,
                                                  const eltt_transaction *tx,
                                                  eltt_validator_error *out_err)
{
    if (tx->token_index < 0 || (size_t)tx->token_index >= bc->token_count) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_TX_TOKEN_INDEX_INVALID;
        return 0;
    }
    if (tx->amount < 0.0) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_TX_AMOUNT_NEGATIVE;
        return 0;
    }

    /* Adressen formal prüfen (nicht Balance, nur Form) */
    if (!eltt_validator_is_address_valid(tx->from)) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_WALLET_ADDRESS_INVALID;
        return 0;
    }
    if (!eltt_validator_is_address_valid(tx->to)) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_WALLET_ADDRESS_INVALID;
        return 0;
    }

    /* Kind-Bereich prüfen */
    if (tx->kind < ELTT_TX_KIND_TRANSFER ||
        tx->kind > ELTT_TX_KIND_GOVERNANCE_PROPOSAL) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_TX_KIND_INVALID;
        return 0;
    }

    return 1;
}

static int eltt_validator_check_block_transactions(const eltt_blockchain *bc,
                                                   const eltt_block *blk,
                                                   eltt_validator_error *out_err)
{
    if (blk->tx_count > ELTT_MAX_TX_PER_BLOCK) {
        /* formaler Schutz, sollte nie passieren, da Struktur begrenzt ist */
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_UNKNOWN;
        return 0;
    }

    /* einfache Replay-Erkennung innerhalb des Blocks */
    uint32_t seen_hashes[ELTT_MAX_TX_PER_BLOCK];
    size_t seen_count = 0;

    for (size_t i = 0; i < blk->tx_count; ++i) {
        const eltt_transaction *tx = &blk->txs[i];

        if (!eltt_validator_check_transaction_basic(bc, tx, out_err)) {
            return 0;
        }

        uint32_t h = eltt_validator_tx_simple_hash(tx);
        for (size_t j = 0; j < seen_count; ++j) {
            if (seen_hashes[j] == h) {
                if (out_err) *out_err = ELTT_VALIDATOR_ERR_TX_REPLAY_DUPLICATE_IN_BLOCK;
                return 0;
            }
        }
        seen_hashes[seen_count++] = h;
    }

    return 1;
}

static int eltt_validator_check_chain(const eltt_blockchain *bc,
                                      eltt_validator_error *out_err)
{
    if (bc->block_count == 0) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_NO_BLOCKS;
        return 0;
    }

    uint64_t last_ts = 0;

    for (size_t i = 0; i < bc->block_count; ++i) {
        const eltt_block *blk = &bc->blocks[i];

        /* Genesis-Block */
        if (i == 0) {
            uint8_t zero[32];
            memset(zero, 0, 32);
            if (memcmp(blk->prev_hash, zero, 32) != 0) {
                if (out_err) *out_err = ELTT_VALIDATOR_ERR_GENESIS_PREV_HASH;
                return 0;
            }
        } else {
            const eltt_block *prev = &bc->blocks[i - 1];
            if (blk->index != prev->index + 1) {
                if (out_err) *out_err = ELTT_VALIDATOR_ERR_BLOCK_INDEX_SEQUENCE;
                return 0;
            }
            if (memcmp(blk->prev_hash, prev->hash, 32) != 0) {
                if (out_err) *out_err = ELTT_VALIDATOR_ERR_BLOCK_PREV_HASH_MISMATCH;
                return 0;
            }
        }

        /* Hash-Konsistenz prüfen */
        eltt_block tmp = *blk;
        eltt_blockchain_compute_block_hash(&tmp);
        if (memcmp(tmp.hash, blk->hash, 32) != 0) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_BLOCK_HASH_MISMATCH;
            return 0;
        }

        /* Zeitstempel-Monotonie (nicht zwingend streng, aber geprüft) */
        if (i > 0 && blk->timestamp < last_ts) {
            if (out_err) *out_err = ELTT_VALIDATOR_ERR_TIMESTAMP_NON_MONOTONIC;
            return 0;
        }
        last_ts = blk->timestamp;

        /* Transaktionen im Block prüfen */
        if (!eltt_validator_check_block_transactions(bc, blk, out_err)) {
            return 0;
        }
    }

    return 1;
}

/* ----------------------------------------------------------
 * Öffentliche Validator-API
 * ---------------------------------------------------------- */

/* Vollständige Blockchain-Prüfung:
 * - Struktur
 * - Token
 * - Wallets
 * - Pools
 * - Stakes
 * - Chain (Blöcke, Hashes, prev_hash, Timestamps, TXs)
 *
 * Gibt 1 bei Erfolg zurück, 0 bei Fehler.
 * out_err (optional) enthält den ersten gefundenen Fehlercode.
 */
int eltt_validator_check_blockchain(const eltt_blockchain *bc,
                                    eltt_validator_error *out_err)
{
    if (out_err) {
        *out_err = ELTT_VALIDATOR_OK;
    }

    if (!bc) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_NULL_BLOCKCHAIN;
        return 0;
    }

    /* Token-Symbole auf Duplikate prüfen */
    if (!eltt_validator_check_token_symbols_unique(bc)) {
        if (out_err) *out_err = ELTT_VALIDATOR_ERR_TOKEN_SYMBOL_DUPLICATE;
        return 0;
    }

    /* Wallets prüfen */
    if (!eltt_validator_check_wallets(bc, out_err)) {
        return 0;
    }

    /* Pools prüfen */
    if (!eltt_validator_check_pools(bc, out_err)) {
        return 0;
    }

    /* Stakes prüfen */
    if (!eltt_validator_check_stakes(bc, out_err)) {
        return 0;
    }

    /* Chain (Blöcke, Hashes, Timestamps, TXs) prüfen */
    if (!eltt_validator_check_chain(bc, out_err)) {
        return 0;
    }

    return 1;
}

#ifdef __cplusplus
}
#endif

#endif /* ELTT_VALIDATOR_H */
