// 竹北三餐 service worker：頁面與名單「先上網拿最新、失敗才用快取」，字型與函式庫用快取。
const V = "zb-v2";
const CORE = ["./", "index.html", "breakfast.html", "lunch.html", "dinner.html", "shops_b.json", "shops_l.json", "shops_d.json", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  if (u.hostname === "ntfy.sh" || u.hostname.endsWith("open-meteo.com") || u.hostname.includes("openstreetmap")) return; // 即時資料不快取
  const sameOrigin = u.origin === location.origin;
  const isLib = /fonts\.(googleapis|gstatic)\.com|cdnjs\.cloudflare\.com/.test(u.hostname);
  if (sameOrigin) {
    e.respondWith(fetch(e.request, { cache: "no-cache" }).then(r => { const c = r.clone(); caches.open(V).then(ca => ca.put(e.request, c)); return r; })
      .catch(() => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match("index.html"))));
  } else if (isLib) {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(res => { const c = res.clone(); caches.open(V).then(ca => ca.put(e.request, c)); return res; })));
  }
});
