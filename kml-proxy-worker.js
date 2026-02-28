/**
 * FireOps — KML Proxy Cloudflare Worker
 * ──────────────────────────────────────
 * Deploy this to Cloudflare Workers (free tier) to proxy the
 * MONITOR KML feed without CORS issues on GitHub Pages.
 *
 * Setup:
 *   1. Go to https://workers.cloudflare.com and create a free account
 *   2. Click "Create Worker"
 *   3. Paste this entire file into the editor
 *   4. Click "Save and Deploy"
 *   5. Copy your worker URL (e.g. https://fireops-kml.your-name.workers.dev)
 *   6. In index.html, set:
 *        const CF_WORKER_URL = 'https://fireops-kml.your-name.workers.dev/kml';
 */

const KML_URL = "https://nexe.online/api/position/kml/update?api_key=c1e5ab04-9891-4c3c-8bcf-5912f861bbe8";

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "*",
        },
      });
    }

    // Only serve /kml path
    if (url.pathname !== "/kml") {
      return new Response("FireOps KML Proxy — use /kml endpoint", {
        status: 200,
        headers: { "Content-Type": "text/plain" },
      });
    }

    try {
      const upstream = await fetch(KML_URL, {
        headers: { "User-Agent": "FireOps/1.0 KML Proxy" },
      });

      if (!upstream.ok) {
        return new Response(`Upstream error: ${upstream.status}`, {
          status: 502,
          headers: { "Access-Control-Allow-Origin": "*" },
        });
      }

      const body = await upstream.text();

      return new Response(body, {
        status: 200,
        headers: {
          "Content-Type": "application/vnd.google-earth.kml+xml; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "no-cache, no-store",
          "X-Proxy": "FireOps-CF-Worker",
        },
      });

    } catch (err) {
      return new Response(`Proxy fetch failed: ${err.message}`, {
        status: 500,
        headers: { "Access-Control-Allow-Origin": "*" },
      });
    }
  },
};
