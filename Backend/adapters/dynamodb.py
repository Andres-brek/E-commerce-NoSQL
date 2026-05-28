import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


def _normalize(text: str) -> str:
    """Quita tildes/diacríticos y baja a minúsculas para comparación tolerante."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", text)
    no_accents = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return no_accents.lower()

from domain.user import User
from domain.order import (
    OrderSummary,
    OrderDetail,
    OrderItem,
    CheckoutItem,
    CheckoutResult,
)
from domain.product import Product
from ports.repositories import UserRepository, OrderRepository, ProductRepository


class CheckoutError(Exception):
    """Error de negocio durante el checkout (stock insuficiente, producto inexistente, etc.)."""


class DynamoUserRepository(UserRepository):
    """Adaptador de salida: implementa UserRepository usando DynamoDB."""

    def __init__(self, table):
        self._table = table

    def find_credentials_by_email(self, correo: str) -> Optional[dict]:
        response = self._table.scan(
            FilterExpression=Attr("SK").eq("CREDENTIALS") & Attr("Correo").eq(correo)
        )
        items = response.get("Items", [])
        return items[0] if items else None

    def find_profile(self, user_id: str) -> Optional[User]:
        response = self._table.get_item(
            Key={"PK": f"USER#{user_id}", "SK": "PROFILE"}
        )
        item = response.get("Item")
        if not item:
            return None
        return User(
            user_id=user_id,
            nombre=item["Nombre"],
            correo=item["Correo"],
            direcciones=item["Direcciones"],
            metodos_de_pago=item["Metodos_de_pago"],
        )


class DynamoOrderRepository(OrderRepository):
    """Adaptador de salida: implementa OrderRepository usando DynamoDB."""

    def __init__(self, table):
        self._table = table

    def find_orders_by_user(self, user_id: str) -> List[OrderSummary]:
        response = self._table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{user_id}")
            & Key("SK").begins_with("ORDER#"),
            ScanIndexForward=False,
        )
        return [
            OrderSummary(
                order_id=item["SK"].replace("ORDER#", ""),
                fecha_creacion=item["Fecha_creacion"],
                estado=item["Estado"],
                total=int(item["Total"]),
                fecha_entrega=item.get("Fecha_entrega"),
            )
            for item in response.get("Items", [])
        ]

    def find_order_detail(self, order_id: str) -> Optional[OrderDetail]:
        response = self._table.query(
            KeyConditionExpression=Key("PK").eq(f"ORD#{order_id}")
        )
        items = response.get("Items", [])
        header = next((i for i in items if i["SK"] == "INFO"), None)
        if not header:
            return None
        order_items = [
            OrderItem(
                producto=i["Producto"],
                cantidad=int(i["Cantidad"]),
                precio_unitario=int(i["Precio_unitario"]),
                product_id=i.get("Product_id"),
            )
            for i in items
            if i["SK"].startswith("ITEM#")
        ]
        return OrderDetail(
            fecha=header["Fecha"],
            total=int(header["Total"]),
            direccion_envio=header["Direccion_envio"],
            items=order_items,
            fecha_entrega=header.get("Fecha_entrega"),
            estado=header.get("Estado"),
        )

    def create_order(
        self,
        user_id: str,
        items: List[CheckoutItem],
        direccion_envio: str,
    ) -> CheckoutResult:
        if not items:
            raise CheckoutError("El carrito está vacío")

        # 1. Cargar productos para validar stock y obtener precios/nombres actuales.
        products_data: List[dict] = []
        total = 0
        for it in items:
            if it.cantidad <= 0:
                raise CheckoutError(f"Cantidad inválida para {it.product_id}")
            resp = self._table.get_item(
                Key={"PK": f"PRODUCT#{it.product_id}", "SK": "INFO"}
            )
            product = resp.get("Item")
            if not product:
                raise CheckoutError(f"Producto {it.product_id} no existe")
            stock = int(product["Stock"])
            if stock < it.cantidad:
                raise CheckoutError(
                    f"Stock insuficiente para {product['Nombre']} (disponible: {stock})"
                )
            precio = int(product["Precio"])
            total += precio * it.cantidad
            products_data.append({
                "product_id": it.product_id,
                "nombre": product["Nombre"],
                "precio": precio,
                "cantidad": it.cantidad,
                "stock_actual": stock,
            })

        # 2. Generar identificadores y fechas.
        now = datetime.now(timezone.utc)
        delivery = now + timedelta(days=5)
        order_id = uuid.uuid4().hex[:8].upper()
        fecha_creacion = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        fecha_entrega = delivery.strftime("%Y-%m-%d")
        estado = "Pago exitoso"

        # 3. TransactWriteItems: orden + items + decremento atómico de stock.
        # Cada decremento usa ConditionExpression para evitar oversell si otro
        # checkout corre en paralelo entre la lectura y la escritura.
        transact_items: List[dict] = []

        # Header en USER (para listar pedidos del usuario)
        transact_items.append({
            "Put": {
                "TableName": self._table.name,
                "Item": {
                    "PK": f"USER#{user_id}",
                    "SK": f"ORDER#{order_id}",
                    "Fecha_creacion": fecha_creacion,
                    "Fecha_entrega": fecha_entrega,
                    "Estado": estado,
                    "Total": total,
                },
            }
        })

        # Header en ORD (para ver detalle)
        transact_items.append({
            "Put": {
                "TableName": self._table.name,
                "Item": {
                    "PK": f"ORD#{order_id}",
                    "SK": "INFO",
                    "Fecha": fecha_creacion,
                    "Fecha_entrega": fecha_entrega,
                    "Estado": estado,
                    "Total": total,
                    "Direccion_envio": direccion_envio,
                    "User_id": user_id,
                },
            }
        })

        for idx, prod in enumerate(products_data, start=1):
            transact_items.append({
                "Put": {
                    "TableName": self._table.name,
                    "Item": {
                        "PK": f"ORD#{order_id}",
                        "SK": f"ITEM#{idx:02d}",
                        "Producto": prod["nombre"],
                        "Product_id": prod["product_id"],
                        "Cantidad": prod["cantidad"],
                        "Precio_unitario": prod["precio"],
                    },
                }
            })
            transact_items.append({
                "Update": {
                    "TableName": self._table.name,
                    "Key": {
                        "PK": f"PRODUCT#{prod['product_id']}",
                        "SK": "INFO",
                    },
                    "UpdateExpression": "SET Stock = Stock - :q",
                    "ConditionExpression": "Stock >= :q",
                    "ExpressionAttributeValues": {":q": prod["cantidad"]},
                }
            })

        client = self._table.meta.client
        try:
            client.transact_write_items(TransactItems=transact_items)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code in ("TransactionCanceledException", "ConditionalCheckFailedException"):
                raise CheckoutError(
                    "No fue posible procesar la orden: stock cambió mientras se procesaba"
                )
            raise

        return CheckoutResult(
            order_id=order_id,
            fecha_creacion=fecha_creacion,
            fecha_entrega=fecha_entrega,
            total=total,
            estado=estado,
        )


class DynamoProductRepository(ProductRepository):
    """Adaptador de salida: implementa ProductRepository usando DynamoDB."""

    def __init__(self, table):
        self._table = table

    def _item_to_product(self, item: dict) -> Product:
        return Product(
            product_id=item["PK"].replace("PRODUCT#", ""),
            nombre=item["Nombre"],
            precio=int(item["Precio"]),
            stock=int(item["Stock"]),
            categoria=item["Categoria"],
            descripcion=item.get("Descripcion", ""),
            imagen_url=item.get("Imagen_url"),
            descuento=int(item.get("Descuento", 0)),
        )

    def find_all(self) -> List[Product]:
        response = self._table.scan(
            FilterExpression=Attr("SK").eq("INFO") & Attr("PK").begins_with("PRODUCT#")
        )
        return [self._item_to_product(i) for i in response.get("Items", [])]

    def find_by_category(self, categoria: str) -> List[Product]:
        response = self._table.scan(
            FilterExpression=Attr("SK").eq("INFO")
            & Attr("PK").begins_with("PRODUCT#")
            & Attr("Categoria").eq(categoria)
        )
        return [self._item_to_product(i) for i in response.get("Items", [])]

    def find_by_id(self, product_id: str) -> Optional[Product]:
        response = self._table.get_item(
            Key={"PK": f"PRODUCT#{product_id}", "SK": "INFO"}
        )
        item = response.get("Item")
        if not item:
            return None
        return self._item_to_product(item)

    def find_on_sale(self) -> List[Product]:
        response = self._table.scan(
            FilterExpression=Attr("SK").eq("INFO")
            & Attr("PK").begins_with("PRODUCT#")
            & Attr("Descuento").gt(0)
        )
        return [self._item_to_product(i) for i in response.get("Items", [])]

    def search_by_name(self, query: str) -> List[Product]:
        # DynamoDB no soporta búsqueda tolerante a tildes/case nativa,
        # así que traemos todos los productos y filtramos en memoria.
        # En producción se usaría OpenSearch o un índice secundario.
        if not query:
            return self.find_all()
        response = self._table.scan(
            FilterExpression=Attr("SK").eq("INFO") & Attr("PK").begins_with("PRODUCT#")
        )
        q_norm = _normalize(query)
        return [
            self._item_to_product(i)
            for i in response.get("Items", [])
            if q_norm in _normalize(i["Nombre"])
            or q_norm in _normalize(i.get("Categoria", ""))
            or q_norm in _normalize(i.get("Descripcion", ""))
        ]
