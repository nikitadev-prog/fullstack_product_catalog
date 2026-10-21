"use client";

import { useState } from "react";
import { api } from "../lib/api";

export function AddToCart({ productId }: { productId: string }) {
  const [text, setText] = useState("");

  async function add() {
    setText("");
    const res = await api("/cart/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, qty: 1 }),
    });
    setText(res.ok ? "Добавлено в корзину" : "Не получилось добавить");
  }

  return (
    <p>
      <button type="button" onClick={add}>
        В корзину
      </button>
      {text ? <span className="muted"> {text}</span> : null}
    </p>
  );
}
