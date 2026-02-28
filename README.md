# 🔥 FireOps — Wildfire Resource Manager

A real-time wildfire resource management map with live MONITOR GPS tracking.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main app — deploy this to GitHub Pages |
| `kml-proxy-worker.js` | Cloudflare Worker for live KML feed (free) |
| `fireops-proxy.py` | Local Python proxy for running offline |

---

## Deploy to GitHub Pages

1. Create a new GitHub repo (e.g. `fireops`)
2. Upload `index.html` to the repo root
3. Go to **Settings → Pages → Source** → set to `main` branch / root
4. Your app will be live at `https://your-username.github.io/fireops`

> **Note:** The live MONITOR feed requires the Cloudflare Worker proxy (below) to work on GitHub Pages due to browser CORS restrictions.

---

## Set Up the Live MONITOR Feed (Cloudflare Worker)

The MONITOR KML feed can't be fetched directly from a browser due to CORS. A free Cloudflare Worker acts as a pass-through proxy.

### Steps

1. Go to [workers.cloudflare.com](https://workers.cloudflare.com) and sign up (free)
2. Click **Create Worker**
3. Paste the entire contents of `kml-proxy-worker.js` into the editor
4. Click **Save and Deploy**
5. Copy your worker URL — it will look like:
   ```
   https://fireops-kml.your-name.workers.dev
   ```
6. Open `index.html` and find this line near the bottom:
   ```js
   const CF_WORKER_URL = null;
   ```
   Replace `null` with your worker URL + `/kml`:
   ```js
   const CF_WORKER_URL = 'https://fireops-kml.your-name.workers.dev/kml';
   ```
7. Re-upload `index.html` to GitHub — the MONITOR feed will now work live.

---

## Run Locally (No Internet Required for Proxy)

If you want to run the app locally without Cloudflare:

```bash
# Put index.html and fireops-proxy.py in the same folder, then:
python3 fireops-proxy.py
```

Then open **http://localhost:8765** in your browser.

The Python proxy fetches the KML server-side (bypassing CORS) and serves the app.

---

## Features

- 🗺️ Interactive map with dark tactical theme
- 📡 Live MONITOR GPS feed (auto-refreshes every 30s)
- 🚒 Wildfire-specific resource types (engines, crews, air tankers, facilities)
- 🟠 Operational statuses: Deployed, Staged, Available, Out of Service
- ➕ Add / edit / remove resources with full ICS fields
- 💾 Data persists in browser localStorage
