from fastapi import FastAPI
import boto3
from boto3.dynamodb.conditions import Key
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

# Configuración de la tabla 
endpoint = os.getenv("DYNAMODB_URL", "http://localhost:8000")
dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint, region_name='us-east-1')
table = dynamodb.Table('EcommerceTable')

@app.get("/user/{user_id}/profile")
async def get_profile(user_id: str):
    # PA1: Obtener perfil usando SK=PROFILE 
    response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
    return response.get('Item')

@app.get("/user/{user_id}/orders")
async def get_recent_orders(user_id: str):
    # PA2: Historial de pedidos usando begins_with 
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('ORDER#'),
        ScanIndexForward=False # Para orden descendente (más reciente primero) 
    )
    return response.get('Items')

@app.get("/order/{order_id}")
async def get_order_details(order_id: str):
    # PA3 y PA4: Traer todo lo relacionado al pedido en una sola consulta 
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f'ORD#{order_id}')
    )
    print(response)
    print("\n")
    items = response.get('Items')
    print(items)
    # Separamos la cabecera (INFO) de los productos (ITEM#) 
    header = next((item for item in items if item['SK'] == 'INFO'), None)
    products = [item for item in items if item['SK'].startswith('ITEM#')]
    
    return {"header": header, "items": products}