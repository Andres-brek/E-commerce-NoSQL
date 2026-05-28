from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    product_id: str
    nombre: str
    precio: int
    stock: int
    categoria: str
    descripcion: str
    imagen_url: Optional[str] = None
    descuento: int = 0  # Porcentaje 0-100 — 0 significa sin oferta.

    @property
    def precio_final(self) -> int:
        if self.descuento <= 0:
            return self.precio
        return int(self.precio * (100 - self.descuento) / 100)
