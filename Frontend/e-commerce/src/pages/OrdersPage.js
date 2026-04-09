import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Nav from '../components/Nav';

const API = 'http://localhost:8050';

function OrdersPage({ user, onLogout }) {
  const [orders, setOrders] = useState([]);
  const [orderDetail, setOrderDetail] = useState(null);
  const [selectedOrderId, setSelectedOrderId] = useState(null);
  const navigate = useNavigate();

  const userId = user.PK.split('#')[1];

  useEffect(() => {
    fetch(`${API}/user/${userId}/orders`)
      .then(res => res.json())
      .then(data => setOrders(data));
  }, [userId]);

  function handleOrderClick(order) {
    const orderId = order.SK.split('#')[1];
    setSelectedOrderId(orderId);
    fetch(`${API}/order/${orderId}`)
      .then(res => res.json())
      .then(data => setOrderDetail(data));
  }

  function handleLogout() {
    onLogout();
    navigate('/login');
  }

  function statusBadge(status) {
    const map = {
      'Pago exitoso': { icon: '✓', cls: 'status-paid' },
      'Entregado':    { icon: '✓', cls: 'status-delivered' },
      'En camino':    { icon: '🚚', cls: 'status-shipping' },
      'Pendiente':    { icon: '⏳', cls: 'status-pending' },
      'Cancelado':    { icon: '✕', cls: 'status-cancelled' },
    };
    const s = map[status] || { icon: '●', cls: '' };
    return <span className={`status-badge ${s.cls}`}>{s.icon} {status}</span>;
  }

  function productIcon(nombre) {
    const n = nombre.toLowerCase();
    if (n.includes('laptop') || n.includes('computador')) return '💻';
    if (n.includes('monitor'))                             return '🖥️';
    if (n.includes('mouse'))                               return '🖱️';
    if (n.includes('teclado'))                             return '⌨️';
    if (n.includes('tablet'))                              return '📱';
    if (n.includes('webcam') || n.includes('camara'))      return '📷';
    if (n.includes('impresora'))                           return '🖨️';
    if (n.includes('audifono') || n.includes('headset'))   return '🎧';
    if (n.includes('libro'))                               return '📚';
    if (n.includes('cable'))                               return '🔌';
    if (n.includes('soporte') || n.includes('pad'))        return '🗂️';
    return '📦';
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString('es-ES', {
      year: 'numeric', month: 'short', day: 'numeric',
    });
  }

  const initial = user.Nombre ? user.Nombre.charAt(0).toUpperCase() : '?';

  return (
    <>
      <Nav onLogout={handleLogout} />

      <div className="panel">
        <div className="panel-header">
          <h1 className="panel-title">Panel de Control</h1>
          <p className="breadcrumb">Inicio › Usuario › {user.Nombre} › Pedidos Recientes</p>
        </div>

        <div className="panel-body">
          {/* ── Columna izquierda ── */}
          <div className="left-col">

            {/* Perfil */}
            <div className="card">
              <h2>Mi Perfil</h2>
              <div className="profile-info">
                <div className="avatar">{initial}</div>
                <div className="profile-details">
                  <p className="profile-name">
                    {user.Nombre}
                    <span className="profile-email"> ({user.Correo})</span>
                  </p>
                  <p className="profile-field">
                    <strong>Direcciones:</strong> {user.Direcciones}
                  </p>
                  <p className="profile-field">
                    <strong>Pagos:</strong> {user.Metodos_de_pago}
                  </p>
                </div>
              </div>
            </div>

            {/* Pedidos recientes */}
            <div className="card">
              <h2>Pedidos Recientes</h2>
              <table className="orders-table">
                <thead>
                  <tr>
                    <th>Estado</th>
                    <th>Fecha Creación</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order, i) => {
                    const orderId = order.SK.split('#')[1];
                    return (
                      <tr
                        key={i}
                        onClick={() => handleOrderClick(order)}
                        className={`order-row ${selectedOrderId === orderId ? 'order-row-active' : ''}`}
                      >
                        <td>{statusBadge(order.Estado)}</td>
                        <td>{formatDate(order.Fecha_creacion)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* ── Columna derecha: detalle ── */}
          <div className="right-col">
            {orderDetail ? (
              <div className="card">
                <h2>Detalle del Pedido ORD#{selectedOrderId}</h2>

                {/* Info general del pedido */}
                <p className="detail-section-title">Información General</p>
                <div className="order-info-card">
                  <span className="order-info-icon">🧾</span>
                  <div className="order-info-grid">
                    <div>
                      <p className="order-info-label">ORD#{selectedOrderId}</p>
                      <p className="order-info-value">Total: ${orderDetail.header?.Total}</p>
                    </div>
                    <div>
                      <p className="order-info-label">Fecha</p>
                      <p className="order-info-value">{orderDetail.header?.Fecha}</p>
                    </div>
                    <div>
                      <p className="order-info-label">Dirección de envío</p>
                      <p className="order-info-value">{orderDetail.header?.Direccion_envio}</p>
                    </div>
                    <div>
                      <p className="order-info-label">Total</p>
                      <p className="order-info-value order-total">${orderDetail.header?.Total}</p>
                    </div>
                  </div>
                </div>

                {/* Items */}
                <p className="detail-section-title">Ítems del Pedido</p>
                <table className="orders-table">
                  <thead>
                    <tr>
                      <th></th>
                      <th>Producto</th>
                      <th>Cantidad</th>
                      <th>Precio Unit.</th>
                      <th>Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orderDetail.items.map((item, i) => (
                      <tr key={i}>
                        <td className="product-icon-cell">{productIcon(item.Producto)}</td>
                        <td>{item.Producto}</td>
                        <td>{item.Cantidad}</td>
                        <td>${item.Precio_unitario}</td>
                        <td>${item.Precio_unitario * item.Cantidad}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="card placeholder">
                <p>Selecciona un pedido para ver el detalle</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default OrdersPage;
