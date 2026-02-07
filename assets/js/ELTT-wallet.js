// assets/js/ELTT-wallet.js

"use strict";

/*
 * Frontend-Wallet-Logik für die ELTT-Blockchain.
 * Deterministisch, auditierbar, paritätisch, souveränitätsfokussiert.
 * Die Owner-Wallet entsteht ausschließlich im Frontend und ist nicht hartkodiert.
 */

const ELTTWallet = (() => {
    const {
        TokenKind,
        TxKind,
        TokenType,
        Wallet,
        Transaction,
        Blockchain,
        initBlockchain,
        createGenesis,
        appendBlock,
        computeTxEnergy,
        createWallet,
        getWallet,
        listWalletTokens,
        buildTransferTx,
    } = window.ELTTBlockchain;

    let blockchain = null;
    let currentWalletAddress = null;

    function ensureBlockchain() {
        if (!blockchain) {
            blockchain = initBlockchain();
            createGenesis(blockchain);
        }
        return blockchain;
    }

    function setCurrentWalletAddress(address) {
        currentWalletAddress = address;
        const bc = ensureBlockchain();
        createWallet(bc, address);
    }

    function getCurrentWalletAddress() {
        return currentWalletAddress;
    }

    function getCurrentWallet() {
        if (!currentWalletAddress) {
            return null;
        }
        const bc = ensureBlockchain();
        return getWallet(bc, currentWalletAddress);
    }

    function getWalletState(address) {
        const bc = ensureBlockchain();
        const w = getWallet(bc, address);
        if (!w) {
            return null;
        }
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
    }

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

    function applyTransferLocally(tx) {
        const bc = ensureBlockchain();
        const from = getWallet(bc, tx.fromAddress);
        const to = getWallet(bc, tx.toAddress);

        if (!from || !to) {
            return;
        }
        if (tx.tokenIndex < 0 || tx.tokenIndex >= from.balances.length) {
            return;
        }

        const idx = tx.tokenIndex;
        const amount = tx.amount;

        if (from.balances[idx] < amount) {
            return;
        }

        from.balances[idx] -= amount;
        to.balances[idx] += amount;
    }

    function commitTransactions(transactions, timestamp) {
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

    function exportState() {
        const bc = ensureBlockchain();
        return JSON.parse(JSON.stringify(bc));
    }

    return Object.freeze({
        TokenKind,
        TxKind,
        TokenType,
        Wallet,
        Transaction,
        Blockchain,
        ensureBlockchain,
        setCurrentWalletAddress,
        getCurrentWalletAddress,
        getCurrentWallet,
        getWalletState,
        buildDeterministicTransfer,
        applyTransferLocally,
        commitTransactions,
        exportState,
    });
})();

window.ELTTWallet = ELTTWallet;
