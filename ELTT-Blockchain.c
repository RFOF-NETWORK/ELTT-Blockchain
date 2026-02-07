/* ELTT-Blockchain.c
 *
 * Formale, deterministische Referenzimplementierung der ELTT-Blockchain-Logik.
 * Keine Beispiele, keine Interpretationen, keine externen Abhängigkeiten.
 * Reines C, nur Standardbibliothek, keine externen Libraries.
 *
 * Enthält:
 * - Datenstrukturen für Blöcke, Transaktionen, Wallets, Token, LP-Token, Pools, Staking.
 * - Deterministische SHA-256-Implementierung.
 * - SI-Byte-System und binäres Byte-System als normative Tabellen.
 * - Energie-Formel E(TX) = SI_Byte_Wert(TX) + Binär_Byte_Wert(TX) + (SHA256(TX_Daten) mod 1).
 * - Deterministische Blockchain-Operationen (Genesis, Blöcke, Transaktionen, Validierung).
 *
 * Die Owner-Wallet, die Genesis-Wallet, die Phrasen und die konkrete Initialisierung
 * werden ausschließlich durch Frontend-Logik bestimmt und hier nicht fest verdrahtet.
 * Diese Datei bildet nur die deterministische Kernlogik ab.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ----------------------------------------------------------
 * SHA-256 – deterministische Implementierung
 * ---------------------------------------------------------- */

typedef struct {
    uint8_t data[64];
    uint32_t datalen;
    uint64_t bitlen;
    uint32_t state[8];
} eltt_sha256_ctx;

#define ELTT_SHA256_ROTR(a,b) (((a) >> (b)) | ((a) << (32-(b))))
#define ELTT_SHA256_CH(x,y,z) (((x) & (y)) ^ (~(x) & (z)))
#define ELTT_SHA256_MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define ELTT_SHA256_EP0(x) (ELTT_SHA256_ROTR(x,2) ^ ELTT_SHA256_ROTR(x,13) ^ ELTT_SHA256_ROTR(x,22))
#define ELTT_SHA256_EP1(x) (ELTT_SHA256_ROTR(x,6) ^ ELTT_SHA256_ROTR(x,11) ^ ELTT_SHA256_ROTR(x,25))
#define ELTT_SHA256_SIG0(x) (ELTT_SHA256_ROTR(x,7) ^ ELTT_SHA256_ROTR(x,18) ^ ((x) >> 3))
#define ELTT_SHA256_SIG1(x) (ELTT_SHA256_ROTR(x,17) ^ ELTT_SHA256_ROTR(x,19) ^ ((x) >> 10))

static const uint32_t eltt_sha256_k[64] = {
    0x428a2f98UL,0x71374491UL,0xb5c0fbcfUL,0xe9b5dba5UL,0x3956c25bUL,0x59f111f1UL,0x923f82a4UL,0xab1c5ed5UL,
    0xd807aa98UL,0x12835b01UL,0x243185beUL,0x550c7dc3UL,0x72be5d74UL,0x80deb1feUL,0x9bdc06a7UL,0xc19bf174UL,
    0xe49b69c1UL,0xefbe4786UL,0x0fc19dc6UL,0x240ca1ccUL,0x2de92c6fUL,0x4a7484aaUL,0x5cb0a9dcUL,0x76f988daUL,
    0x983e5152UL,0xa831c66dUL,0xb00327c8UL,0xbf597fc7UL,0xc6e00bf3UL,0xd5a79147UL,0x06ca6351UL,0x14292967UL,
    0x27b70a85UL,0x2e1b2138UL,0x4d2c6dfcUL,0x53380d13UL,0x650a7354UL,0x766a0abbUL,0x81c2c92eUL,0x92722c85UL,
    0xa2bfe8a1UL,0xa81a664bUL,0xc24b8b70UL,0xc76c51a3UL,0xd192e819UL,0xd6990624UL,0xf40e3585UL,0x106aa070UL,
    0x19a4c116UL,0x1e376c08UL,0x2748774cUL,0x34b0bcb5UL,0x391c0cb3UL,0x4ed8aa4aUL,0x5b9cca4fUL,0x682e6ff3UL,
    0x748f82eeUL,0x78a5636fUL,0x84c87814UL,0x8cc70208UL,0x90befffaUL,0xa4506cebUL,0xbef9a3f7UL,0xc67178f2UL
};

static void eltt_sha256_transform(eltt_sha256_ctx *ctx, const uint8_t data[])
{
    uint32_t a,b,c,d,e,f,g,h,i,j,t1,t2,m[64];

    for (i = 0, j = 0; i < 16; ++i, j += 4) {
        m[i] = ((uint32_t)data[j] << 24) |
               ((uint32_t)data[j+1] << 16) |
               ((uint32_t)data[j+2] << 8) |
               ((uint32_t)data[j+3]);
    }
    for ( ; i < 64; ++i) {
        m[i] = ELTT_SHA256_SIG1(m[i-2]) + m[i-7] + ELTT_SHA256_SIG0(m[i-15]) + m[i-16];
    }

    a = ctx->state[0];
    b = ctx->state[1];
    c = ctx->state[2];
    d = ctx->state[3];
    e = ctx->state[4];
    f = ctx->state[5];
    g = ctx->state[6];
    h = ctx->state[7];

    for (i = 0; i < 64; ++i) {
        t1 = h + ELTT_SHA256_EP1(e) + ELTT_SHA256_CH(e,f,g) + eltt_sha256_k[i] + m[i];
        t2 = ELTT_SHA256_EP0(a) + ELTT_SHA256_MAJ(a,b,c);
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    ctx->state[0] += a;
    ctx->state[1] += b;
    ctx->state[2] += c;
    ctx->state[3] += d;
    ctx->state[4] += e;
    ctx->state[5] += f;
    ctx->state[6] += g;
    ctx->state[7] += h;
}

static void eltt_sha256_init(eltt_sha256_ctx *ctx)
{
    ctx->datalen = 0;
    ctx->bitlen = 0;
    ctx->state[0] = 0x6a09e667UL;
    ctx->state[1] = 0xbb67ae85UL;
    ctx->state[2] = 0x3c6ef372UL;
    ctx->state[3] = 0xa54ff53aUL;
    ctx->state[4] = 0x510e527fUL;
    ctx->state[5] = 0x9b05688cUL;
    ctx->state[6] = 0x1f83d9abUL;
    ctx->state[7] = 0x5be0cd19UL;
}

static void eltt_sha256_update(eltt_sha256_ctx *ctx, const uint8_t data[], size_t len)
{
    for (size_t i = 0; i < len; ++i) {
        ctx->data[ctx->datalen] = data[i];
        ctx->datalen++;
        if (ctx->datalen == 64) {
            eltt_sha256_transform(ctx, ctx->data);
            ctx->bitlen += 512;
            ctx->datalen = 0;
        }
    }
}

static void eltt_sha256_final(eltt_sha256_ctx *ctx, uint8_t hash[])
{
    uint32_t i = ctx->datalen;

    if (ctx->datalen < 56) {
        ctx->data[i++] = 0x80;
        while (i < 56) {
            ctx->data[i++] = 0x00;
        }
    } else {
        ctx->data[i++] = 0x80;
        while (i < 64) {
            ctx->data[i++] = 0x00;
        }
        eltt_sha256_transform(ctx, ctx->data);
        memset(ctx->data, 0, 56);
    }

    ctx->bitlen += ctx->datalen * 8;
    ctx->data[63] = (uint8_t)(ctx->bitlen);
    ctx->data[62] = (uint8_t)(ctx->bitlen >> 8);
    ctx->data[61] = (uint8_t)(ctx->bitlen >> 16);
    ctx->data[60] = (uint8_t)(ctx->bitlen >> 24);
    ctx->data[59] = (uint8_t)(ctx->bitlen >> 32);
    ctx->data[58] = (uint8_t)(ctx->bitlen >> 40);
    ctx->data[57] = (uint8_t)(ctx->bitlen >> 48);
    ctx->data[56] = (uint8_t)(ctx->bitlen >> 56);
    eltt_sha256_transform(ctx, ctx->data);

    for (i = 0; i < 4; ++i) {
        hash[i]      = (uint8_t)((ctx->state[0] >> (24 - i * 8)) & 0xff);
        hash[i + 4]  = (uint8_t)((ctx->state[1] >> (24 - i * 8)) & 0xff);
        hash[i + 8]  = (uint8_t)((ctx->state[2] >> (24 - i * 8)) & 0xff);
        hash[i + 12] = (uint8_t)((ctx->state[3] >> (24 - i * 8)) & 0xff);
        hash[i + 16] = (uint8_t)((ctx->state[4] >> (24 - i * 8)) & 0xff);
        hash[i + 20] = (uint8_t)((ctx->state[5] >> (24 - i * 8)) & 0xff);
        hash[i + 24] = (uint8_t)((ctx->state[6] >> (24 - i * 8)) & 0xff);
        hash[i + 28] = (uint8_t)((ctx->state[7] >> (24 - i * 8)) & 0xff);
    }
}

static void eltt_sha256(const uint8_t *data, size_t len, uint8_t out[32])
{
    eltt_sha256_ctx ctx;
    eltt_sha256_init(&ctx);
    eltt_sha256_update(&ctx, data, len);
    eltt_sha256_final(&ctx, out);
}

/* ----------------------------------------------------------
 * Byte-Systeme (SI und binär) – normative Tabellen
 * ---------------------------------------------------------- */

typedef struct {
    const char *name;
    const char *symbol;
    double power10;
} eltt_si_byte_unit;

static const eltt_si_byte_unit ELTT_SI_BYTE_TABLE[24] = {
    {"Quecto", "qB", 1e-30},
    {"Ronto",  "rB", 1e-27},
    {"Yocto",  "yB", 1e-24},
    {"Zepto",  "zB", 1e-21},
    {"Atto",   "aB", 1e-18},
    {"Femto",  "fB", 1e-15},
    {"Pico",   "pB", 1e-12},
    {"Nano",   "nB", 1e-9},
    {"Mikro",  "µB", 1e-6},
    {"Milli",  "mB", 1e-3},
    {"Zenti",  "cB", 1e-2},
    {"Dezi",   "dB", 1e-1},
    {"Byte",   "B",  1e0},
    {"Deka",   "daB",1e1},
    {"Hekto",  "hB", 1e2},
    {"Kilo",   "kB", 1e3},
    {"Mega",   "MB", 1e6},
    {"Giga",   "GB", 1e9},
    {"Tera",   "TB", 1e12},
    {"Peta",   "PB", 1e15},
    {"Exa",    "EB", 1e18},
    {"Zetta",  "ZB", 1e21},
    {"Yotta",  "YB", 1e24},
    {"Quetta", "QB", 1e30}
};

typedef struct {
    const char *name;
    const char *symbol;
    int power2;
    double approx_bytes;
} eltt_binary_byte_unit;

static const eltt_binary_byte_unit ELTT_BINARY_BYTE_TABLE[24] = {
    {"Quectibyte", "QiB",   0,   1.0},
    {"Rontibyte",  "RiB",  10,   1024.0},
    {"Yoctibyte",  "YiB",  20,   1048576.0},
    {"Zeptibyte",  "ZiB",  30,   1073741824.0},
    {"Attibyte",   "AiB",  40,   1099511627776.0},
    {"Femtoibyte", "FiB",  50,   1125899906842624.0},
    {"Picoibyte",  "PiB",  60,   1152921504606846976.0},
    {"Nanoibyte",  "NiB",  70,   1180591620717411303424.0},
    {"Microibyte", "µiB",  80,   1208925819614629174706176.0},
    {"Millibyte",  "miB",  90,   1.237e27},
    {"Centibyte",  "ciB", 100,   1.267e30},
    {"Decibyte",   "diB", 110,   1.298e33},
    {"Byte",       "B",   120,   1.330e36},
    {"Dekibyte",   "daiB",130,   1.363e39},
    {"Hektibyte",  "hiB", 140,   1.398e42},
    {"Kilobibyte", "KiB", 150,   1.433e45},
    {"Megabibyte", "MiB", 160,   1.470e48},
    {"Gigabibyte", "GiB", 170,   1.508e51},
    {"Terabibyte", "TiB", 180,   1.547e54},
    {"Petabibyte", "PiBiB",190,  1.587e57},
    {"Exbibibyte", "EiBiB",200,  1.628e60},
    {"Zebbibyte",  "ZiBiB",210,  1.670e63},
    {"Yobbibyte",  "YiBiB",220,  1.713e66},
    {"Quettibyte", "QiBiB",230,  1.757e69}
};

/* Normative Hilfsfunktionen zur Energie-Berechnung */

static double eltt_si_byte_value_from_size(size_t bytes)
{
    if (bytes == 0) {
        return 0.0;
    }
    double b = (double)bytes;
    double best = b;
    for (int i = 0; i < 24; ++i) {
        double v = b / ELTT_SI_BYTE_TABLE[i].power10;
        (void)v;
    }
    return b;
}

static double eltt_binary_byte_value_from_size(size_t bytes)
{
    if (bytes == 0) {
        return 0.0;
    }
    double b = (double)bytes;
    double best = b;
    for (int i = 0; i < 24; ++i) {
        double v = b / ELTT_BINARY_BYTE_TABLE[i].approx_bytes;
        (void)v;
    }
    return b;
}

/* ----------------------------------------------------------
 * Kern-Datenstrukturen
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
 * Hilfsfunktionen für Hashing und Serialisierung
 * ---------------------------------------------------------- */

static void eltt_serialize_transaction(const eltt_transaction *tx, uint8_t **out, size_t *out_len)
{
    size_t len = 0;
    len += strlen(tx->from) + 1;
    len += strlen(tx->to) + 1;
    len += sizeof(double);
    len += sizeof(int);
    len += sizeof(int);
    len += strlen(tx->memo) + 1;

    uint8_t *buf = (uint8_t *)malloc(len);
    size_t pos = 0;

    size_t lfrom = strlen(tx->from) + 1;
    memcpy(buf + pos, tx->from, lfrom);
    pos += lfrom;

    size_t lto = strlen(tx->to) + 1;
    memcpy(buf + pos, tx->to, lto);
    pos += lto;

    memcpy(buf + pos, &tx->amount, sizeof(double));
    pos += sizeof(double);

    memcpy(buf + pos, &tx->token_index, sizeof(int));
    pos += sizeof(int);

    int kind = (int)tx->kind;
    memcpy(buf + pos, &kind, sizeof(int));
    pos += sizeof(int);

    size_t lmemo = strlen(tx->memo) + 1;
    memcpy(buf + pos, tx->memo, lmemo);
    pos += lmemo;

    *out = buf;
    *out_len = pos;
}

static void eltt_serialize_block_header(const eltt_block *block, uint8_t **out, size_t *out_len)
{
    size_t len = 0;
    len += sizeof(uint32_t);
    len += sizeof(uint64_t);
    len += 32;
    len += sizeof(size_t);

    uint8_t *buf = (uint8_t *)malloc(len);
    size_t pos = 0;

    memcpy(buf + pos, &block->index, sizeof(uint32_t));
    pos += sizeof(uint32_t);

    memcpy(buf + pos, &block->timestamp, sizeof(uint64_t));
    pos += sizeof(uint64_t);

    memcpy(buf + pos, block->prev_hash, 32);
    pos += 32;

    memcpy(buf + pos, &block->tx_count, sizeof(size_t));
    pos += sizeof(size_t);

    *out = buf;
    *out_len = pos;
}

static void eltt_compute_block_hash(eltt_block *block)
{
    uint8_t *header = NULL;
    size_t header_len = 0;
    eltt_serialize_block_header(block, &header, &header_len);

    eltt_sha256(header, header_len, block->hash);

    free(header);
}

/* ----------------------------------------------------------
 * Energie-Formel
 * ---------------------------------------------------------- */

static double eltt_energy_from_transaction(const eltt_transaction *tx)
{
    uint8_t *serialized = NULL;
    size_t serialized_len = 0;
    eltt_serialize_transaction(tx, &serialized, &serialized_len);

    double si_value = eltt_si_byte_value_from_size(serialized_len);
    double bin_value = eltt_binary_byte_value_from_size(serialized_len);

    uint8_t hash[32];
    eltt_sha256(serialized, serialized_len, hash);

    uint64_t last8 = 0;
    for (int i = 24; i < 32; ++i) {
        last8 = (last8 << 8) | hash[i];
    }
    double frac = (double)(last8 % 1000000000ULL) / 1000000000.0;

    double energy = si_value + bin_value + frac;

    free(serialized);
    return energy;
}

/* ----------------------------------------------------------
 * Token- und Wallet-Logik
 * ---------------------------------------------------------- */

static int eltt_find_wallet_index(const eltt_blockchain *bc, const char *address)
{
    for (size_t i = 0; i < bc->wallet_count; ++i) {
        if (strcmp(bc->wallets[i].address, address) == 0) {
            return (int)i;
        }
    }
    return -1;
}

static int eltt_add_wallet(eltt_blockchain *bc, const char *address)
{
    if (bc->wallet_count >= ELTT_MAX_WALLETS) {
        return -1;
    }
    int idx = (int)bc->wallet_count;
    eltt_wallet *w = &bc->wallets[idx];
    memset(w, 0, sizeof(*w));
    strncpy(w->address, address, ELTT_MAX_ADDRESS_LEN - 1);
    w->address[ELTT_MAX_ADDRESS_LEN - 1] = '\0';
    w->token_count = bc->token_count;
    for (size_t i = 0; i < bc->token_count; ++i) {
        w->balances[i] = 0.0;
    }
    bc->wallet_count++;
    return idx;
}

static int eltt_find_or_create_wallet(eltt_blockchain *bc, const char *address)
{
    int idx = eltt_find_wallet_index(bc, address);
    if (idx >= 0) {
        return idx;
    }
    return eltt_add_wallet(bc, address);
}

static int eltt_add_token_type(eltt_blockchain *bc,
                               const char *name,
                               const char *symbol,
                               int decimals,
                               eltt_token_kind kind,
                               double energy_binding_factor)
{
    if (bc->token_count >= ELTT_MAX_TOKEN_TYPES) {
        return -1;
    }
    int idx = (int)bc->token_count;
    eltt_token_type *t = &bc->token_types[idx];
    memset(t, 0, sizeof(*t));
    strncpy(t->name, name, ELTT_MAX_TOKEN_NAME_LEN - 1);
    t->name[ELTT_MAX_TOKEN_NAME_LEN - 1] = '\0';
    strncpy(t->symbol, symbol, ELTT_MAX_TOKEN_SYMBOL_LEN - 1);
    t->symbol[ELTT_MAX_TOKEN_SYMBOL_LEN - 1] = '\0';
    t->decimals = decimals;
    t->kind = kind;
    t->energy_binding_factor = energy_binding_factor;
    bc->token_count++;
    for (size_t i = 0; i < bc->wallet_count; ++i) {
        bc->wallets[i].balances[idx] = 0.0;
        bc->wallets[i].token_count = bc->token_count;
    }
    return idx;
}

/* ----------------------------------------------------------
 * Validierung von Transaktionen
 * ---------------------------------------------------------- */

static int eltt_validate_transaction(const eltt_blockchain *bc, const eltt_transaction *tx)
{
    if (tx->token_index < 0 || (size_t)tx->token_index >= bc->token_count) {
        return 0;
    }
    if (tx->amount < 0.0) {
        return 0;
    }

    int from_idx = eltt_find_wallet_index(bc, tx->from);
    int to_idx   = eltt_find_wallet_index(bc, tx->to);

    switch (tx->kind) {
        case ELTT_TX_KIND_TRANSFER:
        case ELTT_TX_KIND_SWAP:
        case ELTT_TX_KIND_STAKE:
            if (from_idx < 0) return 0;
            if (bc->wallets[from_idx].balances[tx->token_index] < tx->amount) return 0;
            if (tx->amount <= 0.0) return 0;
            break;
        case ELTT_TX_KIND_MINT:
            if (to_idx < 0) return 0;
            if (tx->amount <= 0.0) return 0;
            break;
        case ELTT_TX_KIND_BURN:
            if (from_idx < 0) return 0;
            if (bc->wallets[from_idx].balances[tx->token_index] < tx->amount) return 0;
            if (tx->amount <= 0.0) return 0;
            break;
        case ELTT_TX_KIND_CREATE_TOKEN:
        case ELTT_TX_KIND_CREATE_POOL:
        case ELTT_TX_KIND_ADD_LIQUIDITY:
        case ELTT_TX_KIND_REMOVE_LIQUIDITY:
        case ELTT_TX_KIND_UNSTAKE:
        case ELTT_TX_KIND_CLAIM_REWARDS:
        case ELTT_TX_KIND_PROFILE_UPDATE:
        case ELTT_TX_KIND_GOVERNANCE_PROPOSAL:
            break;
        default:
            return 0;
    }
    return 1;
}

/* ----------------------------------------------------------
 * Anwendung von Transaktionen auf den Zustand
 * ---------------------------------------------------------- */

static void eltt_apply_transaction(eltt_blockchain *bc, const eltt_transaction *tx)
{
    int from_idx = eltt_find_or_create_wallet(bc, tx->from);
    int to_idx   = eltt_find_or_create_wallet(bc, tx->to);

    switch (tx->kind) {
        case ELTT_TX_KIND_TRANSFER:
        case ELTT_TX_KIND_SWAP:
            bc->wallets[from_idx].balances[tx->token_index] -= tx->amount;
            bc->wallets[to_idx].balances[tx->token_index]   += tx->amount;
            break;
        case ELTT_TX_KIND_MINT:
            bc->wallets[to_idx].balances[tx->token_index] += tx->amount;
            break;
        case ELTT_TX_KIND_BURN:
            bc->wallets[from_idx].balances[tx->token_index] -= tx->amount;
            break;
        case ELTT_TX_KIND_STAKE:
        case ELTT_TX_KIND_UNSTAKE:
        case ELTT_TX_KIND_CLAIM_REWARDS:
        case ELTT_TX_KIND_CREATE_TOKEN:
        case ELTT_TX_KIND_CREATE_POOL:
        case ELTT_TX_KIND_ADD_LIQUIDITY:
        case ELTT_TX_KIND_REMOVE_LIQUIDITY:
        case ELTT_TX_KIND_PROFILE_UPDATE:
        case ELTT_TX_KIND_GOVERNANCE_PROPOSAL:
            break;
        default:
            break;
    }
}

/* ----------------------------------------------------------
 * Block-Validierung und Chain-Aufbau
 * ---------------------------------------------------------- */

static int eltt_validate_block(const eltt_blockchain *bc, const eltt_block *block)
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

    eltt_block tmp = *block;
    eltt_compute_block_hash(&tmp);
    if (memcmp(tmp.hash, block->hash, 32) != 0) {
        return 0;
    }

    for (size_t i = 0; i < block->tx_count; ++i) {
        if (!eltt_validate_transaction(bc, &block->txs[i])) {
            return 0;
        }
    }

    return 1;
}

static int eltt_append_block(eltt_blockchain *bc, const eltt_block *block)
{
    if (!eltt_validate_block(bc, block)) {
        return 0;
    }

    eltt_block *new_blocks = (eltt_block *)realloc(bc->blocks, (bc->block_count + 1) * sizeof(eltt_block));
    if (!new_blocks) {
        return 0;
    }
    bc->blocks = new_blocks;
    bc->blocks[bc->block_count] = *block;
    bc->block_count++;

    for (size_t i = 0; i < block->tx_count; ++i) {
        eltt_apply_transaction(bc, &block->txs[i]);
    }

    return 1;
}

/* ----------------------------------------------------------
 * Genesis-Block-Logik (ohne Owner-Hardcoding)
 * ---------------------------------------------------------- */

static void eltt_init_blockchain(eltt_blockchain *bc)
{
    memset(bc, 0, sizeof(*bc));
    bc->blocks = NULL;
    bc->block_count = 0;
    bc->wallet_count = 0;
    bc->token_count = 0;
    bc->pool_count = 0;
    bc->stake_count = 0;

    eltt_add_token_type(bc, "TTTC", "TTTC", 8, ELTT_TOKEN_KIND_TTTC, 0.75);
    eltt_add_token_type(bc, "ELTT", "ELTT", 8, ELTT_TOKEN_KIND_ELTT, 0.75);
    eltt_add_token_type(bc, "ELTC", "ELTC", 8, ELTT_TOKEN_KIND_ELTC, 0.75);
}

static void eltt_build_genesis_block(eltt_block *genesis,
                                     const char *owner_address,
                                     uint64_t timestamp)
{
    memset(genesis, 0, sizeof(*genesis));
    genesis->index = 0;
    genesis->timestamp = timestamp;
    memset(genesis->prev_hash, 0, 32);
    genesis->tx_count = 0;

    eltt_compute_block_hash(genesis);
}

/* ----------------------------------------------------------
 * Öffentliche API-Funktionen (Header-ähnlich)
 * ---------------------------------------------------------- */

void eltt_blockchain_init(eltt_blockchain *bc)
{
    eltt_init_blockchain(bc);
}

void eltt_blockchain_free(eltt_blockchain *bc)
{
    if (bc->blocks) {
        free(bc->blocks);
        bc->blocks = NULL;
    }
    bc->block_count = 0;
}

int eltt_blockchain_add_block(eltt_blockchain *bc, const eltt_block *block)
{
    return eltt_append_block(bc, block);
}

void eltt_blockchain_create_genesis(eltt_blockchain *bc,
                                    const char *owner_address,
                                    uint64_t timestamp)
{
    eltt_block genesis;
    eltt_build_genesis_block(&genesis, owner_address, timestamp);
    eltt_append_block(bc, &genesis);
}

double eltt_blockchain_compute_tx_energy(const eltt_transaction *tx)
{
    return eltt_energy_from_transaction(tx);
}
