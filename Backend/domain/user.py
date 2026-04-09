from dataclasses import dataclass


@dataclass
class User:
    user_id: str
    nombre: str
    correo: str
    direcciones: str
    metodos_de_pago: str
