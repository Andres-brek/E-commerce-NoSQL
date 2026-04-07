import { useEffect, useState } from 'react';
import './App.css';

const API = 'http://localhost:8050';
const USER_ID = '001';

function App() {
  const [profile, setProfile] = useState(null);
  const [orders, setOrders] = useState([]);
  const [orderDetail, setOrderDetail] = useState(null);

  useEffect(() => {
    fetch(`${API}/user/${USER_ID}/profile`)
      .then(res => res.json())
      .then(data => setProfile(data));

    fetch(`${API}/user/${USER_ID}/orders`)
      .then(res => res.json())
      .then(data => setOrders(data));
  }, []);

  function handleOrderClick(order) {
    const orderId = order.SK.split('#')[1];
    fetch(`${API}/order/${orderId}`)
      .then(res => res.json())
      .then(data => setOrderDetail(data));
  }

  function iconStatus(status){
    switch (status) {
      case "Cancelado":
        return "❌"
        
      case "Pago exitoso":
        return "💳"

      case "En camino":
        return "🚚"

      case "Pendiente":
        return "⏳"
        
      default:
        return "✔️"
    }
  }

  return (
    <div className="panel">
      <h1 className="panel-title">Mi Mercado Global - Panel de Control</h1>
      <p className="breadcrumb">Inicio &gt; Usuario &gt; {profile?.Nombre} &gt; Pedidos Recientes</p>

      <div className="panel-body">
        <div className="left-col">
          {/* Perfil */}
          <div className="card">
            <h2>Mi Perfil</h2>
            {profile ? (
              <div className="profile-info">
                <div className="avatar">👤</div>
                <div>
                  <p><strong>Nombres:</strong> {profile.Nombre} ({profile.Correo})</p>
                  <p><strong>Direcciones:</strong> {profile.Direcciones}</p>
                  <p><strong>Metodos de pago:</strong> {profile.Metodos_de_pago}</p>
                </div>
              </div>
            ) : (
              <p>Cargando perfil...</p>
            )}
          </div>

          {/* Pedidos Recientes */}
          <div className="card">
            <h2>Pedidos Recientes</h2>
            <table className="orders-table">
              <thead>
                <tr>
                  <th></th>
                  <th>Estado</th>
                  <th>Fecha Creación</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order, i) => (
                  <tr key={i} onClick={() => handleOrderClick(order)} className="order-row">
                    <td>{iconStatus(order.Estado)}</td>
                    <td>{order.Estado}</td>
                    <td>{new Date(order.Fecha_creacion).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detalle del Pedido */}
        <div className="right-col">
          {orderDetail ? (
            <div className="card">
              <h2>Detalle del Pedido</h2>
              <div className="order-header">
                <p><strong>Fecha:</strong> {orderDetail.header?.Fecha}</p>
                <p><strong>Total:</strong> ${orderDetail.header?.Total}</p>
              </div>
              <h3>Ítems del Pedido</h3>
              <table className="orders-table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio unitario</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {orderDetail.items.map((item, i) => (
                    <tr key={i}>
                      <td>{item.Producto}</td>
                      <td>{item.Cantidad}</td>
                      <td>{item.Precio_unitario}</td>
                      <td>{item.Precio_unitario * item.Cantidad}</td>
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
  );
}

export default App;
