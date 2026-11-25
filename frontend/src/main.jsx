import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("/api/v1/products")
      .then((response) => response.json())
      .then(setProducts)
      .catch(() => setMessage("Unable to reach the API gateway"));
  }, []);

  async function checkout() {
    if (!cart.length) {
      setMessage("Add an item before checkout");
      return;
    }
    const response = await fetch("/api/v1/orders/checkout", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        idempotency_key: crypto.randomUUID(),
        items: cart.map((item) => ({ product_id: item.id, quantity: 1 })),
      }),
    });
    const order = await response.json();
    setMessage(response.ok ? `Order ${order.id} created` : order.detail);
  }

  return (
    <main>
      <header>
        <div>
          <p className="eyebrow">MicroFlow Marketplace</p>
          <h1>Cloud-ready goods</h1>
        </div>
        <button className="cart" onClick={checkout}>Cart ({cart.length})</button>
      </header>
      {message && <p className="message" role="status">{message}</p>}
      <section className="grid">
        {products.map((product) => (
          <article key={product.id}>
            <div className="icon" aria-hidden="true">M</div>
            <h2>{product.name}</h2>
            <p>{product.description}</p>
            <div className="product-footer">
              <strong>${(product.price_cents / 100).toFixed(2)}</strong>
              <button onClick={() => setCart((current) => [...current, product])}>Add</button>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode><App /></React.StrictMode>,
);
