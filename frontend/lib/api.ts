const STORAGE_KEY = "sid";

export async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) headers.set("X-Session-Id", saved);

  const res = await fetch(`/api${path}`, {
    ...init,
    headers,
    credentials: "include",
    cache: "no-store",
  });
  const sid = res.headers.get("X-Session-Id");
  if (sid) localStorage.setItem(STORAGE_KEY, sid);
  return res;
}
