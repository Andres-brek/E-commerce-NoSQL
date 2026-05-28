import { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useDebounce } from '../hooks/useDebounce';

function Nav({ user, onLogout, cartCount = 0 }) {
  const [profileOpen, setProfileOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  // El input usa estado local para ser responsivo a la tecla,
  // pero solo propagamos a la URL después del debounce.
  const initialQuery = location.pathname === '/' ? (searchParams.get('q') || '') : '';
  const [query, setQuery] = useState(initialQuery);
  const debouncedQuery = useDebounce(query, 350);

  // Sincroniza el debounced query con la URL.
  // Solo escribimos cuando el usuario está escribiendo (no en cada cambio de ruta).
  const lastPushed = useRef(initialQuery);
  useEffect(() => {
    if (debouncedQuery === lastPushed.current) return;
    lastPushed.current = debouncedQuery;

    // Si está en otra página, llévalo a /; si ya está en /, solo actualiza el query.
    const params = new URLSearchParams(location.pathname === '/' ? searchParams : '');
    if (debouncedQuery.trim()) params.set('q', debouncedQuery.trim());
    else params.delete('q');
    const qs = params.toString();
    navigate(qs ? `/?${qs}` : '/', { replace: location.pathname === '/' });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery]);

  // Cierra el dropdown al hacer click fuera
  useEffect(() => {
    function handleOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  function handleLogout() {
    setProfileOpen(false);
    onLogout();
    navigate('/login');
  }

  const navLinks = [
    { label: 'Inicio', path: '/' },
    { label: '🏷️ Ofertas', path: '/?ofertas=1' },
  ];

  // Detecta cuál link está activo comparando pathname y query principal.
  function isLinkActive(linkPath) {
    if (location.pathname !== linkPath.split('?')[0]) return false;
    const linkQs = new URLSearchParams(linkPath.split('?')[1] || '');
    // "Ofertas" se considera activo si la URL contiene ?ofertas=1.
    if (linkQs.get('ofertas') === '1') return searchParams.get('ofertas') === '1';
    // "Inicio" se considera activo si NO hay categoría/ofertas en la URL.
    if (linkPath === '/') {
      return !searchParams.get('ofertas') && !searchParams.get('categoria');
    }
    return true;
  }

  return (
    <nav className="nav">
      <span className="nav-brand" onClick={() => navigate('/')}>
        🌿 Mi Mercado Global
      </span>

      <div className="nav-search-wrap">
        <input
          className="nav-search"
          type="text"
          placeholder="Buscar productos..."
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <span className="nav-search-icon">🔍</span>
      </div>

      <div className="nav-links">
        {navLinks.map(link => (
          <span
            key={link.label}
            className={`nav-link${isLinkActive(link.path) ? ' active' : ''}`}
            onClick={() => navigate(link.path)}
          >
            {link.label}
          </span>
        ))}
      </div>

      <div className="nav-actions">
        <button className="nav-cart-btn" onClick={() => navigate('/cart')}>
          🛒 Carrito
          {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </button>

        {user ? (
          <div className="nav-profile-wrap" ref={dropdownRef}>
            <button
              className="nav-profile-btn"
              onClick={() => setProfileOpen(o => !o)}
              aria-expanded={profileOpen}
            >
              👤
            </button>
            {profileOpen && (
              <div className="profile-dropdown">
                <p className="dropdown-greeting">
                  Bienvenido, <strong>{user.Nombre}</strong>
                </p>
                {user.Direcciones && (
                  <p className="dropdown-address">
                    <span className="dropdown-label">Dirección de envío por defecto:</span>
                    <br />
                    {user.Direcciones}
                  </p>
                )}
                <div className="dropdown-divider" />
                <button className="dropdown-link" onClick={() => { navigate('/orders'); setProfileOpen(false); }}>
                  📦 Mis Pedidos
                </button>
                <button className="dropdown-link logout" onClick={handleLogout}>
                  ↩ Cerrar sesión
                </button>
              </div>
            )}
          </div>
        ) : (
          <button className="nav-login-btn" onClick={() => navigate('/login')}>
            👤 Iniciar sesión
          </button>
        )}
      </div>
    </nav>
  );
}

export default Nav;
