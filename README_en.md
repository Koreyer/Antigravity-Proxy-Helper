<p align="center">
  <img src="icon.png" alt="Antigravity Proxy Helper" width="120"/>
</p>

<h1 align="center">Antigravity Proxy Helper</h1>

<p align="center">
  <b>🚀 Built for Antigravity & Antigravity IDE — no TUN mode, no Global mode, works in Rule mode through Clash Verge</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg" alt="Platform"/>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/Clash%20Verge-Rev-8A2BE2.svg" alt="Clash Verge"/>
  <img src="https://img.shields.io/badge/TUN-not%20required-brightgreen.svg" alt="No TUN"/>
</p>

<p align="center">
  <a href="README.md">🇨🇳 中文</a> | 🇬🇧 English
</p>

---

## ✨ What is this?

A one-click helper that makes **Antigravity / Antigravity IDE** work through **Clash Verge**.

> 🎉 **No TUN mode, no Global mode needed** — just keep Clash in Rule mode with system proxy on.
> 🖱️ **Foolproof one-click flow**: run → click **🛠️ Setup Clash profile** once → restart Clash Verge → open Antigravity. Done.

### Why did you need TUN before? This tool bypasses it

| Traffic | Uses system proxy | Note |
| --- | --- | --- |
| Antigravity UI (Electron) | ✅ Yes | works already |
| Language server `language_server*.exe` (a Go program) | ❌ No | only reads `HTTP_PROXY/HTTPS_PROXY` env vars (TUN used to be the only way) |
| Model requests (Gemini) | — | exit region must not be Hong Kong / mainland China / Russia, etc. |

This tool configures your **environment variables**, **Antigravity settings**, and **Clash routing rules** automatically — so TUN and Global mode are no longer needed.

### 🎁 Highlights

- 🎯 **One-time setup button**: env vars + Antigravity settings + Clash profile all applied permanently — **run it once, no need to keep the tool open**
- 🛠️ **One-click Clash setup** (first run only): reads your current subscription → **makes a copy** (your original profile stays untouched) → injects process/domain rules + the `🤖 Antigravity` group (auto-selects **all nodes from supported regions**, excluding HK/RU and other unsupported regions)
- 🌐 **Automatic proxy setup**: writes `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` env vars + Antigravity `settings.json` on startup
- 🧹 **Optional auto restore on exit**: restores env vars + removes `http.proxy` when you close the app (can be disabled)
- 🔌 **Editable endpoint**: defaults to `127.0.0.1:7897`, change it anytime (saved automatically)
- 🌍 **Bilingual UI**: switch Chinese/English in one click; English-only Clash configs are fully supported
- ♻️ **Safe & repeatable**: only the copied profile is modified; re-running never duplicates configs; backups are created before changes

---

## 🚀 Quick Start (3 steps)

1. **Start Clash Verge** (Rule mode)
2. Run **`AntigravityProxyHelper.exe`** → click **🛠️ Setup Clash profile** (**first run only**; click again after changing/updating your subscription)
   - If Clash Verge is running, the tool will **close and reopen it automatically** (so the new profile is never overwritten)
3. Click **▶ Launch Antigravity** or open Antigravity manually

> 🎯 **Just want to configure once and never open this tool again?** Click **🎯 One-time setup**: env vars + Antigravity settings + Clash profile are all applied permanently and survive closing the tool.
> 💡 Everyday use afterwards: open Clash Verge → open Antigravity (no need to run the helper every time).

---

## 🔘 Buttons

| Button | What it does |
| --- | --- |
| 🚀 **Apply proxy now** | Writes the current host/port into env vars and Antigravity settings (runs automatically on startup; click it after changing the port) |
| 🎯 **One-time setup** | Permanently applies everything (env vars + Antigravity settings + Clash setup); **no need to run this tool again** |
| 🧹 **Restore proxy settings** | Full undo: restores env vars + removes `http.proxy` from Antigravity `settings.json`; also runs on exit if the checkbox is on |
| 🛠️ **Setup Clash profile** | Copies your current subscription as `name (Antigravity)`, injects rules + proxy group, and sets it as the current profile (first run only) |
| 🔌 **Test connection** | Checks whether the Clash port is reachable |
| ▶ **Launch ...** | Starts Antigravity with the proxy environment applied |

---

## ❓ FAQ

- **Setup done but nothing changed?** Make sure you are on the new profile `name (Antigravity)` in Clash Verge; restart Antigravity if it was already running.
- **Do I need to run the Clash setup every time?** No — **the first time only**; click it again only after changing/updating your subscription.
- **What does closing the tool restore?** With "restore on exit" checked: env vars are restored and `http.proxy` is removed from Antigravity `settings.json`. Uncheck it (or use **🎯 One-time setup**) to keep everything permanently.
- **Why did setup close/restart my Clash Verge?** Clash keeps its profile list in memory; writing it while Clash is running can be overwritten on exit. The tool closes Clash, writes safely, then reopens it automatically.
- **Why are there no Hong Kong nodes in the group?** Gemini is not available in Hong Kong; they are filtered out automatically.
- **Antigravity shows `Agent execution terminated due to error`?** Usually caused by an interrupted long-lived stream (unstable node) or a Google-side issue: **switch the node** in the 🤖 Antigravity group (a Japan or another US node is recommended) and retry; if it persists, try another model (e.g. Gemini Flash Medium), start a new conversation, or sign out and sign back in.
- **Does it need admin rights?** No.
- **Antivirus/SmartScreen warning?** Normal for an unsigned exe — click "Run anyway".
- **What backups are created?** Clash `profiles.yaml.antigravity.bak` and Antigravity `settings.json.bak`.

---

## 🧑‍💻 Run from source (optional)

```powershell
pip install pyyaml
python antigravity_proxy_helper.py
```

or double-click `Start Antigravity Proxy Helper.bat`.

Requirements: Windows 10/11, Python 3.10+ (source only), Clash Verge Rev.
