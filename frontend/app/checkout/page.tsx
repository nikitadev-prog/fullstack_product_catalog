"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "../../lib/api";

export default function CheckoutPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setError("");
    const res = await api("/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, phone }),
    });
    setPending(false);
    if (!res.ok) {
      const data = await res.json().catch(() => null);
      const detail = data && typeof data.detail === "string" ? data.detail : "Не получилось оформить заказ";
      setError(detail);
      return;
    }
    const order = await res.json();
    router.push(`/order/${order.id}`);
  }

  return (
    <section>
      <h1>Заказ</h1>
      <form onSubmit={submit}>
        <label>
          Имя
          <input value={name} onChange={(event) => setName(event.target.value)} required />
        </label>
        <label>
          Телефон
          <input value={phone} onChange={(event) => setPhone(event.target.value)} required />
        </label>
        <button type="submit" disabled={pending}>
          Оформить
        </button>
      </form>
      {error ? <p>{error}</p> : null}
    </section>
  );
}
