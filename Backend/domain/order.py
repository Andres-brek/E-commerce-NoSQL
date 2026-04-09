from dataclasses import dataclass, field
from typing import List


@dataclass
class OrderItem:
    producto: str
    cantidad: int
    precio_unitario: int


@dataclass
class OrderSummary:
    order_id: str
    fecha_creacion: str
    estado: str
    total: int


@dataclass
class OrderDetail:
    fecha: str
    total: int
    direccion_envio: str
    items: List[OrderItem] = field(default_factory=list)
