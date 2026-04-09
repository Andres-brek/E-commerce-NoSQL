function Nav({ onLogout }) {
  return (
    <nav className="nav">
      <span className="nav-title">Mi Mercado Global</span>
      <button className="nav-logout" onClick={onLogout}>Cerrar sesión</button>
    </nav>
  );
}

export default Nav;
