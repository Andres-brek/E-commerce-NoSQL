import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import Nav from '../components/Nav';
import API from '../config';
import { useDebounce } from '../hooks/useDebounce';

const CATEGORIES = ['Todas', 'Electronica', 'Ropa', 'Hogar', 'Deportes'];

function formatCOP(price) {
  return '$ ' + Number(price).toLocaleString('es-CO') + ' COP';
}

function QtySelector({ product, qty, onSetQty }) {
  // Estado local del input para permitir escribir números intermedios
  // sin saltar al valor confirmado en cada tecla.
  const [inputValue, setInputValue] = useState(String(qty));

  // Si la cantidad cambia desde fuera (botones +/−, eliminar desde carrito),
  // sincronizamos el input.
  useEffect(() => { setInputValue(String(qty)); }, [qty]);

  function commit(raw) {
    const parsed = parseInt(raw, 10);
    if (isNaN(parsed) || parsed <= 0) {
      onSetQty(product, 0);
    } else {
      onSetQty(product, Math.min(parsed, product.stock));
    }
  }

  return (
    <div className="qty-selector">
      <button
        type="button"
        className="qty-selector-btn"
        onClick={() => onSetQty(product, qty - 1)}
        aria-label="Quitar uno"
      >−</button>
      <input
        type="number"
        className="qty-selector-input"
        min="0"
        max={product.stock}
        value={inputValue}
        onChange={e => setInputValue(e.target.value)}
        onBlur={e => commit(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter') e.target.blur(); }}
      />
      <button
        type="button"
        className="qty-selector-btn"
        onClick={() => onSetQty(product, qty + 1)}
        disabled={qty >= product.stock}
        aria-label="Añadir uno"
      >+</button>
    </div>
  );
}

function ProductCard({ product, cartItem, onAddToCart, onSetQty }) {
  const inCartQty = cartItem ? cartItem.qty : 0;
  const hasDiscount = Boolean(product.descuento && product.descuento > 0);
  const finalPrice = product.precio_final ?? product.precio;

  return (
    <div className="product-card">
      {hasDiscount ? (
        <span className="product-badge">−{product.descuento}%</span>
      ) : null}
      <div className="product-img-wrap">
        {product.imagen_url ? (
          <img src={product.imagen_url} alt={product.nombre} className="product-img" />
        ) : (
          <div className="product-img-placeholder">📦</div>
        )}
      </div>
      <div className="product-info">
        <p className="product-name">{product.nombre}</p>
        {hasDiscount ? (
          <div className="product-price-row">
            <span className="product-price-old">{formatCOP(product.precio)}</span>
            <span className="product-price product-price-sale">{formatCOP(finalPrice)}</span>
          </div>
        ) : (
          <p className="product-price">{formatCOP(product.precio)}</p>
        )}
        <p className="product-stock">Stock: {product.stock}</p>

        {product.stock === 0 ? (
          <button className="add-cart-btn" disabled>Sin stock</button>
        ) : inCartQty > 0 ? (
          <QtySelector product={product} qty={inCartQty} onSetQty={onSetQty} />
        ) : (
          <button className="add-cart-btn" onClick={() => onAddToCart(product)}>
            Añadir al Carrito
          </button>
        )}
      </div>
    </div>
  );
}

function HomePage({ user, onLogout, cart, onAddToCart, onSetQty }) {
  const [searchParams, setSearchParams] = useSearchParams();

  // El término de búsqueda y la categoría son la fuente de verdad en la URL,
  // así el Nav y la HomePage quedan sincronizados sin estado global.
  const activeCategory = searchParams.get('categoria') || 'Todas';
  const onlyOffers = searchParams.get('ofertas') === '1';
  const debouncedSearch = useDebounce(searchParams.get('q') || '', 350);

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Cada vez que cambia la categoría o el término ya debounceado, vamos al backend.
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (debouncedSearch.trim()) params.set('q', debouncedSearch.trim());
    if (activeCategory && activeCategory !== 'Todas') params.set('categoria', activeCategory);
    if (onlyOffers) params.set('ofertas', '1');
    const qs = params.toString();
    const url = qs ? `${API}/products?${qs}` : `${API}/products`;

    let cancelled = false;
    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (cancelled) return;
        setProducts(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [debouncedSearch, activeCategory, onlyOffers]);

  function updateCategory(cat) {
    const next = new URLSearchParams(searchParams);
    if (cat && cat !== 'Todas') next.set('categoria', cat);
    else next.delete('categoria');
    setSearchParams(next, { replace: true });
  }

  const cartCount = cart.reduce((a, i) => a + i.qty, 0);

  return (
    <>
      <Nav user={user} onLogout={onLogout} cartCount={cartCount} />

      <div className="home-layout">
        <aside className="sidebar">
          <h3 className="sidebar-title">Categorías</h3>
          <ul className="sidebar-list">
            {CATEGORIES.map(cat => (
              <li
                key={cat}
                className={`sidebar-item${activeCategory === cat ? ' active' : ''}`}
                onClick={() => updateCategory(cat)}
              >
                {cat === 'Todas' ? '🏠 Todas' :
                 cat === 'Electronica' ? '📱 Electrónica' :
                 cat === 'Ropa' ? '👕 Ropa' :
                 cat === 'Hogar' ? '🏠 Hogar' :
                 '⚽ Deportes'}
              </li>
            ))}
          </ul>
        </aside>

        <main className="home-main">
          <div className="home-header-row">
            <h2 className="home-section-title">
              {onlyOffers
                ? '🏷️ Ofertas de la semana'
                : debouncedSearch
                  ? `Resultados para "${debouncedSearch}"`
                  : activeCategory !== 'Todas'
                    ? activeCategory
                    : 'Nuestros Productos'}
            </h2>
          </div>

          {loading ? (
            <div className="home-loading">Cargando productos...</div>
          ) : products.length === 0 ? (
            <div className="home-empty">
              {debouncedSearch
                ? `No se encontraron productos para "${debouncedSearch}".`
                : 'No hay productos en esta categoría.'}
            </div>
          ) : (
            <div className="products-grid">
              {products.map(p => (
                <ProductCard
                  key={p.id}
                  product={p}
                  cartItem={cart.find(c => c.id === p.id)}
                  onAddToCart={onAddToCart}
                  onSetQty={onSetQty}
                />
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}

export default HomePage;
