import boto3
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

# Conexión local
endpoint = os.getenv("DYNAMODB_URL", "http://localhost:8000")
dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint, region_name='us-east-1')

def hash_password(password: str) -> str:
    pepper = os.getenv("PASSWORD_PEPPER", "")
    return hashlib.sha256((password + pepper).encode()).hexdigest()

def create_table():
    table = dynamodb.create_table(
        TableName='EcommerceTable',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'}, # Partition Key 
            {'AttributeName': 'SK', 'KeyType': 'RANGE'} # Sort Key 
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    table.wait_until_exists()
    return table

def seed_products():
    table = dynamodb.Table('EcommerceTable')
    products = [
        # Electrónica
        {
            "PK": "PRODUCT#P001", "SK": "INFO",
            "Nombre": "Teléfono Inteligente X100",
            "Precio": 850000, "Stock": 15,
            "Categoria": "Electronica",
            "Descripcion": "Smartphone de última generación con cámara de 108MP y batería de 5000mAh.",
            "Imagen_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80",
            "Descuento": 15,
        },
        {
            "PK": "PRODUCT#P002", "SK": "INFO",
            "Nombre": "Portátil WorkPro 15",
            "Precio": 2200000, "Stock": 8,
            "Categoria": "Electronica",
            "Descripcion": "Laptop profesional con procesador Intel i7, 16GB RAM y SSD 512GB.",
            "Imagen_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80",
            "Descuento": 0,
        },
        {
            "PK": "PRODUCT#P003", "SK": "INFO",
            "Nombre": "Auriculares Bluetooth Z5",
            "Precio": 120000, "Stock": 25,
            "Categoria": "Electronica",
            "Descripcion": "Auriculares inalámbricos con cancelación de ruido y 30 horas de batería.",
            "Imagen_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80",
            "Descuento": 25,
        },
        {
            "PK": "PRODUCT#P004", "SK": "INFO",
            "Nombre": "Reloj Inteligente FitTrack",
            "Precio": 350000, "Stock": 3,
            "Categoria": "Electronica",
            "Descripcion": "Smartwatch con monitor cardíaco, GPS y resistencia al agua.",
            "Imagen_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80",
            "Descuento": 0,
        },
        # Ropa
        {
            "PK": "PRODUCT#P005", "SK": "INFO",
            "Nombre": "Camiseta Algodón Hombre",
            "Precio": 45000, "Stock": 100,
            "Categoria": "Ropa",
            "Descripcion": "Camiseta 100% algodón peinado, corte slim fit.",
            "Imagen_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80",
            "Descuento": 30,
        },
        {
            "PK": "PRODUCT#P006", "SK": "INFO",
            "Nombre": "Jeans Clásico Azul",
            "Precio": 95000, "Stock": 40,
            "Categoria": "Ropa",
            "Descripcion": "Jean clásico de corte recto, tela denim premium.",
            "Imagen_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&q=80",
            "Descuento": 0,
        },
        # Hogar
        {
            "PK": "PRODUCT#P007", "SK": "INFO",
            "Nombre": "Mochila de Viaje",
            "Precio": 90000, "Stock": 50,
            "Categoria": "Hogar",
            "Descripcion": "Mochila resistente al agua, 35L de capacidad, múltiples compartimentos.",
            "Imagen_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&q=80",
            "Descuento": 20,
        },
        {
            "PK": "PRODUCT#P008", "SK": "INFO",
            "Nombre": "Lámpara LED Escritorio",
            "Precio": 75000, "Stock": 30,
            "Categoria": "Hogar",
            "Descripcion": "Lámpara LED de escritorio con intensidad regulable y puerto USB.",
            "Imagen_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&q=80",
            "Descuento": 0,
        },
        # Deportes
        {
            "PK": "PRODUCT#P009", "SK": "INFO",
            "Nombre": "Balón Fútbol Pro",
            "Precio": 60000, "Stock": 20,
            "Categoria": "Deportes",
            "Descripcion": "Balón de fútbol profesional talla 5, cuero sintético de alta durabilidad.",
            "Imagen_url": "https://images.unsplash.com/photo-1553778263-73a83bab9b0c?w=400&q=80",
            "Descuento": 10,
        },
        {
            "PK": "PRODUCT#P010", "SK": "INFO",
            "Nombre": "Tenis Running Air",
            "Precio": 280000, "Stock": 18,
            "Categoria": "Deportes",
            "Descripcion": "Zapatillas de running con amortiguación máxima y suela de goma.",
            "Imagen_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80",
            "Descuento": 40,
        },
    ]
    for item in products:
        table.put_item(Item=item)


def seed_data():
    table = dynamodb.Table('EcommerceTable')
    items = [
        # Perfiles
        {"PK": "USER#001", "SK": "PROFILE", "Nombre": "Luisa", "Correo": "l@x.com", "Direcciones": "Concepcion 2 mz v casa 20", "Metodos_de_pago": "Nequi"},
        {"PK": "USER#002", "SK": "PROFILE", "Nombre": "Carlos", "Correo": "c@x.com", "Direcciones": "Calle 45 # 12-30", "Metodos_de_pago": "Tarjeta Visa"},
        {"PK": "USER#003", "SK": "PROFILE", "Nombre": "Maria", "Correo": "m@x.com", "Direcciones": "Av. Siempre Viva 742", "Metodos_de_pago": "PSE"},

        # Credenciales
        {"PK": "USER#001", "SK": "CREDENTIALS", "Correo": "l@x.com", "Password_hash": hash_password("luisa123")},
        {"PK": "USER#002", "SK": "CREDENTIALS", "Correo": "c@x.com", "Password_hash": hash_password("carlos456")},
        {"PK": "USER#003", "SK": "CREDENTIALS", "Correo": "m@x.com", "Password_hash": hash_password("maria789")},

        # Ordenes de USER#001
        {"PK": "USER#001", "SK": "ORDER#030426", "Fecha_creacion": "2026-04-03T16:55:00Z", "Estado": "Pago exitoso", "Total": 1250},
        {"PK": "USER#001", "SK": "ORDER#020426", "Fecha_creacion": "2026-04-02T10:30:00Z", "Estado": "En camino", "Total": 320},
        {"PK": "USER#001", "SK": "ORDER#010426", "Fecha_creacion": "2026-04-01T09:00:00Z", "Estado": "Entregado", "Total": 85},

        # Ordenes de USER#002
        {"PK": "USER#002", "SK": "ORDER#040426", "Fecha_creacion": "2026-04-04T14:20:00Z", "Estado": "Pendiente", "Total": 540},
        {"PK": "USER#002", "SK": "ORDER#050426", "Fecha_creacion": "2026-04-05T08:15:00Z", "Estado": "Pago exitoso", "Total": 199},

        # Ordenes de USER#003
        {"PK": "USER#003", "SK": "ORDER#060426", "Fecha_creacion": "2026-04-03T11:45:00Z", "Estado": "Cancelado", "Total": 760},
        {"PK": "USER#003", "SK": "ORDER#070426", "Fecha_creacion": "2026-04-05T17:00:00Z", "Estado": "En camino", "Total": 430},

        # Items de ORD#030426 (Luisa - Laptop)
        {"PK": "ORD#030426", "SK": "INFO", "Fecha": "2026-04-03T16:55:00Z", "Total": 1250, "Direccion_envio": "Concepcion 2 mz v casa 20"},
        {"PK": "ORD#030426", "SK": "ITEM#01", "Producto": "Laptop XPS", "Cantidad": 1, "Precio_unitario": 1100},
        {"PK": "ORD#030426", "SK": "ITEM#02", "Producto": "Mouse Inalambrico", "Cantidad": 1, "Precio_unitario": 85},
        {"PK": "ORD#030426", "SK": "ITEM#03", "Producto": "Pad de escritorio", "Cantidad": 1, "Precio_unitario": 65},

        # Items de ORD#020426 (Luisa - Accesorios)
        {"PK": "ORD#020426", "SK": "INFO", "Fecha": "2026-04-02T10:30:00Z", "Total": 320, "Direccion_envio": "Concepcion 2 mz v casa 20"},
        {"PK": "ORD#020426", "SK": "ITEM#01", "Producto": "Teclado Mecanico", "Cantidad": 1, "Precio_unitario": 220},
        {"PK": "ORD#020426", "SK": "ITEM#02", "Producto": "Cable USB-C", "Cantidad": 2, "Precio_unitario": 50},

        # Items de ORD#010426 (Luisa - Pequeña)
        {"PK": "ORD#010426", "SK": "INFO", "Fecha": "2026-04-01T09:00:00Z", "Total": 85, "Direccion_envio": "Concepcion 2 mz v casa 20"},
        {"PK": "ORD#010426", "SK": "ITEM#01", "Producto": "Audífonos Bluetooth", "Cantidad": 1, "Precio_unitario": 85},

        # Items de ORD#040426 (Carlos)
        {"PK": "ORD#040426", "SK": "INFO", "Fecha": "2026-04-04T14:20:00Z", "Total": 540, "Direccion_envio": "Calle 45 # 12-30"},
        {"PK": "ORD#040426", "SK": "ITEM#01", "Producto": "Monitor 24\"", "Cantidad": 1, "Precio_unitario": 400},
        {"PK": "ORD#040426", "SK": "ITEM#02", "Producto": "Hub USB", "Cantidad": 2, "Precio_unitario": 70},

        # Items de ORD#050426 (Carlos)
        {"PK": "ORD#050426", "SK": "INFO", "Fecha": "2026-04-05T08:15:00Z", "Total": 199, "Direccion_envio": "Calle 45 # 12-30"},
        {"PK": "ORD#050426", "SK": "ITEM#01", "Producto": "Webcam HD", "Cantidad": 1, "Precio_unitario": 129},
        {"PK": "ORD#050426", "SK": "ITEM#02", "Producto": "Soporte para laptop", "Cantidad": 1, "Precio_unitario": 70},

        # Items de ORD#060426 (Maria - Cancelado)
        {"PK": "ORD#060426", "SK": "INFO", "Fecha": "2026-04-03T11:45:00Z", "Total": 760, "Direccion_envio": "Av. Siempre Viva 742"},
        {"PK": "ORD#060426", "SK": "ITEM#01", "Producto": "Tablet Samsung", "Cantidad": 1, "Precio_unitario": 600},
        {"PK": "ORD#060426", "SK": "ITEM#02", "Producto": "Funda Tablet", "Cantidad": 1, "Precio_unitario": 40},
        {"PK": "ORD#060426", "SK": "ITEM#03", "Producto": "Vidrio templado", "Cantidad": 2, "Precio_unitario": 60},

        # Items de ORD#070426 (Maria)
        {"PK": "ORD#070426", "SK": "INFO", "Fecha": "2026-04-05T17:00:00Z", "Total": 430, "Direccion_envio": "Av. Siempre Viva 742"},
        {"PK": "ORD#070426", "SK": "ITEM#01", "Producto": "Impresora Laser", "Cantidad": 1, "Precio_unitario": 350},
        {"PK": "ORD#070426", "SK": "ITEM#02", "Producto": "Resma de papel", "Cantidad": 4, "Precio_unitario": 20},
    ]
    for item in items:
        table.put_item(Item=item)

if __name__ == "__main__":
    # La tabla la crea CDK (PersistenceStack), no este script.
    # Esperar hasta que la tabla exista antes de cargar datos.
    table = dynamodb.Table('EcommerceTable')
    print("Esperando a que la tabla EcommerceTable esté lista...")
    table.wait_until_exists()
    seed_data()
    seed_products()
    print("Datos cargados.")
