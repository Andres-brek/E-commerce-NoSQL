from abc import ABC, abstractmethod
from typing import List, Optional

from domain.user import User
from domain.order import OrderSummary, OrderDetail


class UserRepository(ABC):
    """Puerto de salida: define CÓMO se accede a datos de usuarios.
    El dominio no sabe si es DynamoDB, Postgres, una API externa, etc."""

    @abstractmethod
    def find_credentials_by_email(self, correo: str) -> Optional[dict]:
        pass

    @abstractmethod
    def find_profile(self, user_id: str) -> Optional[User]:
        pass


class OrderRepository(ABC):
    """Puerto de salida: define CÓMO se accede a datos de pedidos."""

    @abstractmethod
    def find_orders_by_user(self, user_id: str) -> List[OrderSummary]:
        pass

    @abstractmethod
    def find_order_detail(self, order_id: str) -> Optional[OrderDetail]:
        pass
