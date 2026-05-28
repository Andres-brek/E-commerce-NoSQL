from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OrderItem:
    producto: str
    cantidad: int
    precio_unitario: int
    product_id: Optional[str] = None


@dataclass
class OrderSummary:
    order_id: str
    fecha_creacion: str
    estado: str
    total: int
    fecha_entrega: Optional[str] = None


@dataclass
class OrderDetail:
    fecha: str
    total: int
    direccion_envio: str
    items: List[OrderItem] = field(default_factory=list)
    fecha_entrega: Optional[str] = None
    estado: Optional[str] = None


@dataclass
class CheckoutItem:
    product_id: str
    cantidad: int


@dataclass
class CheckoutResult:
    order_id: str
    fecha_creacion: str
    fecha_entrega: str
    total: int
    estado: str
