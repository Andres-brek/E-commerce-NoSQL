from typing import List, Optional

from domain.order import OrderSummary, OrderDetail
from ports.repositories import OrderRepository


class OrderService:
    """Lógica de negocio de pedidos.
    Solo conoce el puerto (OrderRepository), nunca DynamoDB directamente."""

    def __init__(self, repo: OrderRepository):
        self._repo = repo

    def get_user_orders(self, user_id: str) -> List[OrderSummary]:
        return self._repo.find_orders_by_user(user_id)

    def get_order_detail(self, order_id: str) -> Optional[OrderDetail]:
        return self._repo.find_order_detail(order_id)
