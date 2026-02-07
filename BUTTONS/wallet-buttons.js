"use strict";

/*
 * BUTTONS/wallet-buttons.js
 * Wallet-Login-Erkennung, STATE-Integration,
 * deterministische Sichtbarkeit von Create/Settings/Profil.
 */

(function () {
    const OWNER_KEY = "ELTT_OWNER_WALLET_ADDRESS";
    const OWNER_SETTINGS_KEY = "ELTT_OWNER_WALLET_SETTINGS";
    const OWNER_PROFILE_KEY = "ELTT_OWNER_WALLET_PROFILE";

    /* -------------------------
       Hilfsfunktionen
    -------------------------- */

    function qs(sel) {
        return document.querySelector(sel);
    }

    function createElement(tag, attrs, text) {
        const el = document.createElement(tag);
        if (attrs) {
            Object.keys(attrs).forEach((k) => {
                if (k === "class") el.className = attrs[k];
                else el.setAttribute(k, attrs[k]);
            });
        }
        if (text) el.textContent = text;
        return el;
    }

    function getOwnerAddress() {
        return localStorage.getItem(OWNER_KEY) || null;
    }

    function setOwnerAddress(addr) {
        localStorage.setItem(OWNER_KEY, addr);
    }

    function getOwnerSettings() {
        try {
            const raw = localStorage.getItem(OWNER_SETTINGS_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (_) {
            return null;
        }
    }

    function setOwnerSettings(settings) {
        localStorage.setItem(OWNER_SETTINGS_KEY, JSON.stringify(settings));
    }

    function getOwnerProfile() {
        try {
            const raw = localStorage.getItem(OWNER_PROFILE_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (_) {
            return null;
        }
    }

    function setOwnerProfile(profile) {
        localStorage.setItem(OWNER_PROFILE_KEY, JSON.stringify(profile));
    }

    function randomBytes(len) {
        const arr = new Uint8Array(len);
        window.crypto.getRandomValues(arr);
        return arr;
    }

    function simpleHashHex(str) {
        let h1 = 0x811c9dc5;
        for (let i = 0; i < str.length; i++) {
            h1 ^= str.charCodeAt(i);
            h1 = (h1 * 0x01000193) >>> 0;
        }
        return h1.toString(16).padStart(8, "0");
    }

    function deriveAddressFromMnemonic(mnemonic) {
        const hex = simpleHashHex(mnemonic);
        return "ELTT-" + hex.toUpperCase();
    }

    function getWordList() {
        return [
            "alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet","kilo","lima",
            "mike","november","oscar","papa","quebec","romeo","sierra","tango","uniform","victor","whiskey",
            "xray","yankee","zulu","aurora","beacon","candle","dawn","ember","flame","glow","horizon","ion",
            "jade","keystone","lumen","matrix","nova","orbit","pulse","quantum","radial","signal","terra",
            "umbra","vector","wave","zenith","anchor","bridge","cipher","drift","echoes","forge","glyph",
            "harbor","island","junction","kernel","ledger","mirror","node","origin","pillar","quartz","relay",
            "spectrum","token","unity","vault","woven","yield","zen","atlas","binary","circuit","domain",
            "engine","frame","grid","halo","index","key","link","mesh","nexus","optic","path","query","root",
            "stack","trace","uplink","verge","wire","xenon","yard","zenithal"
        ];
    }

    function generateMnemonic() {
        const words = getWordList();
        const bytes = randomBytes(12);
        return Array.from(bytes).map(b => words[b % words.length]).join(" ");
    }

    /* -------------------------
       STATE-Integration (über ELTTBlockchain)
    -------------------------- */

    function persistOwnerInState(address) {
        if (!window.ELTTBlockchain || !window.ELTTBlockchain.withPersistentBlockchain) {
            return;
        }

        window.ELTTBlockchain.withPersistentBlockchain((bc) => {
            // Token-Typen sicherstellen (Genesis, falls leer)
            window.ELTTBlockchain.createGenesis(bc);

            // Wallet anlegen, falls nicht vorhanden
            const w = window.ELTTBlockchain.getWallet(bc, address) ||
                      window.ELTTBlockchain.createWallet(bc, address);

            // Owner-Genesis-Block nur, wenn noch kein Block mit diesem Memo existiert
            const hasOwnerGenesis = bc.blocks.some(
                (b) => b.transactions.some((t) => t.memo === "OWNER-GENESIS" && t.toAddress === address)
            );
            if (!hasOwnerGenesis) {
                const tx = new window.ELTTBlockchain.Transaction(
                    "",
                    address,
                    0.0,
                    0,
                    window.ELTTBlockchain.TxKind.GOVERNANCE,
                    "OWNER-GENESIS"
                );
                window.ELTTBlockchain.computeTxEnergy(tx);
                const ts = Date.now();
                window.ELTTBlockchain.appendBlock(bc, [tx], ts);
            }

            return bc;
        });
    }

    /* -------------------------
       Wallet erzeugen
    -------------------------- */

    function createOwnerWalletIfNeeded() {
        const existing = getOwnerAddress();
        if (existing) return existing;

        const mnemonic = generateMnemonic();
        const addr = deriveAddressFromMnemonic(mnemonic);

        setOwnerAddress(addr);
        setOwnerSettings({
            mnemonic,
            created_at: new Date().toISOString()
        });

        // Persistente Verankerung im Blockchain-STATE
        persistOwnerInState(addr);

        return addr;
    }

    /* -------------------------
       UI: Settings / Profil
    -------------------------- */

    function renderSettingsView() {
        const settings = getOwnerSettings();
        const addr = getOwnerAddress();

        const wrap = createElement("div", null);
        wrap.appendChild(createElement("h3", null, "Wallet Settings"));

        const info = createElement(
            "p",
            null,
            addr ? "Owner‑Wallet ist gesetzt." : "Noch keine Owner‑Wallet gesetzt."
        );
        wrap.appendChild(info);

        const phraseBox = createElement("textarea", { readonly: "readonly" });
        phraseBox.value = settings && settings.mnemonic ? settings.mnemonic : "";
        wrap.appendChild(phraseBox);

        const addrBox = createElement("input", { readonly: "readonly" });
        addrBox.value = addr || "";
        wrap.appendChild(addrBox);

        return wrap;
    }

    function renderProfileView() {
        const profile = getOwnerProfile() || {};

        const wrap = createElement("div", null);
        wrap.appendChild(createElement("h3", null, "Wallet Profil"));

        const userInput = createElement("input", { type: "text" });
        userInput.value = profile.username || "";
        wrap.appendChild(userInput);

        const passInput = createElement("input", { type: "password" });
        wrap.appendChild(passInput);

        const saveBtn = createElement("button", null, "Profil speichern");
        saveBtn.addEventListener("click", () => {
            const username = userInput.value.trim();
            const password = passInput.value;
            if (!username || !password) return;

            setOwnerProfile({
                username,
                password_hash: simpleHashHex(username + ":" + password)
            });
        });

        wrap.appendChild(saveBtn);
        return wrap;
    }

    /* -------------------------
       UI: Buttons
    -------------------------- */

    function injectButtons() {
        const walletSection = qs("#wallet-address-section");
        if (!walletSection) return;

        const addr = getOwnerAddress();

        let btnRow = walletSection.querySelector(".wallet-buttons-row");
        if (!btnRow) {
            btnRow = createElement("div", { class: "wallet-buttons-row" });
            walletSection.appendChild(btnRow);
        }

        // Create Wallet
        if (!addr) {
            const createBtn = createElement("button", null, "Create Wallet");
            createBtn.addEventListener("click", () => {
                const newAddr = createOwnerWalletIfNeeded();
                // optional: Adresse ins Eingabefeld spiegeln, falls vorhanden
                const addrInput = qs("#wallet-address-input");
                if (addrInput) {
                    addrInput.value = newAddr;
                    addrInput.dispatchEvent(new Event("input", { bubbles: true }));
                }
                location.reload();
            });
            btnRow.appendChild(createBtn);
        }

        // Settings
        if (addr) {
            const settingsBtn = createElement("button", null, "Settings");
            settingsBtn.addEventListener("click", () => {
                const view = renderSettingsView();
                // hier könntest du dein Overlay-System einhängen
                alert("Settings öffnen");
            });
            btnRow.appendChild(settingsBtn);
        }

        // Profil
        if (addr) {
            const profileBtn = createElement("button", null, "Profil");
            profileBtn.addEventListener("click", () => {
                const view = renderProfileView();
                // hier könntest du dein Overlay-System einhängen
                alert("Profil öffnen");
            });
            btnRow.appendChild(profileBtn);
        }
    }

    document.addEventListener("DOMContentLoaded", injectButtons);
})();
