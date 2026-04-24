import os

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

# --- Wiring: conectar adaptadores → servicios ---
endpoint = os.getenv("DYNAMODB_URL", "http://localhost:8000")
dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint, region_name="us-east-1")
table = dynamodb.Table("EcommerceTable")

# Cliente Redis usado por el adaptador de caché.
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(redis_url, decode_responses=True)

# TTL configurable para controlar cuánto dura cada item en caché.
cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "60"))
cache = RedisJsonCache(redis_client, ttl_seconds=cache_ttl_seconds)
cache_metrics = CacheMetrics(redis_client)

# Repositorios base (DynamoDB) y decoradores cache-aside.
user_repository = CachedUserRepository(DynamoUserRepository(table), cache, cache_metrics)
order_repository = CachedOrderRepository(DynamoOrderRepository(table), cache, cache_metrics)

user_service = UserService(user_repository)
order_service = OrderService(order_repository)


# --- Adaptador de entrada HTTP ---

class LoginRequest(BaseModel):
    correo: str
    password: str


@app.post("/login")
async def login(body: LoginRequest):
    user = user_service.login(body.correo, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {
        "PK": f"USER#{user.user_id}",
        "Nombre": user.nombre,
        "Correo": user.correo,
        "Direcciones": user.direcciones,
        "Metodos_de_pago": user.metodos_de_pago,
    }


@app.get("/user/{user_id}/profile")
async def get_profile(user_id: str):
    user = user_service.get_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "PK": f"USER#{user.user_id}",
        "Nombre": user.nombre,
        "Correo": user.correo,
        "Direcciones": user.direcciones,
        "Metodos_de_pago": user.metodos_de_pago,
    }


@app.get("/user/{user_id}/orders")
async def get_recent_orders(user_id: str):
    orders = order_service.get_user_orders(user_id)
    return [
        {
            "SK": f"ORDER#{o.order_id}",
            "Fecha_creacion": o.fecha_creacion,
            "Estado": o.estado,
            "Total": o.total,
        }
        for o in orders
    ]


@app.get("/order/{order_id}")
async def get_order_details(order_id: str):
    detail = order_service.get_order_detail(order_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {
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
    }


@app.get("/cache/metrics")
async def get_cache_metrics():
    """Endpoint de observabilidad para monitorear hits/misses de caché."""
    return cache_metrics.snapshot()


@app.get("/cache/keys")
async def get_cache_keys(limit: int = 20):
    """Lista claves activas de caché y su TTL restante."""
    return cache.list_entries(limit=limit)
