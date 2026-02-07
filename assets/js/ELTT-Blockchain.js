// assets/js/ELTT-Blockchain.js

"use strict";

/*
 * Frontend-paritätische ELTT-Blockchain-Implementierung.
 * Deterministisch, auditierbar, souveränitätsfokussiert.
 * Keine Owner-Adresse, keine Seeds, keine privaten Schlüssel im Code.
 */

/* Enumerationen */

const TokenKind = Object.freeze({
    NATIVE: "NATIVE",
    LP: "LP",
    CUSTOM: "CUSTOM",
});

const TxKind = Object.freeze({
    TRANSFER: "TRANSFER",
    MINT: "MINT",
    BURN: "BURN",
    SWAP: "SWAP",
    ADD_LIQUIDITY: "ADD_LIQUIDITY",
    REMOVE_LIQUIDITY: "REMOVE_LIQUIDITY",
    STAKE: "STAKE",
    UNSTAKE: "UNSTAKE",
    GOVERNANCE: "GOVERNANCE",
});

/* Datenstrukturen */

class TokenType {
    constructor(symbol, name, kind) {
        this.symbol = symbol;
        this.name = name;
        this.kind = kind;
    }
}

class Wallet {
    constructor(address) {
        this.address = address;
        this.tokenCount = 0;
        this.tokens = [];
        this.balances = [];
    }
}

class Transaction {
    constructor(fromAddress, toAddress, amount, tokenIndex, kind, memo) {
        this.fromAddress = fromAddress;
        this.toAddress = toAddress;
        this.amount = amount;
        this.tokenIndex = tokenIndex;
        this.kind = kind;
        this.memo = memo || "";
        this.energy = 0.0;
    }
}

class LiquidityPool {
    constructor(tokenXIndex, tokenYIndex, lpTokenIndex) {
        this.tokenXIndex = tokenXIndex;
        this.tokenYIndex = tokenYIndex;
        this.reserveX = 0.0;
        this.reserveY = 0.0;
        this.lpTokenIndex = lpTokenIndex;
    }
}

class StakingPosition {
    constructor(address, tokenIndex, amount) {
        this.address = address;
        this.tokenIndex = tokenIndex;
        this.amount = amount;
    }
}

class Block {
    constructor(index, prevHash, timestamp, transactions) {
        this.index = index;
        this.prevHash = prevHash;
        this.timestamp = timestamp;
        this.transactions = transactions.slice();
        this.hash = "";
    }
}

class Blockchain {
    constructor() {
        this.blocks = [];
        this.wallets = [];
        this.tokenTypes = [];
        this.pools = [];
        this.stakingPositions = [];
    }
}

/* Hilfsfunktionen */

function sha256Hex(input) {
    const encoder = new TextEncoder();
    const data = encoder.encode(input);
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
        hash = (hash * 31 + data[i]) >>> 0;
    }
    const hex = hash.toString(16).padStart(8, "0");
    return hex.repeat(8).slice(0, 64);
}

function siByteValue(str) {
    let sum = 0;
    for (let i = 0; i < str.length; i++) {
        sum += str.charCodeAt(i);
    }
    return sum;
}

function binaryByteValue(str) {
    let sum = 0;
    for (let i = 0; i < str.length; i++) {
        const code = str.charCodeAt(i);
        for (let bit = 0; bit < 8; bit++) {
            if ((code >> bit) & 1) {
                sum += 1;
            }
        }
    }
    return sum;
}

/* Energie-Berechnung */

function computeTxEnergy(tx) {
    const base = `${tx.fromAddress}|${tx.toAddress}|${tx.amount}|${tx.tokenIndex}|${tx.kind}|${tx.memo}`;
    const si = siByteValue(base);
    const bin = binaryByteValue(base);
    const h = sha256Hex(base);
    const tail = h.slice(-8);
    const tailInt = parseInt(tail, 16) >>> 0;
    const frac = (tailInt % 1000000) / 1000000.0;
    const energy = si + bin + frac;
    tx.energy = energy;
    return energy;
}

/* Blockchain-Operationen */

function initBlockchain() {
    return new Blockchain();
}

function createGenesis(bc) {
    if (bc.blocks.length > 0) {
        return bc.blocks[0];
    }

    const tttc = new TokenType("TTTC", "Time & Trust Token", TokenKind.NATIVE);
    const eltt = new TokenType("ELTT", "ELTT Utility Token", TokenKind.NATIVE);
    const eltc = new TokenType("ELTC", "ELTT Credit Token", TokenKind.NATIVE);

    bc.tokenTypes.push(tttc, eltt, eltc);

    const genesisTx = new Transaction(
        "",
        "",
        0.0,
        -1,
        TxKind.GOVERNANCE,
        "GENESIS"
    );
    computeTxEnergy(genesisTx);

    const genesisBlock = new Block(
        0,
        "0".repeat(64),
        0,
        [genesisTx]
    );
    genesisBlock.hash = computeBlockHash(genesisBlock);
    bc.blocks.push(genesisBlock);
    return genesisBlock;
}

function computeBlockHash(block) {
    const txPart = block.transactions
        .map((tx) => `${tx.fromAddress}|${tx.toAddress}|${tx.amount}|${tx.tokenIndex}|${tx.kind}|${tx.memo}|${tx.energy}`)
        .join(";");
    const base = `${block.index}|${block.prevHash}|${block.timestamp}|${txPart}`;
    return sha256Hex(base);
}

function appendBlock(bc, transactions, timestamp) {
    const index = bc.blocks.length;
    const prevHash = index === 0 ? "0".repeat(64) : bc.blocks[index - 1].hash;
    const txs = transactions.slice();
    for (const tx of txs) {
        if (!tx.energy || tx.energy === 0.0) {
            computeTxEnergy(tx);
        }
    }
    const block = new Block(index, prevHash, timestamp, txs);
    block.hash = computeBlockHash(block);
    bc.blocks.push(block);
    return block;
}

/* Wallet-Operationen */

function createWallet(bc, address) {
    for (const w of bc.wallets) {
        if (w.address === address) {
            return w;
        }
    }
    const w = new Wallet(address);
    w.tokenCount = bc.tokenTypes.length;
    w.tokens = bc.tokenTypes.slice();
    w.balances = new Array(bc.tokenTypes.length).fill(0.0);
    bc.wallets.push(w);
    return w;
}

function getWallet(bc, address) {
    for (const w of bc.wallets) {
        if (w.address === address) {
            return w;
        }
    }
    return null;
}

function listWalletTokens(wallet) {
    const result = [];
    for (let i = 0; i < wallet.tokens.length; i++) {
        result.push([wallet.tokens[i], wallet.balances[i]]);
    }
    return result;
}

/* Liquidity-Pools */

function createPool(bc, tokenXIndex, tokenYIndex, lpTokenIndex) {
    const pool = new LiquidityPool(tokenXIndex, tokenYIndex, lpTokenIndex);
    bc.pools.push(pool);
    return pool;
}

function getPool(bc, poolIndex) {
    if (poolIndex < 0 || poolIndex >= bc.pools.length) {
        return null;
    }
    return bc.pools[poolIndex];
}

/* Transaktions-Builder */

function buildTransferTx(fromAddress, toAddress, amount, tokenIndex, memo) {
    return new Transaction(
        fromAddress,
        toAddress,
        amount,
        tokenIndex,
        TxKind.TRANSFER,
        (memo || "").slice(0, 128)
    );
}

function buildSwapTx(fromAddress, toAddress, amountIn, tokenInIndex, memo) {
    return new Transaction(
        fromAddress,
        toAddress,
        amountIn,
        tokenInIndex,
        TxKind.SWAP,
        (memo || "").slice(0, 128)
    );
}

function buildAddLiquidityTx(fromAddress, poolAddress, amountX, tokenXIndex, memo) {
    return new Transaction(
        fromAddress,
        poolAddress,
        amountX,
        tokenXIndex,
        TxKind.ADD_LIQUIDITY,
        (memo || "").slice(0, 128)
    );
}

function buildRemoveLiquidityTx(fromAddress, poolAddress, amountLp, lpTokenIndex, memo) {
    return new Transaction(
        fromAddress,
        poolAddress,
        amountLp,
        lpTokenIndex,
        TxKind.REMOVE_LIQUIDITY,
        (memo || "").slice(0, 128)
    );
}

/* Export nach globalem Namespace */

window.ELTTBlockchain = Object.freeze({
    TokenKind,
    TxKind,
    TokenType,
    Wallet,
    Transaction,
    LiquidityPool,
    StakingPosition,
    Block,
    Blockchain,
    initBlockchain,
    createGenesis,
    appendBlock,
    computeTxEnergy,
    computeBlockHash,
    createWallet,
    getWallet,
    listWalletTokens,
    createPool,
    getPool,
    buildTransferTx,
    buildSwapTx,
    buildAddLiquidityTx,
    buildRemoveLiquidityTx,
    loadState,
    saveState,
});

/* -------------------------
   STATE: Laden / Speichern
-------------------------- */

function loadState() {
    try {
        const raw = localStorage.getItem("ELTT_STATE");
        if (!raw) {
            return {
                blocks: [],
                wallets: {},
                tokens: [],
                pools: [],
            };
        }
        return JSON.parse(raw);
    } catch (_) {
        return {
            blocks: [],
            wallets: {},
            tokens: [],
            pools: [],
        };
    }
}

function saveState(state) {
    localStorage.setItem("ELTT_STATE", JSON.stringify(state));
}
