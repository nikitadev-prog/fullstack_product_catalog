"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import type { CartItem } from "../../lib/types";

export default function CartPage() {
  const [items, setItems] = useState<CartItem[] | null>(null);
  const [error, setError] = useState("");

  async function load() {
    const res = await api("/cart");
    if (!res.ok) {
      setError("Не получилось загрузить корзину");
      setItems([]);
      return;
    }
    const data = await res.json();
    setItems(data.items);
  }

  useEffect(() => {
    load();
  }, []);

  async function changeQty(id: string, qty: number) {
    const res = await api(`/cart/items/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ qty }),
    });
    if (!res.ok) {
      setError("Не получилось обновить");
      return;
    }
    const data = await res.json();
    setItems(data.items);
    setError("");
  }

  async function remove(id: string) {
    const res = await api(`/cart/items/${id}`, { method: "DELETE" });
    if (!res.ok) {
      setError("Не получилось убрать");
      return;
    }
    const data = await res.json();
    setItems(data.items);
  }

  if (items === null) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Корзина</h1>
      {error ? <p>{error}</p> : null}
      {items.length === 0 ? <p>Корзина пуста</p> : null}
      {items.map((item) => (
        <div className="row" key={item.product_id}>
          <img className="thumb" src={item.image_url} alt="" />
          <div>
            <div>{item.name}</div>
            <input
              type="number"
              min={0}
              max={99}
              defaultValue={item.qty}
              key={`${item.product_id}-${item.qty}`}
              onBlur={(event) => {
                const next = Number(event.target.value);
                if (next !== item.qty) changeQty(item.product_id, next);
              }}
            />
            <button type="button" onClick={() => remove(item.product_id)}>
              Убрать
            </button>
          </div>
        </div>
      ))}
      {items.length > 0 ? (
        <p>
          <Link href="/checkout">Оформить заказ</Link>
        </p>
      ) : null}
    </section>
  );
}
