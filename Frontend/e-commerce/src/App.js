import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';

function App() {
  const [user, setUser] = useState(null);
  // cart: [{ id, nombre, precio, stock, categoria, imagen_url, qty }]
  const [cart, setCart] = useState([]);

  function handleLogin(userData) {
    setUser(userData);
  }

  function handleLogout() {
    setUser(null);
  }

  // Si el producto está en oferta, el carrito guarda el precio con descuento
  // como `precio`. Mantenemos `precio_original` por si se quiere mostrar.
  function normalizeForCart(product) {
    const finalPrice = product.precio_final ?? product.precio;
    return {
      ...product,
      precio_original: product.precio,
      precio: finalPrice,
    };
  }

  function handleAddToCart(product) {
    const normalized = normalizeForCart(product);
    setCart(prev => {
      const existing = prev.find(i => i.id === normalized.id);
      if (existing) {
        // No superar el stock
        if (existing.qty >= normalized.stock) return prev;
        return prev.map(i => i.id === normalized.id ? { ...i, qty: i.qty + 1 } : i);
      }
      return [...prev, { ...normalized, qty: 1 }];
    });
  }

  function handleSetQty(product, qty) {
    const normalized = normalizeForCart(product);
    setCart(prev => {
      // qty <= 0 elimina; nunca pasa del stock disponible.
      if (qty <= 0) return prev.filter(i => i.id !== normalized.id);
      const capped = Math.min(qty, normalized.stock);
      const existing = prev.find(i => i.id === normalized.id);
      if (existing) {
        return prev.map(i => i.id === normalized.id ? { ...i, qty: capped } : i);
      }
      return [...prev, { ...normalized, qty: capped }];
    });
  }

  const sharedNavProps = { user, onLogout: handleLogout };

  return (
    <BrowserRouter>
      <Routes>
        {/* Página principal — catálogo */}
        <Route
          path="/"
          element={
            <HomePage
              {...sharedNavProps}
              cart={cart}
              onAddToCart={handleAddToCart}
              onSetQty={handleSetQty}
            />
          }
        />

        {/* Carrito */}
        <Route
          path="/cart"
          element={
            <CartPage
              {...sharedNavProps}
              cart={cart}
              onUpdateCart={setCart}
            />
          }
        />

        {/* Login */}
        <Route
          path="/login"
          element={
            user
              ? <Navigate to="/" />
              : <LoginPage onLogin={handleLogin} />
          }
        />

        {/* Mis pedidos — requiere login */}
        <Route
          path="/orders"
          element={
            user
              ? <OrdersPage user={user} onLogout={handleLogout} />
              : <Navigate to="/login" />
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
