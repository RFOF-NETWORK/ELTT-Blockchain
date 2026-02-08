// assets/js/ELTT-Viewer.js
"use strict";

/*
 * ELTT-Viewer.js
 * Read-only Viewer-Parität zur ELTT-Blockchain.
 * - keine Mutationen
 * - keine STATE-Schreiboperationen
 * - nur lesender Zugriff auf den persistenten STATE
 * - JSON-kompatible Sichten
 */

(function () {
    if (!window.ELTTBlockchain) {
        throw new Error("ELTTBlockchain engine not available");
    }

    const {
        loadState,
        blockchainFromState,
        computeTxEnergy,
    } = window.ELTTBlockchain;

    /* -------------------------
       Interner, read-only Snapshot
    -------------------------- */

    function getReadOnlyBlockchain() {
        const state = loadState();
        // Wichtig: KEIN stateFromBlockchain + saveState, nur Rekonstruktion
        const bc = blockchainFromState(state);
        return bc;
    }

    /* -------------------------
       Sichten: Blöcke
    -------------------------- */

    function listBlocksView() {
        const bc = getReadOnlyBlockchain();
        return bc.blocks.map((b) => ({
            index: b.index,
            timestamp: b.timestamp,
            hash: b.hash,
            prevHash: b.prevHash,
            txCount: Array.isArray(b.transactions) ? b.transactions.length : 0,
        }));
    }

    function getBlockDetailsView(blockIndex) {
        const bc = getReadOnlyBlockchain();
        if (blockIndex < 0 || blockIndex >= bc.blocks.length) {
            return null;
        }
        const b = bc.blocks[blockIndex];
        return {
            index: b.index,
            prevHash: b.prevHash,
            timestamp: b.timestamp,
            transactions: b.transactions.map((t) => ({
                fromAddress: t.fromAddress,
                toAddress: t.toAddress,
                amount: t.amount,
                tokenIndex: t.tokenIndex,
                kind: t.kind,
                memo: t.memo,
                energy: t.energy,
            })),
            hash: b.hash,
        };
    }

    /* -------------------------
       Sicht: Transaktions-Energie (synthetisch)
    -------------------------- */

    function simulateTxEnergyView(fromAddress, toAddress, amount, tokenIndex, kind, memo) {
        const tx = new window.ELTTBlockchain.Transaction(
            fromAddress || "",
            toAddress || "",
            typeof amount === "number" ? amount : 0.0,
            typeof tokenIndex === "number" ? tokenIndex : 0,
            kind || window.ELTTBlockchain.TxKind.TRANSFER,
            (memo || "").slice(0, 128)
        );
        const energy = computeTxEnergy(tx);
        return {
            fromAddress: tx.fromAddress,
            toAddress: tx.toAddress,
            amount: tx.amount,
            tokenIndex: tx.tokenIndex,
            kind: tx.kind,
            memo: tx.memo,
            energy: energy,
        };
    }

    /* -------------------------
       Export: reiner Viewer-Namespace
    -------------------------- */

    window.ELTTViewer = Object.freeze({
        listBlocksView,
        getBlockDetailsView,
        simulateTxEnergyView,
    });
})();
