import type { Product } from "./types";

function base() {
  return (process.env.API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
}

export async function getProducts(): Promise<Product[]> {
  const res = await fetch(`${base()}/products`, { cache: "no-store" });
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}

export async function getProduct(id: string): Promise<Product | null> {
  const res = await fetch(`${base()}/products/${id}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}
