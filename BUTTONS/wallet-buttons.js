// BUTTONS/wallet-buttons.js

"use strict";

/*
 * Zusätzliche Wallet-Buttons (Create Wallet, Settings, Profil)
 * Rein frontend-basiert, deterministisch, souveränitätsfokussiert.
 * Keine Änderung bestehender Dateien erforderlich.
 */

(function () {
    const OWNER_KEY = "ELTT_OWNER_WALLET_ADDRESS";
    const OWNER_SETTINGS_KEY = "ELTT_OWNER_WALLET_SETTINGS";
    const OWNER_PROFILE_KEY = "ELTT_OWNER_WALLET_PROFILE";

    function qs(sel) {
        return document.querySelector(sel);
    }

    function createElement(tag, attrs, text) {
        const el = document.createElement(tag);
        if (attrs) {
            Object.keys(attrs).forEach((k) => {
                if (k === "class") {
                    el.className = attrs[k];
                } else if (k === "style") {
                    el.setAttribute("style", attrs[k]);
                } else {
                    el.setAttribute(k, attrs[k]);
                }
            });
        }
        if (text) {
            el.textContent = text;
        }
        return el;
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

    function getOwnerAddress() {
        return localStorage.getItem(OWNER_KEY) || null;
    }

    function setOwnerAddress(addr) {
        localStorage.setItem(OWNER_KEY, addr);
    }

    function randomBytes(len) {
        const arr = new Uint8Array(len);
        if (window.crypto && window.crypto.getRandomValues) {
            window.crypto.getRandomValues(arr);
        } else {
            for (let i = 0; i < len; i++) {
                arr[i] = Math.floor(Math.random() * 256);
            }
        }
        return arr;
    }

    function bytesToHex(bytes) {
        return Array.from(bytes)
            .map((b) => b.toString(16).padStart(2, "0"))
            .join("");
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
        const out = [];
        const bytes = randomBytes(12);
        for (let i = 0; i < 12; i++) {
            const idx = bytes[i] % words.length;
            out.push(words[idx]);
        }
        return out.join(" ");
    }

    function downloadTextFile(filename, content) {
        const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function ensureOverlay() {
        let overlay = qs("#wallet-buttons-overlay");
        if (!overlay) {
            overlay = createElement("div", {
                id: "wallet-buttons-overlay",
                style: "position:fixed;inset:0;background:rgba(15,23,42,0.85);display:none;z-index:9999;align-items:center;justify-content:center;"
            });
            const inner = createElement("div", {
                id: "wallet-buttons-overlay-inner",
                style: "background:#020617;border:1px solid #1f2937;border-radius:12px;padding:16px;max-width:420px;width:90%;color:#e5e7eb;font-size:0.9rem;"
            });
            const closeBtn = createElement("button", {
                type: "button",
                style: "float:right;background:#111827;border:1px solid #374151;border-radius:999px;padding:2px 10px;font-size:0.75rem;color:#e5e7eb;cursor:pointer;"
            }, "×");
            closeBtn.addEventListener("click", () => {
                overlay.style.display = "none";
            });
            inner.appendChild(closeBtn);
            inner.appendChild(createElement("div", { id: "wallet-buttons-overlay-content" }));
            overlay.appendChild(inner);
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    function showOverlay(contentNode) {
        const overlay = ensureOverlay();
        const content = qs("#wallet-buttons-overlay-content");
        content.innerHTML = "";
        content.appendChild(contentNode);
        overlay.style.display = "flex";
    }

    function renderSettingsView() {
        const settings = getOwnerSettings();
        const ownerAddr = getOwnerAddress();

        const wrap = createElement("div", null);
        wrap.appendChild(createElement("h3", { style: "margin:0 0 8px 0;font-size:1rem;" }, "Wallet Settings"));

        const info = createElement("p", { style: "margin:4px 0 8px 0;" });
        info.textContent = ownerAddr
            ? "Owner‑Wallet ist gesetzt. Du kannst deine Phrase und Einstellungen verwalten."
            : "Noch keine Owner‑Wallet gesetzt. Erzeuge zuerst eine Wallet.";
        wrap.appendChild(info);

        const phraseBox = createElement("textarea", {
            readonly: "readonly",
            style: "width:100%;min-height:80px;background:#020617;border:1px solid #374151;border-radius:8px;padding:6px;color:#e5e7eb;font-size:0.8rem;resize:vertical;margin-bottom:8px;"
        });
        phraseBox.value = settings && settings.mnemonic ? settings.mnemonic : "";
        wrap.appendChild(phraseBox);

        const addrBox = createElement("input", {
            type: "text",
            readonly: "readonly",
            style: "width:100%;background:#020617;border:1px solid #374151;border-radius:8px;padding:6px;color:#e5e7eb;font-size:0.8rem;margin-bottom:8px;"
        });
        addrBox.value = ownerAddr || "";
        wrap.appendChild(addrBox);

        const btnRow = createElement("div", { style: "display:flex;gap:8px;flex-wrap:wrap;margin-top:4px;" });

        const dlBtn = createElement("button", {
            type: "button",
            style: "background:#1d4ed8;border:none;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;"
        }, "Settings als Datei speichern");
        dlBtn.addEventListener("click", () => {
            if (!settings || !ownerAddr) {
                return;
            }
            const payload = {
                address: ownerAddr,
                mnemonic: settings.mnemonic,
                created_at: settings.created_at,
                is_owner: true
            };
            const ts = new Date().toISOString().replace(/[:.]/g, "-");
            downloadTextFile("ELTT-WALLET-SETTINGS-" + ts + ".txt", JSON.stringify(payload, null, 2));
        });

        const clearBtn = createElement("button", {
            type: "button",
            style: "background:#111827;border:1px solid #374151;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;"
        }, "Lokale Settings löschen");
        clearBtn.addEventListener("click", () => {
            localStorage.removeItem(OWNER_SETTINGS_KEY);
            phraseBox.value = "";
        });

        btnRow.appendChild(dlBtn);
        btnRow.appendChild(clearBtn);
        wrap.appendChild(btnRow);

        return wrap;
    }

    function renderProfileView() {
        const profile = getOwnerProfile() || {};
        const wrap = createElement("div", null);
        wrap.appendChild(createElement("h3", { style: "margin:0 0 8px 0;font-size:1rem;" }, "Wallet Profil"));

        const userLabel = createElement("label", { style: "display:block;font-size:0.8rem;margin-bottom:2px;" }, "Benutzername");
        const userInput = createElement("input", {
            type: "text",
            style: "width:100%;background:#020617;border:1px solid #374151;border-radius:8px;padding:6px;color:#e5e7eb;font-size:0.8rem;margin-bottom:8px;"
        });
        userInput.value = profile.username || "";

        const passLabel = createElement("label", { style: "display:block;font-size:0.8rem;margin-bottom:2px;" }, "Passwort (wird lokal gespeichert)");
        const passInput = createElement("input", {
            type: "password",
            style: "width:100%;background:#020617;border:1px solid #374151;border-radius:8px;padding:6px;color:#e5e7eb;font-size:0.8rem;margin-bottom:8px;"
        });

        const info = createElement("p", { style: "margin:4px 0 8px 0;font-size:0.75rem;color:#9ca3af;" },
            "Profil‑Daten werden ausschließlich lokal im Browser gespeichert und nicht an ein Backend übertragen.");

        const btnRow = createElement("div", { style: "display:flex;gap:8px;flex-wrap:wrap;margin-top:4px;" });

        const saveBtn = createElement("button", {
            type: "button",
            style: "background:#1d4ed8;border:none;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;"
        }, "Profil speichern");
        saveBtn.addEventListener("click", () => {
            const username = (userInput.value || "").trim();
            const password = passInput.value || "";
            if (!username || !password) {
                return;
            }
            const profileObj = {
                username,
                password_hash: simpleHashHex(username + ":" + password)
            };
            setOwnerProfile(profileObj);
            passInput.value = "";
        });

        const clearBtn = createElement("button", {
            type: "button",
            style: "background:#111827;border:1px solid #374151;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;"
        }, "Profil löschen");
        clearBtn.addEventListener("click", () => {
            localStorage.removeItem(OWNER_PROFILE_KEY);
            userInput.value = "";
            passInput.value = "";
        });

        btnRow.appendChild(saveBtn);
        btnRow.appendChild(clearBtn);

        wrap.appendChild(userLabel);
        wrap.appendChild(userInput);
        wrap.appendChild(passLabel);
        wrap.appendChild(passInput);
        wrap.appendChild(info);
        wrap.appendChild(btnRow);

        return wrap;
    }

    function createOwnerWalletIfNeeded() {
        const existingOwner = getOwnerAddress();
        if (existingOwner) {
            return existingOwner;
        }
        const mnemonic = generateMnemonic();
        const addr = deriveAddressFromMnemonic(mnemonic);
        setOwnerAddress(addr);
        setOwnerSettings({
            mnemonic,
            created_at: new Date().toISOString()
        });
        try {
            if (window.ELTTWallet && typeof window.ELTTWallet.setCurrentWalletAddress === "function") {
                window.ELTTWallet.setCurrentWalletAddress(addr);
            }
        } catch (_) {
        }
        const addrInput = qs("#wallet-address-input");
        if (addrInput) {
            addrInput.value = addr;
        }
        const evt = new Event("input", { bubbles: true });
        if (addrInput) {
            addrInput.dispatchEvent(evt);
        }
        return addr;
    }

    function renderCreateWalletOverlay() {
        const wrap = createElement("div", null);
        wrap.appendChild(createElement("h3", { style: "margin:0 0 8px 0;font-size:1rem;" }, "Owner‑Wallet erzeugen"));

        const info = createElement("p", { style: "margin:4px 0 8px 0;" },
            "Du bist der erste, der diese Owner‑Wallet auf diesem Gerät erzeugt. Die Seed‑Phrase wird nur hier angezeigt und lokal gespeichert, nicht im Backend.");

        const createBtn = createElement("button", {
            type: "button",
            style: "background:#1d4ed8;border:none;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;margin-bottom:8px;"
        }, "Owner‑Wallet jetzt erzeugen");

        const phraseBox = createElement("textarea", {
            readonly: "readonly",
            style: "width:100%;min-height:80px;background:#020617;border:1px solid #374151;border-radius:8px;padding:6px;color:#e5e7eb;font-size:0.8rem;resize:vertical;margin-bottom:8px;display:none;"
        });

        const addrBox = createElement("input", {
            type: "text",
            readonly: "readonly",
            style: "width:100%;background:#020617;border:1px solid #374151;border-radius:8px;padding:6px;color:#e5e7eb;font-size:0.8rem;margin-bottom:8px;display:none;"
        });

        const dlBtn = createElement("button", {
            type: "button",
            style: "background:#111827;border:1px solid #374151;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;display:none;"
        }, "Seed‑Settings als Datei speichern");

        createBtn.addEventListener("click", () => {
            const addr = createOwnerWalletIfNeeded();
            const settings = getOwnerSettings();
            phraseBox.style.display = "block";
            addrBox.style.display = "block";
            dlBtn.style.display = "inline-flex";
            phraseBox.value = settings && settings.mnemonic ? settings.mnemonic : "";
            addrBox.value = addr || "";
        });

        dlBtn.addEventListener("click", () => {
            const addr = getOwnerAddress();
            const settings = getOwnerSettings();
            if (!addr || !settings) {
                return;
            }
            const payload = {
                address: addr,
                mnemonic: settings.mnemonic,
                created_at: settings.created_at,
                is_owner: true
            };
            const ts = new Date().toISOString().replace(/[:.]/g, "-");
            downloadTextFile("ELTT-OWNER-GENESIS-" + ts + ".txt", JSON.stringify(payload, null, 2));
        });

        wrap.appendChild(info);
        wrap.appendChild(createBtn);
        wrap.appendChild(phraseBox);
        wrap.appendChild(addrBox);
        wrap.appendChild(dlBtn);

        return wrap;
    }

    function injectButtons() {
        const walletSection = qs("#wallet-address-section");
        if (!walletSection) {
            return;
        }

        let btnRow = walletSection.querySelector(".wallet-buttons-row");
        if (!btnRow) {
            btnRow = createElement("div", {
                class: "wallet-buttons-row",
                style: "display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;"
            });
            walletSection.appendChild(btnRow);
        }

        const createBtn = createElement("button", {
            type: "button",
            style: "background:#1d4ed8;border:none;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;"
        }, "Create Wallet");
        createBtn.addEventListener("click", () => {
            const view = renderCreateWalletOverlay();
            showOverlay(view);
        });

        const settingsBtn = createElement("button", {
            type: "button",
            style: "background:#111827;border:1px solid #374151;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;"
        }, "Settings");
        settingsBtn.addEventListener("click", () => {
            const view = renderSettingsView();
            showOverlay(view);
        });

        const profileBtn = createElement("button", {
            type: "button",
            style: "background:#111827;border:1px solid #374151;border-radius:999px;padding:6px 12px;font-size:0.8rem;color:#e5e7eb;cursor:pointer;"
        }, "Profil");
        profileBtn.addEventListener("click", () => {
            const view = renderProfileView();
            showOverlay(view);
        });

        btnRow.appendChild(createBtn);
        btnRow.appendChild(settingsBtn);
        btnRow.appendChild(profileBtn);
    }

    document.addEventListener("DOMContentLoaded", injectButtons);
})();
