export type Product = {
  id: string;
  name: string;
  image_url: string;
};

export type CartItem = {
  product_id: string;
  name: string;
  image_url: string;
  qty: number;
};

export type Order = {
  id: string;
  customer_name: string;
  phone: string;
  items: { name: string; qty: number }[];
};
