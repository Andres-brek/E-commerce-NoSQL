"""
Lambda handler — entry point for API Gateway proxy integration.

Each invocation receives an API Gateway event, routes it to the matching
service method, and returns a proxy-compatible response dict.
"""
import json
import os
import re

import boto3
from redis import Redis

from adapters.cache import (
    CacheMetrics,
    CachedOrderRepository,
    CachedUserRepository,
    RedisJsonCache,
)
from adapters.dynamodb import DynamoUserRepository, DynamoOrderRepository
from services.user_service import UserService
from services.order_service import OrderService

# ---------------------------------------------------------------------------
# Wiring — executed once per cold start, reused across warm invocations.
# ---------------------------------------------------------------------------

_dynamodb_url = os.environ.get("DYNAMODB_URL", "http://localhost:4566")
_table_name = os.environ.get("TABLE_NAME", "EcommerceTable")
_redis_url = os.environ.get("REDIS_URL", "")
_cache_ttl = int(os.environ.get("CACHE_TTL_SECONDS", "120"))

_dynamo = boto3.resource(
    "dynamodb",
    endpoint_url=_dynamodb_url,
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
)
_table = _dynamo.Table(_table_name)

_dynamo_user_repo = DynamoUserRepository(_table)
_dynamo_order_repo = DynamoOrderRepository(_table)

if _redis_url:
    _redis_client = Redis.from_url(_redis_url, decode_responses=True)
    _cache = RedisJsonCache(_redis_client, ttl_seconds=_cache_ttl)
    _metrics = CacheMetrics(_redis_client)
    _user_repo = CachedUserRepository(_dynamo_user_repo, _cache, _metrics)
    _order_repo = CachedOrderRepository(_dynamo_order_repo, _cache, _metrics)
else:
    # No Redis available — use plain DynamoDB repositories.
    _redis_client = None
    _cache = None
    _metrics = None
    _user_repo = _dynamo_user_repo
    _order_repo = _dynamo_order_repo

_user_service = UserService(_user_repo)
_order_service = OrderService(_order_repo)


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def _ok(body: object, status: int = 200) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        },
        "body": json.dumps(body),
    }


def _error(status: int, detail: str) -> dict:
    return _ok({"detail": detail}, status=status)


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

def _login(event: dict) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _error(400, "Cuerpo JSON inválido")

    correo = body.get("correo")
    password = body.get("password")
    if not correo or not password:
        return _error(400, "correo y password son requeridos")

    user = _user_service.login(correo, password)
    if not user:
        return _error(401, "Credenciales inválidas")

    return _ok({
        "PK": f"USER#{user.user_id}",
        "Nombre": user.nombre,
        "Correo": user.correo,
        "Direcciones": user.direcciones,
        "Metodos_de_pago": user.metodos_de_pago,
    })


def _get_profile(user_id: str) -> dict:
    user = _user_service.get_profile(user_id)
    if not user:
        return _error(404, "Usuario no encontrado")
    return _ok({
        "PK": f"USER#{user.user_id}",
        "Nombre": user.nombre,
        "Correo": user.correo,
        "Direcciones": user.direcciones,
        "Metodos_de_pago": user.metodos_de_pago,
    })


def _get_user_orders(user_id: str) -> dict:
    orders = _order_service.get_user_orders(user_id)
    return _ok([
        {
            "SK": f"ORDER#{o.order_id}",
            "Fecha_creacion": o.fecha_creacion,
            "Estado": o.estado,
            "Total": o.total,
        }
        for o in orders
    ])


def _get_order_detail(order_id: str) -> dict:
    detail = _order_service.get_order_detail(order_id)
    if not detail:
        return _error(404, "Pedido no encontrado")
    return _ok({
        "header": {
            "Fecha": detail.fecha,
            "Total": detail.total,
            "Direccion_envio": detail.direccion_envio,
        },
        "items": [
            {
                "Producto": item.producto,
                "Cantidad": item.cantidad,
                "Precio_unitario": item.precio_unitario,
            }
            for item in detail.items
        ],
    })


def _get_cache_metrics() -> dict:
    if _metrics is None:
        return _ok({"detail": "Cache no configurada"})
    return _ok(_metrics.snapshot())


def _get_cache_keys(event: dict) -> dict:
    if _cache is None:
        return _ok([])
    limit = int((event.get("queryStringParameters") or {}).get("limit", 20))
    return _ok(_cache.list_entries(limit=limit))


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

# Patterns are matched against path in order; the first match wins.
_ROUTES = [
    ("POST",  re.compile(r"^/login$"),                        lambda e, m: _login(e)),
    ("GET",   re.compile(r"^/user/(?P<uid>[^/]+)/profile$"),  lambda e, m: _get_profile(m.group("uid"))),
    ("GET",   re.compile(r"^/user/(?P<uid>[^/]+)/orders$"),   lambda e, m: _get_user_orders(m.group("uid"))),
    ("GET",   re.compile(r"^/order/(?P<oid>[^/]+)$"),         lambda e, m: _get_order_detail(m.group("oid"))),
    ("GET",   re.compile(r"^/cache/metrics$"),                 lambda e, m: _get_cache_metrics()),
    ("GET",   re.compile(r"^/cache/keys$"),                    lambda e, m: _get_cache_keys(e)),
]


def handler(event: dict, context) -> dict:
    method = event.get("httpMethod", "GET").upper()
    path = event.get("path", "/")

    # API Gateway OPTIONS pre-flight
    if method == "OPTIONS":
        return _ok({})

    for route_method, pattern, fn in _ROUTES:
        if method != route_method:
            continue
        match = pattern.match(path)
        if match:
            return fn(event, match)

    return _error(404, f"Ruta no encontrada: {method} {path}")
