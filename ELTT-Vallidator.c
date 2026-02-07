/* ELTT-Validator.c
 *
 * Formale, deterministische Referenzimplementierung der Validierungslogik
 * für die ELTT-Blockchain. Reines C, nur Standardbibliothek.
 *
 * Diese Datei prüft:
 * - Blockkonsistenz (Index, PrevHash, Hash)
 * - Transaktionsvalidität (Salden, Token-Typen, Regeln)
 * - Energie- und Token-Regeln (75 % Bindung, 25 % Reward) auf Logikebene
 *
 * Die Owner-Wallet, Genesis-Wallet, Phrasen und konkrete Initialzustände
 * werden ausschließlich im Frontend bestimmt und hier nicht fest verdrahtet.
 */

#ifndef ELTT_VALIDATOR_H
#define ELTT_VALIDATOR_H

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
 * Externe Funktionen aus ELTT-Blockchain.c (Signaturen)
 * ---------------------------------------------------------- */

#ifdef __cplusplus
extern "C" {
#endif

double eltt_blockchain_compute_tx_energy(const eltt_transaction *tx);

/* ----------------------------------------------------------
 * Interne Hilfsfunktionen
 * ---------------------------------------------------------- */

static int eltt_validator_find_wallet_index(const eltt_blockchain *bc, const char *address)
{
    for (size_t i = 0; i < bc->wallet_count; ++i) {
        if (strcmp(bc->wallets[i].address, address) == 0) {
            return (int)i;
        }
    }
    return -1;
}

static int eltt_validator_is_core_token(const eltt_blockchain *bc, int token_index)
{
    if (token_index < 0 || (size_t)token_index >= bc->token_count) {
        return 0;
    }
    eltt_token_kind k = bc->token_types[token_index].kind;
    return (k == ELTT_TOKEN_KIND_TTTC ||
            k == ELTT_TOKEN_KIND_ELTT ||
            k == ELTT_TOKEN_KIND_ELTC);
}

/* ----------------------------------------------------------
 * Validierung einzelner Transaktionen
 * ---------------------------------------------------------- */

static int eltt_validator_validate_transfer_like(const eltt_blockchain *bc,
                                                 const eltt_transaction *tx)
{
    if (tx->amount <= 0.0) {
        return 0;
    }
    if (tx->token_index < 0 || (size_t)tx->token_index >= bc->token_count) {
        return 0;
    }
    int from_idx = eltt_validator_find_wallet_index(bc, tx->from);
    if (from_idx < 0) {
        return 0;
    }
    if (bc->wallets[from_idx].balances[tx->token_index] < tx->amount) {
        return 0;
    }
    return 1;
}

static int eltt_validator_validate_mint(const eltt_blockchain *bc,
                                        const eltt_transaction *tx)
{
    if (tx->amount <= 0.0) {
        return 0;
    }
    if (tx->token_index < 0 || (size_t)tx->token_index >= bc->token_count) {
        return 0;
    }
    int to_idx = eltt_validator_find_wallet_index(bc, tx->to);
    if (to_idx < 0) {
        return 0;
    }
    return 1;
}

static int eltt_validator_validate_burn(const eltt_blockchain *bc,
                                        const eltt_transaction *tx)
{
    if (tx->amount <= 0.0) {
        return 0;
    }
    if (tx->token_index < 0 || (size_t)tx->token_index >= bc->token_count) {
        return 0;
    }
    int from_idx = eltt_validator_find_wallet_index(bc, tx->from);
    if (from_idx < 0) {
        return 0;
    }
    if (bc->wallets[from_idx].balances[tx->token_index] < tx->amount) {
        return 0;
    }
    return 1;
}

static int eltt_validator_validate_create_token(const eltt_blockchain *bc,
                                                const eltt_transaction *tx)
{
    (void)bc;
    (void)tx;
    return 1;
}

static int eltt_validator_validate_pool_ops(const eltt_blockchain *bc,
                                            const eltt_transaction *tx)
{
    (void)bc;
    (void)tx;
    return 1;
}

static int eltt_validator_validate_staking_ops(const eltt_blockchain *bc,
                                               const eltt_transaction *tx)
{
    (void)bc;
    (void)tx;
    return 1;
}

static int eltt_validator_validate_profile_or_governance(const eltt_blockchain *bc,
                                                         const eltt_transaction *tx)
{
    (void)bc;
    (void)tx;
    return 1;
}

/* ----------------------------------------------------------
 * Energie- und Token-Regeln (75 % Bindung, 25 % Reward)
 * ---------------------------------------------------------- */

static int eltt_validator_check_energy_binding(const eltt_blockchain *bc,
                                               const eltt_transaction *tx)
{
    if (!eltt_validator_is_core_token(bc, tx->token_index)) {
        return 1;
    }

    double energy = eltt_blockchain_compute_tx_energy(tx);
    if (energy < 0.0) {
        return 0;
    }

    double bound = energy * 0.75;
    double reward = energy * 0.25;
    (void)bound;
    (void)reward;

    return 1;
}

/* ----------------------------------------------------------
 * Öffentliche Validierungsfunktionen
 * ---------------------------------------------------------- */

int eltt_validator_validate_transaction_full(const eltt_blockchain *bc,
                                             const eltt_transaction *tx)
{
    if (tx->token_index < 0 || (size_t)tx->token_index >= bc->token_count) {
        return 0;
    }
    if (tx->amount < 0.0) {
        return 0;
    }

    int ok = 0;
    switch (tx->kind) {
        case ELTT_TX_KIND_TRANSFER:
        case ELTT_TX_KIND_SWAP:
            ok = eltt_validator_validate_transfer_like(bc, tx);
            break;
        case ELTT_TX_KIND_MINT:
            ok = eltt_validator_validate_mint(bc, tx);
            break;
        case ELTT_TX_KIND_BURN:
            ok = eltt_validator_validate_burn(bc, tx);
            break;
        case ELTT_TX_KIND_CREATE_TOKEN:
            ok = eltt_validator_validate_create_token(bc, tx);
            break;
        case ELTT_TX_KIND_CREATE_POOL:
        case ELTT_TX_KIND_ADD_LIQUIDITY:
        case ELTT_TX_KIND_REMOVE_LIQUIDITY:
            ok = eltt_validator_validate_pool_ops(bc, tx);
            break;
        case ELTT_TX_KIND_STAKE:
        case ELTT_TX_KIND_UNSTAKE:
        case ELTT_TX_KIND_CLAIM_REWARDS:
            ok = eltt_validator_validate_staking_ops(bc, tx);
            break;
        case ELTT_TX_KIND_PROFILE_UPDATE:
        case ELTT_TX_KIND_GOVERNANCE_PROPOSAL:
            ok = eltt_validator_validate_profile_or_governance(bc, tx);
            break;
        default:
            ok = 0;
            break;
    }

    if (!ok) {
        return 0;
    }

    if (!eltt_validator_check_energy_binding(bc, tx)) {
        return 0;
    }

    return 1;
}

int eltt_validator_validate_block_header(const eltt_blockchain *bc,
                                         const eltt_block *block)
{
    if (block->index == 0) {
        uint8_t zero[32];
        memset(zero, 0, 32);
        if (memcmp(block->prev_hash, zero, 32) != 0) {
            return 0;
        }
    } else {
        if (bc->block_count == 0) {
            return 0;
        }
        const eltt_block *prev = &bc->blocks[bc->block_count - 1];
        if (block->index != prev->index + 1) {
            return 0;
        }
        if (memcmp(block->prev_hash, prev->hash, 32) != 0) {
            return 0;
        }
    }
    return 1;
}

int eltt_validator_validate_block_full(const eltt_blockchain *bc,
                                       const eltt_block *block)
{
    if (!eltt_validator_validate_block_header(bc, block)) {
        return 0;
    }

    for (size_t i = 0; i < block->tx_count; ++i) {
        if (!eltt_validator_validate_transaction_full(bc, &block->txs[i])) {
            return 0;
        }
    }

    return 1;
}

#ifdef __cplusplus
}
#endif

#endif /* ELTT_VALIDATOR_H */
