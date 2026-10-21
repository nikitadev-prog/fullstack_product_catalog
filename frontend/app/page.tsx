import Link from "next/link";
import { getProducts } from "../lib/products";

export const dynamic = "force-dynamic";

export default async function CatalogPage() {
  let products = null;
  try {
    products = await getProducts();
  } catch {
    products = null;
  }

  return (
    <section>
      <h1>Каталог</h1>
      {products === null && <p>Каталог сейчас недоступен</p>}
      {products && products.length === 0 && <p>Пока нет товаров</p>}
      {products && products.length > 0 && (
        <ul>
          {products.map((product) => (
            <li key={product.id}>
              <Link href={`/product/${product.id}`}>
                <img className="thumb" src={product.image_url} alt="" />
                <span>{product.name}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
