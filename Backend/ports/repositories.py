from abc import ABC, abstractmethod
from typing import List, Optional

from domain.user import User
from domain.order import OrderSummary, OrderDetail, CheckoutItem, CheckoutResult
from domain.product import Product


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

    @abstractmethod
    def create_order(
        self,
        user_id: str,
        items: List[CheckoutItem],
        direccion_envio: str,
    ) -> CheckoutResult:
        """Crea una orden de forma atómica: descuenta stock, crea header e items."""
        pass


class ProductRepository(ABC):
    """Puerto de salida: define CÓMO se accede a datos de productos."""

    @abstractmethod
    def find_all(self) -> List[Product]:
        pass

    @abstractmethod
    def find_by_category(self, categoria: str) -> List[Product]:
        pass

    @abstractmethod
    def find_by_id(self, product_id: str) -> Optional[Product]:
        pass

    @abstractmethod
    def search_by_name(self, query: str) -> List[Product]:
        pass

    @abstractmethod
    def find_on_sale(self) -> List[Product]:
        """Devuelve solo productos con descuento > 0."""
        pass
