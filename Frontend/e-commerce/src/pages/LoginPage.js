import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API = 'http://localhost:8050';

function LoginPage({ onLogin }) {
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    const res = await fetch(`${API}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, password }),
    });

    if (res.ok) {
      const user = await res.json();
      onLogin(user);
      navigate('/orders');
    } else {
      setError('Correo o contraseña incorrectos');
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <h1 className="login-brand">Mi Mercado Global</h1>
        <h2 className="login-title">Iniciar sesión</h2>
        <form onSubmit={handleSubmit}>
          <label>Correo</label>
          <input
            type="email"
            value={correo}
            onChange={e => setCorreo(e.target.value)}
            placeholder="usuario@correo.com"
            required
          />
          <label>Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
          {error && <p className="login-error">{error}</p>}
          <button type="submit" className="login-btn">Entrar</button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;
