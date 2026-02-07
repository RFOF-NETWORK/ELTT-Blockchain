// assets/js/ELTT-launcher.js

"use strict";

/*
 * Frontend-Launcher-/DEX-Logik für die ELTT-Blockchain.
 * Deterministisch, auditierbar, paritätisch, souveränitätsfokussiert.
 * Keine Owner-Adresse, keine Seeds, keine privaten Schlüssel im Code.
 * Keine eigene Blockchain, kein eigener STATE.
 * Alle Operationen laufen über ELTTBlockchain.withPersistentBlockchain.
 */

const ELTTLauncher = (() => {
    const {
        TokenKind,
        TxKind,
        TokenType,
        Wallet,
        Transaction,
        LiquidityPool,
        appendBlock,
        computeTxEnergy,
        createPool,
        getPool,
        buildSwapTx,
        buildAddLiquidityTx,
        buildRemoveLiquidityTx,
        withPersistentBlockchain,
    } = window.ELTTBlockchain;

    const { getCurrentWalletAddress } = window.ELTTWallet;

    /* -------------------------
       Pools (persistent)
    -------------------------- */

    function ensurePool(tokenXIndex, tokenYIndex, lpTokenIndex) {
        return withPersistentBlockchain((bc) => {
            for (let i = 0; i < bc.pools.length; i++) {
                const p = bc.pools[i];
                if (
                    p.tokenXIndex === tokenXIndex &&
                    p.tokenYIndex === tokenYIndex &&
                    p.lpTokenIndex === lpTokenIndex
                ) {
                    return { pool: p, index: i };
                }
            }
            const pool = createPool(bc, tokenXIndex, tokenYIndex, lpTokenIndex);
            return { pool, index: bc.pools.length - 1 };
        });
    }

    /* -------------------------
       Transaktions-Builder (deterministisch)
    -------------------------- */

    function buildDeterministicSwapTx(toAddress, amountIn, tokenInIndex, memo) {
        const fromAddress = getCurrentWalletAddress();
        if (!fromAddress) {
            throw new Error("No current wallet address set for swap.");
        }
        const tx = buildSwapTx(
            fromAddress,
            toAddress,
            amountIn,
            tokenInIndex,
            memo || ""
        );
        computeTxEnergy(tx);
        return tx;
    }

    function buildDeterministicAddLiquidityTx(poolAddress, amountX, tokenXIndex, memo) {
        const fromAddress = getCurrentWalletAddress();
        if (!fromAddress) {
            throw new Error("No current wallet address set for add-liquidity.");
        }
        const tx = buildAddLiquidityTx(
            fromAddress,
            poolAddress,
            amountX,
            tokenXIndex,
            memo || ""
        );
        computeTxEnergy(tx);
        return tx;
    }

    function buildDeterministicRemoveLiquidityTx(poolAddress, amountLp, lpTokenIndex, memo) {
        const fromAddress = getCurrentWalletAddress();
        if (!fromAddress) {
            throw new Error("No current wallet address set for remove-liquidity.");
        }
        const tx = buildRemoveLiquidityTx(
            fromAddress,
            poolAddress,
            amountLp,
            lpTokenIndex,
            memo || ""
        );
        computeTxEnergy(tx);
        return tx;
    }

    /* -------------------------
       Lokale DEX-Effekte (persistent im Engine-STATE)
    -------------------------- */

    function applyAddLiquidityLocally(poolIndex, amountX, amountY) {
        return withPersistentBlockchain((bc) => {
            const pool = getPool(bc, poolIndex);
            if (!pool) {
                return null;
            }
            pool.reserveX += amountX;
            pool.reserveY += amountY;
            return {
                tokenXIndex: pool.tokenXIndex,
                tokenYIndex: pool.tokenYIndex,
                lpTokenIndex: pool.lpTokenIndex,
                reserveX: pool.reserveX,
                reserveY: pool.reserveY,
            };
        });
    }

    function applyRemoveLiquidityLocally(poolIndex, shareX, shareY) {
        return withPersistentBlockchain((bc) => {
            const pool = getPool(bc, poolIndex);
            if (!pool) {
                return null;
            }
            pool.reserveX -= shareX;
            pool.reserveY -= shareY;
            if (pool.reserveX < 0.0) pool.reserveX = 0.0;
            if (pool.reserveY < 0.0) pool.reserveY = 0.0;
            return {
                tokenXIndex: pool.tokenXIndex,
                tokenYIndex: pool.tokenYIndex,
                lpTokenIndex: pool.lpTokenIndex,
                reserveX: pool.reserveX,
                reserveY: pool.reserveY,
            };
        });
    }

    /* -------------------------
       Commit (persistent)
    -------------------------- */

    function commitDexTransactions(transactions, timestamp) {
        return withPersistentBlockchain((bc) => {
            const txs = transactions.slice();
            for (const tx of txs) {
                if (!tx.energy || tx.energy === 0.0) {
                    computeTxEnergy(tx);
                }
            }
            const block = appendBlock(bc, txs, timestamp);
            return {
                index: block.index,
                prevHash: block.prevHash,
                timestamp: block.timestamp,
                hash: block.hash,
            };
        });
    }

    /* -------------------------
       Export (read-only Sicht)
    -------------------------- */

    function exportDexState() {
        return withPersistentBlockchain((bc) => {
            return {
                pools: bc.pools.map((p, idx) => ({
                    index: idx,
                    tokenXIndex: p.tokenXIndex,
                    tokenYIndex: p.tokenYIndex,
                    lpTokenIndex: p.lpTokenIndex,
                    reserveX: p.reserveX,
                    reserveY: p.reserveY,
                })),
                blocks: bc.blocks.map((b) => ({
                    index: b.index,
                    prevHash: b.prevHash,
                    timestamp: b.timestamp,
                    hash: b.hash,
                })),
            };
        });
    }

    return Object.freeze({
        ensurePool,
        buildDeterministicSwapTx,
        buildDeterministicAddLiquidityTx,
        buildDeterministicRemoveLiquidityTx,
        applyAddLiquidityLocally,
        applyRemoveLiquidityLocally,
        commitDexTransactions,
        exportDexState,
    });
})();

window.ELTTLauncher = ELTTLauncher;
