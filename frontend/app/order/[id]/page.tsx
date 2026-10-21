"use client";

import { useEffect, useState } from "react";
import { api } from "../../../lib/api";
import type { Order } from "../../../lib/types";

export default function OrderPage({ params }: { params: Promise<{ id: string }> }) {
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    params.then(async ({ id }) => {
      const res = await api(`/orders/${id}`);
      if (cancelled) return;
      if (!res.ok) {
        setError("Заказ не найден");
        return;
      }
      setOrder(await res.json());
    });
    return () => {
      cancelled = true;
    };
  }, [params]);

  if (error) return <p>{error}</p>;
  if (!order) return <p>Загрузка...</p>;

  return (
    <section>
      <h1>Заказ принят</h1>
      <p>
        {order.customer_name}, {order.phone}
      </p>
      <ul>
        {order.items.map((item, index) => (
          <li key={`${item.name}-${index}`}>
            {item.name} — {item.qty} шт.
          </li>
        ))}
      </ul>
    </section>
  );
}
