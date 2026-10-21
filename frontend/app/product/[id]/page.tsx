import { AddToCart } from "../../../components/AddToCart";
import { getProduct } from "../../../lib/products";

export const dynamic = "force-dynamic";

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let product;
  try {
    product = await getProduct(id);
  } catch {
    return <p>Каталог сейчас недоступен</p>;
  }
  if (!product) return <p>Товар не найден</p>;

  return (
    <article>
      <h1>{product.name}</h1>
      <img className="photo" src={product.image_url} alt={product.name} />
      <AddToCart productId={product.id} />
    </article>
  );
}
