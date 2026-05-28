import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '../components/Nav';
import API from '../config';

function formatCOP(price) {
  return '$ ' + Number(price).toLocaleString('es-CO') + ' COP';
}

function formatDeliveryDate(iso) {
  // iso = "YYYY-MM-DD" — lo parseamos manualmente para evitar shifts por zona horaria.
  const [y, m, d] = iso.split('-').map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString('es-CO', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });
}

function CartPage({ user, onLogout, cart, onUpdateCart }) {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [confirmation, setConfirmation] = useState(null);

  function handleQtyChange(productId, delta) {
    onUpdateCart(prev =>
      prev
        .map(item =>
          item.id === productId ? { ...item, qty: item.qty + delta } : item
        )
        .filter(item => item.qty > 0)
    );
  }

  function handleRemove(productId) {
    onUpdateCart(prev => prev.filter(item => item.id !== productId));
  }

  async function handleCheckout() {
    if (!user) { navigate('/login'); return; }
    setSubmitting(true);
    setError('');

    const userId = user.PK.split('#')[1];
    const payload = {
      user_id: userId,
      direccion_envio: user.Direcciones,
      items: cart.map(it => ({ product_id: it.id, cantidad: it.qty })),
    };

    try {
      const res = await fetch(`${API}/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'No se pudo procesar el pedido.');
      } else {
        setConfirmation(data);
        onUpdateCart(() => []);
      }
    } catch (err) {
      setError('Error de red. Intenta de nuevo.');
    } finally {
      setSubmitting(false);
    }
  }

  const subtotal = cart.reduce((sum, item) => sum + item.precio * item.qty, 0);
  const cartCount = cart.reduce((a, i) => a + i.qty, 0);

  // ── Pantalla de confirmación tras compra exitosa ──
  if (confirmation) {
    return (
      <>
        <Nav user={user} onLogout={onLogout} cartCount={0} />
        <div className="cart-page">
          <div className="checkout-success">
            <div className="success-icon">✓</div>
            <h2>¡Pedido confirmado!</h2>
            <p className="success-msg">
              Tu pedido <strong>ORD#{confirmation.order_id}</strong> fue procesado con éxito.
            </p>
            <div className="success-box">
              <div className="success-row">
                <span className="success-label">Total pagado</span>
                <span className="success-value">{formatCOP(confirmation.total)}</span>
              </div>
              <div className="success-row">
                <span className="success-label">Fecha estimada de entrega</span>
                <span className="success-value highlight">
                  📦 {formatDeliveryDate(confirmation.fecha_entrega)}
                </span>
              </div>
              <div className="success-row">
                <span className="success-label">Dirección</span>
                <span className="success-value">{user.Direcciones}</span>
              </div>
            </div>
            <div className="success-actions">
              <button className="back-btn" onClick={() => navigate('/')}>← Seguir comprando</button>
              <button className="checkout-btn" onClick={() => navigate('/orders')}>
                Ver mis pedidos
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Nav user={user} onLogout={onLogout} cartCount={cartCount} />

      <div className="cart-page">
        <div className="cart-header-row">
          <h2 className="cart-title">🛒 Mi Carrito</h2>
          <button className="back-btn" onClick={() => navigate('/')}>← Seguir comprando</button>
        </div>

        {cart.length === 0 ? (
          <div className="cart-empty">
            <p>Tu carrito está vacío.</p>
            <button className="add-cart-btn" onClick={() => navigate('/')}>Ver productos</button>
          </div>
        ) : (
          <div className="cart-layout">
            <div className="cart-items">
              {cart.map(item => (
                <div key={item.id} className="cart-item-row">
                  <div className="cart-item-img-wrap">
                    {item.imagen_url ? (
                      <img src={item.imagen_url} alt={item.nombre} className="cart-item-img" />
                    ) : (
                      <div className="cart-item-img-placeholder">📦</div>
                    )}
                  </div>
                  <div className="cart-item-details">
                    <p className="cart-item-name">{item.nombre}</p>
                    <p className="cart-item-cat">{item.categoria}</p>
                    <p className="cart-item-price">{formatCOP(item.precio)} c/u</p>
                  </div>
                  <div className="cart-item-qty">
                    <button className="qty-btn" onClick={() => handleQtyChange(item.id, -1)}>−</button>
                    <span className="qty-value">{item.qty}</span>
                    <button
                      className="qty-btn"
                      onClick={() => handleQtyChange(item.id, 1)}
                      disabled={item.qty >= item.stock}
                    >+</button>
                  </div>
                  <div className="cart-item-subtotal">
                    {formatCOP(item.precio * item.qty)}
                  </div>
                  <button className="cart-remove-btn" onClick={() => handleRemove(item.id)}>✕</button>
                </div>
              ))}
            </div>

            <div className="cart-summary">
              <h3 className="summary-title">Resumen del pedido</h3>
              <div className="summary-row">
                <span>Subtotal ({cartCount} artículo{cartCount !== 1 ? 's' : ''})</span>
                <span>{formatCOP(subtotal)}</span>
              </div>
              <div className="summary-row">
                <span>Envío</span>
                <span className="free-shipping">Gratis</span>
              </div>
              <div className="summary-divider" />
              <div className="summary-row total-row">
                <span>Total</span>
                <span>{formatCOP(subtotal)}</span>
              </div>
              {user ? (
                <>
                  <p className="summary-address">
                    📍 <strong>Dirección de envío:</strong><br />
                    {user.Direcciones}
                  </p>
                  <p className="summary-delivery">
                    🚚 <strong>Entrega estimada:</strong> 5 días hábiles tras la compra
                  </p>
                  {error && <p className="checkout-error">{error}</p>}
                  <button
                    className="checkout-btn"
                    onClick={handleCheckout}
                    disabled={submitting}
                  >
                    {submitting ? 'Procesando...' : 'Proceder al pago'}
                  </button>
                </>
              ) : (
                <button className="checkout-btn" onClick={() => navigate('/login')}>
                  Iniciar sesión para pagar
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default CartPage;
