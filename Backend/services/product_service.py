from typing import List, Optional

from domain.product import Product
from ports.repositories import ProductRepository


class ProductService:
    """Lógica de negocio de productos.
    Solo conoce el puerto (ProductRepository), nunca DynamoDB directamente."""

    def __init__(self, repo: ProductRepository):
        self._repo = repo

    def get_all(self) -> List[Product]:
        return self._repo.find_all()

    def get_by_category(self, categoria: str) -> List[Product]:
        return self._repo.find_by_category(categoria)

    def get_by_id(self, product_id: str) -> Optional[Product]:
        return self._repo.find_by_id(product_id)

    def search(self, query: str) -> List[Product]:
        return self._repo.search_by_name(query)

    def get_on_sale(self) -> List[Product]:
        return self._repo.find_on_sale()
