import os

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

user_service = UserService(DynamoUserRepository(table))
order_service = OrderService(DynamoOrderRepository(table))


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
