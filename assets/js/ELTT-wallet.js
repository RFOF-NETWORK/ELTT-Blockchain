// assets/js/ELTT-wallet.js
"use strict";

/*
 * Frontend-Wallet-Logik für die ELTT-Blockchain.
 * Deterministisch, auditierbar, paritätisch, souveränitätsfokussiert.
 * Keine eigene Blockchain, kein eigener STATE.
 * Alle Operationen laufen über ELTTBlockchain.withPersistentBlockchain.
 */

const ELTTWallet = (() => {
    const {
        TokenKind,
        TxKind,
        TokenType,
        Wallet,
        Transaction,
        computeTxEnergy,
        createWallet,
        getWallet,
        listWalletTokens,
        buildTransferTx,
        withPersistentBlockchain,
    } = window.ELTTBlockchain;

    let currentWalletAddress = null;

    /* -------------------------
       Wallet-Adresse (Frontend)
    -------------------------- */

    function setCurrentWalletAddress(address) {
        currentWalletAddress = address;

        // Wallet im persistenten STATE anlegen
        withPersistentBlockchain((bc) => {
            createWallet(bc, address);
            return bc;
        });
    }

    function getCurrentWalletAddress() {
        return currentWalletAddress;
    }

    /* -------------------------
       Wallet-Sichten (read-only)
    -------------------------- */

    function getCurrentWallet() {
        if (!currentWalletAddress) return null;

        return withPersistentBlockchain((bc) => {
            return getWallet(bc, currentWalletAddress) || null;
        });
    }

    function getWalletState(address) {
        return withPersistentBlockchain((bc) => {
            const w = getWallet(bc, address);
            if (!w) return null;

            const tokens = listWalletTokens(w).map(([t, bal]) => ({
                symbol: t.symbol,
                name: t.name,
                kind: t.kind,
                balance: bal,
            }));

            return {
                address: w.address,
                tokens,
            };
        });
    }

    /* -------------------------
       Transaktionen (deterministisch)
    -------------------------- */

    function buildDeterministicTransfer(toAddress, amount, tokenIndex, memo) {
        if (!currentWalletAddress) {
            throw new Error("No current wallet address set.");
        }

        const tx = buildTransferTx(
            currentWalletAddress,
            toAddress,
            amount,
            tokenIndex,
            memo || ""
        );

        computeTxEnergy(tx);
        return tx;
    }

    /* -------------------------
       Commit (persistent)
    -------------------------- */

    function commitTransactions(transactions, timestamp) {
        return withPersistentBlockchain((bc) => {
            const txs = transactions.slice();

            for (const tx of txs) {
                if (!tx.energy || tx.energy === 0.0) {
                    computeTxEnergy(tx);
                }
            }

            // Engine erzeugt Block + persistiert STATE
            return window.ELTTBlockchain.appendBlock(bc, txs, timestamp);
        });
    }

    /* -------------------------
       Export (persistent)
    -------------------------- */

    function exportState() {
        return window.ELTTBlockchain.loadState();
    }

    return Object.freeze({
        TokenKind,
        TxKind,
        TokenType,
        Wallet,
        Transaction,
        setCurrentWalletAddress,
        getCurrentWalletAddress,
        getCurrentWallet,
        getWalletState,
        buildDeterministicTransfer,
        commitTransactions,
        exportState,
    });
})();

window.ELTTWallet = ELTTWallet;
