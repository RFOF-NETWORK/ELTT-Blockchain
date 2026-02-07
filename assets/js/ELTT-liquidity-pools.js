// assets/js/ELTT-liquidity-pools.js

"use strict";

/*
 * Frontend-Liquidity-Pool-Logik für die ELTT-Blockchain.
 * Deterministisch, auditierbar, paritätisch, souveränitätsfokussiert.
 * Keine Owner-Adresse, keine Seeds, keine privaten Schlüssel im Code.
 */

const ELTTLiquidityPools = (() => {
    const {
        LiquidityPool,
        Blockchain,
        initBlockchain,
        createGenesis,
        appendBlock,
        computeTxEnergy,
        createPool,
        getPool,
        buildAddLiquidityTx,
        buildRemoveLiquidityTx,
    } = window.ELTTBlockchain;

    const { ensureBlockchain, getCurrentWalletAddress } = window.ELTTWallet;

    function ensurePool(bc, tokenXIndex, tokenYIndex, lpTokenIndex) {
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
    }

    function getPoolState(poolIndex) {
        const bc = ensureBlockchain();
        const pool = getPool(bc, poolIndex);
        if (!pool) {
            return null;
        }
        return {
            index: poolIndex,
            tokenXIndex: pool.tokenXIndex,
            tokenYIndex: pool.tokenYIndex,
            lpTokenIndex: pool.lpTokenIndex,
            reserveX: pool.reserveX,
            reserveY: pool.reserveY,
        };
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

    function applyAddLiquidityLocally(poolIndex, amountX, amountY) {
        const bc = ensureBlockchain();
        const pool = getPool(bc, poolIndex);
        if (!pool) {
            return;
        }
        pool.reserveX += amountX;
        pool.reserveY += amountY;
    }

    function applyRemoveLiquidityLocally(poolIndex, shareX, shareY) {
        const bc = ensureBlockchain();
        const pool = getPool(bc, poolIndex);
        if (!pool) {
            return;
        }
        pool.reserveX -= shareX;
        pool.reserveY -= shareY;
        if (pool.reserveX < 0.0) {
            pool.reserveX = 0.0;
        }
        if (pool.reserveY < 0.0) {
            pool.reserveY = 0.0;
        }
    }

    function commitPoolTransactions(transactions, timestamp) {
        const bc = ensureBlockchain();
        const txs = transactions.slice();
        for (const tx of txs) {
            if (!tx.energy || tx.energy === 0.0) {
                computeTxEnergy(tx);
            }
        }
        const block = appendBlock(bc, txs, timestamp);
        return block;
    }

    function exportPoolState() {
        const bc = ensureBlockchain();
        return JSON.parse(JSON.stringify(bc.pools));
    }

    return Object.freeze({
        ensurePool,
        getPoolState,
        buildDeterministicAddLiquidityTx,
        buildDeterministicRemoveLiquidityTx,
        applyAddLiquidityLocally,
        applyRemoveLiquidityLocally,
        commitPoolTransactions,
        exportPoolState,
    });
})();

window.ELTTLiquidityPools = ELTTLiquidityPools;
