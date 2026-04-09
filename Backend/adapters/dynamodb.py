from typing import List, Optional

from boto3.dynamodb.conditions import Key, Attr

from domain.user import User
from domain.order import OrderSummary, OrderDetail, OrderItem
from ports.repositories import UserRepository, OrderRepository


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
            )
            for i in items
            if i["SK"].startswith("ITEM#")
        ]
        return OrderDetail(
            fecha=header["Fecha"],
            total=int(header["Total"]),
            direccion_envio=header["Direccion_envio"],
            items=order_items,
        )
