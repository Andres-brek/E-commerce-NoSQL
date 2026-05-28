import json
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from redis import Redis

from domain.order import (
    CheckoutItem,
    CheckoutResult,
    OrderDetail,
    OrderItem,
    OrderSummary,
)
from domain.product import Product
from domain.user import User
from ports.repositories import OrderRepository, ProductRepository, UserRepository


class RedisJsonCache:
    """Adaptador de caché JSON sobre Redis.

    Encapsula la serialización/deserialización y el manejo de TTL para que
    los repositorios cacheados solo se enfoquen en la estrategia cache-aside.
    """

    def __init__(self, client: Redis, ttl_seconds: int, namespace: str = "cache:data"):
        self._client = client
        self._ttl_seconds = ttl_seconds
        self._namespace = namespace

    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor desde Redis y lo transforma desde JSON."""
        redis_key = self._redis_key(key)
        cached_value = self._client.get(redis_key)
        if cached_value is None:
            return None
        return json.loads(cached_value)

    def set(self, key: str, value: Any) -> None:
        """Guarda un valor en Redis como JSON con expiración (TTL)."""
        redis_key = self._redis_key(key)
        serialized = json.dumps(value)
        self._client.set(redis_key, serialized, ex=self._ttl_seconds)

    def delete(self, key: str) -> None:
        """Elimina una entrada concreta de la caché."""
        self._client.delete(self._redis_key(key))

    def delete_pattern(self, pattern: str) -> None:
        """Elimina todas las claves que coinciden con un patrón estilo glob (e.g. 'products:*')."""
        full_pattern = f"{self._namespace}:{pattern}"
        for key in self._client.scan_iter(match=full_pattern, count=100):
            self._client.delete(key)

    def list_entries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lista claves de caché con su TTL para observabilidad."""
        pattern = f"{self._namespace}:*"
        entries: List[Dict[str, Any]] = []
        for key in self._client.scan_iter(match=pattern, count=100):
            entries.append(
                {
                    "key": key,
                    "ttl_seconds": self._client.ttl(key),
                }
            )
            if len(entries) >= limit:
                break
        return entries

    def _redis_key(self, key: str) -> str:
        return f"{self._namespace}:{key}"


class CacheMetrics:
    """Métricas de caché para observar hit/miss en tiempo real."""

    def __init__(self, client: Redis, metrics_key: str = "cache:metrics"):
        self._client = client
        self._metrics_key = metrics_key

    def record_hit(self, scope: str) -> None:
        """Registra hit global y hit por alcance (scope)."""
        pipeline = self._client.pipeline()
        pipeline.hincrby(self._metrics_key, "hits", 1)
        pipeline.hincrby(self._metrics_key, f"{scope}_hits", 1)
        pipeline.execute()

    def record_miss(self, scope: str) -> None:
        """Registra miss global y miss por alcance (scope)."""
        pipeline = self._client.pipeline()
        pipeline.hincrby(self._metrics_key, "misses", 1)
        pipeline.hincrby(self._metrics_key, f"{scope}_misses", 1)
        pipeline.execute()

    def snapshot(self) -> Dict[str, int]:
        """Devuelve el estado actual de métricas."""
        raw = self._client.hgetall(self._metrics_key)
        return {key: int(value) for key, value in raw.items()}


class CachedUserRepository(UserRepository):
    """Repositorio decorador de usuario con estrategia cache-aside."""

    def __init__(
        self,
        source: UserRepository,
        cache: RedisJsonCache,
        metrics: CacheMetrics,
    ):
        self._source = source
        self._cache = cache
        self._metrics = metrics

    def find_credentials_by_email(self, correo: str) -> Optional[dict]:
        cache_key = f"user:credentials:{correo.strip().lower()}"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("credentials")
            print(f"[CACHE HIT] login credentials correo={correo}", flush=True)
            return cached_value

        self._metrics.record_miss("credentials")
        print(f"[CACHE MISS] login credentials correo={correo} -> DynamoDB", flush=True)
        credentials = self._source.find_credentials_by_email(correo)
        if credentials is not None:
            self._cache.set(cache_key, credentials)
        return credentials

    def find_profile(self, user_id: str) -> Optional[User]:
        cache_key = f"user:profile:{user_id}"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("profile")
            print(f"[CACHE HIT] user profile user_id={user_id}", flush=True)
            return User(**cached_value)

        self._metrics.record_miss("profile")
        print(f"[CACHE MISS] user profile user_id={user_id} -> DynamoDB", flush=True)
        user = self._source.find_profile(user_id)
        if user is not None:
            self._cache.set(cache_key, asdict(user))
        return user


class CachedOrderRepository(OrderRepository):
    """Repositorio decorador de pedidos con estrategia cache-aside."""

    def __init__(
        self,
        source: OrderRepository,
        cache: RedisJsonCache,
        metrics: CacheMetrics,
    ):
        self._source = source
        self._cache = cache
        self._metrics = metrics

    def find_orders_by_user(self, user_id: str) -> List[OrderSummary]:
        cache_key = f"user:orders:{user_id}"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("orders")
            return [OrderSummary(**item) for item in cached_value]

        self._metrics.record_miss("orders")
        orders = self._source.find_orders_by_user(user_id)
        self._cache.set(cache_key, [asdict(order) for order in orders])
        return orders

    def find_order_detail(self, order_id: str) -> Optional[OrderDetail]:
        cache_key = f"order:detail:{order_id}"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("order_detail")
            return OrderDetail(
                fecha=cached_value["fecha"],
                total=cached_value["total"],
                direccion_envio=cached_value["direccion_envio"],
                items=[OrderItem(**item) for item in cached_value["items"]],
                fecha_entrega=cached_value.get("fecha_entrega"),
                estado=cached_value.get("estado"),
            )

        self._metrics.record_miss("order_detail")
        detail = self._source.find_order_detail(order_id)
        if detail is not None:
            self._cache.set(cache_key, asdict(detail))
        return detail

    def create_order(
        self,
        user_id: str,
        items: List[CheckoutItem],
        direccion_envio: str,
    ) -> CheckoutResult:
        result = self._source.create_order(user_id, items, direccion_envio)
        # Invalidar listado de pedidos del usuario y todo lo de productos
        # (porque cambió el stock — más simple que invalidar por id).
        self._cache.delete(f"user:orders:{user_id}")
        self._cache.delete_pattern("products:*")
        return result


class CachedProductRepository(ProductRepository):
    """Repositorio decorador de productos con estrategia cache-aside."""

    def __init__(
        self,
        source: ProductRepository,
        cache: RedisJsonCache,
        metrics: CacheMetrics,
    ):
        self._source = source
        self._cache = cache
        self._metrics = metrics

    def _deserialize(self, raw: dict) -> Product:
        return Product(**raw)

    def find_all(self) -> List[Product]:
        cache_key = "products:all"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("products")
            print(f"[CACHE HIT] products catalog ({len(cached_value)} items)", flush=True)
            return [self._deserialize(p) for p in cached_value]

        self._metrics.record_miss("products")
        print("[CACHE MISS] products catalog -> DynamoDB", flush=True)
        products = self._source.find_all()
        self._cache.set(cache_key, [asdict(p) for p in products])
        return products

    def find_by_category(self, categoria: str) -> List[Product]:
        cache_key = f"products:category:{categoria}"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("products_cat")
            return [self._deserialize(p) for p in cached_value]

        self._metrics.record_miss("products_cat")
        products = self._source.find_by_category(categoria)
        self._cache.set(cache_key, [asdict(p) for p in products])
        return products

    def find_by_id(self, product_id: str) -> Optional[Product]:
        cache_key = f"products:id:{product_id}"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("product_detail")
            return self._deserialize(cached_value)

        self._metrics.record_miss("product_detail")
        product = self._source.find_by_id(product_id)
        if product is not None:
            self._cache.set(cache_key, asdict(product))
        return product

    def find_on_sale(self) -> List[Product]:
        cache_key = "products:on_sale"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("products_sale")
            return [self._deserialize(p) for p in cached_value]

        self._metrics.record_miss("products_sale")
        products = self._source.find_on_sale()
        self._cache.set(cache_key, [asdict(p) for p in products])
        return products

    def search_by_name(self, query: str) -> List[Product]:
        # Normalizamos la query para usarla como clave de caché.
        cache_key = f"products:search:{query.strip().lower()}"
        cached_value = self._cache.get(cache_key)
        if cached_value is not None:
            self._metrics.record_hit("products_search")
            return [self._deserialize(p) for p in cached_value]

        self._metrics.record_miss("products_search")
        products = self._source.search_by_name(query)
        self._cache.set(cache_key, [asdict(p) for p in products])
        return products
