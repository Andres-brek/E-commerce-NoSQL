# E-commerce NoSQL - Proyecto DynamoDB

Este proyecto es una aplicación de e-commerce que utiliza **DynamoDB** como base de datos NoSQL, implementando una arquitectura hexagonal (Ports and Adapters).

## Información del Grupo
- **Número de Grupo:** 5
- **Integrantes:**
  - Andrés Idarraga
  - Julio Curiel
  - Jhon Galofre
  - Jabes Borre

## Stack Tecnológico

### Backend
- **Lenguaje:** Python 3.9+
- **Framework:** FastAPI
- **Base de Datos:** Amazon DynamoDB (LocalStack)
- **Caché:** Redis (patrón Cache-Aside)
- **Librerías principales:**
  - `boto3`: SDK de AWS para interactuar con DynamoDB.
  - `pydantic`: Validación de datos y esquemas.
  - `python-dotenv`: Manejo de variables de entorno.
   - `redis`: Cliente para cache distribuido.
  - `uvicorn`: Servidor ASGI para FastAPI.

### Frontend
- **Framework:** React
- **Librerías principales:**
  - `react-router-dom`: Enrutamiento.
  - `react-scripts`: Scripts de construcción y desarrollo.

### Infraestructura
- **Contenedores:** Docker y Docker Compose.
- **Servidor Web:** Nginx (para servir el Frontend en producción).
- **Servicio de caché:** Redis (puerto `6379`).
- **AWS Local:** LocalStack (puerto `4566`) + CDK Local.

---

## Estructura del Proyecto

```text
/E-commerce-NoSLQ/
├── Backend/                 # Código fuente del servidor
│   ├── adapters/            # Adaptadores de salida (Implementación de DB)
│   ├── domain/              # Lógica de negocio y Dataclasses
│   ├── ports/               # Interfaces (Puertos) de los repositorios
│   ├── services/            # Servicios de aplicación
│   ├── api.py               # Adaptadores de entrada (Endpoints FastAPI)
│   └── requirements.txt     # Dependencias de Python
├── Frontend/                # Código fuente del cliente (React)
│   └── e-commerce/
│       ├── src/
│       │   ├── components/  # Componentes reutilizables
│       │   └── pages/       # Páginas de la aplicación
│       └── Dockerfile
├── Infra/
│   └── cdk-local/           # App CDK (Python) para desplegar en LocalStack
└── docker-compose.yml       # Orquestación de servicios (API, Frontend, LocalStack, Redis)
```

---

## Instrucciones para Levantar el Proyecto

Para ejecutar todo el sistema (Base de datos local, API y Frontend), asegúrate de tener instalado **Docker** y **Docker Compose**.

1. **Clonar el repositorio:**
   ```bash
   git clone [URL-del-repositorio]
   cd E-commerce-NoSLQ
   ```

2. **Levantar los servicios:**
   Desde la raíz del proyecto, ejecuta:
   ```bash
   docker-compose up --build
   ```

3. **Acceso a los servicios:**
     - **Frontend:** [http://localhost:3000](http://localhost:3000)
     - **Backend (API):** [http://localhost:8050](http://localhost:8050)
     - **Documentación API (Swagger):** [http://localhost:8050/docs](http://localhost:8050/docs)
     - **LocalStack endpoint AWS:** [http://localhost:4566](http://localhost:4566)
     - **Redis:** `localhost:6379`

## CDK Local + LocalStack (Serverless en local)

1. Levanta el entorno base:

```bash
docker compose up -d --build
```

2. Instala dependencias del proyecto CDK dentro del contenedor `cdk-local`:

```bash
docker compose exec cdk-local sh -lc "apt-get update && apt-get install -y python3 python3-pip && npm install && pip3 install -r requirements.txt"
```

3. Bootstrap y despliegue local del stack:

```bash
docker compose exec cdk-local npm run bootstrap:local
docker compose exec cdk-local npm run deploy:local
```

4. Verifica que el backend sigue operativo contra LocalStack:

```bash
curl -s http://localhost:8050/user/001/profile
```

Notas:
- El backend usa `DYNAMODB_URL=http://localstack:4566`.
- `Backend/init_db.py` mantiene la semilla de datos para pruebas rápidas y ahora es idempotente.

---

## Abstracción de Tablas con Dataclasses

Se utilizan `dataclasses` de Python para definir las entidades de dominio, asegurando tipos fuertes y una representación clara de los datos.

- **User:** Representa el perfil de un usuario.
- **OrderItem:** Detalle de un producto en una orden (producto, cantidad, precio).
- **OrderSummary:** Resumen de una orden para listados (ID, fecha, estado, total).
- **OrderDetail:** Información completa de una orden, incluyendo su lista de items.

Ubicación: `Backend/domain/`

---

## Abstracción de Adaptadores

### Adaptadores de Entrada (Entry Adapters)
Implementados en `Backend/api.py` mediante **FastAPI**. Estos adaptadores reciben las peticiones HTTP, validan los datos de entrada usando Pydantic y delegan la ejecución a los servicios de dominio.

### Adaptadores de Salida (Output Adapters / Persistencia)
Ubicación: `Backend/adapters/dynamodb.py`.
Implementan los repositorios definidos en `Backend/ports/repositories.py`. Estos adaptadores se encargan de la comunicación directa con **DynamoDB**, realizando consultas (`query`), escaneos (`scan`) y recuperación de ítems (`get_item`).

---

## Caché Aside en Backend

El backend implementa estrategia **Cache-Aside** en los repositorios de lectura:

- `GET /user/{user_id}/profile`
- `GET /user/{user_id}/orders`
- `GET /order/{order_id}`

Flujo aplicado:

1. El repositorio cacheado consulta primero Redis.
2. Si existe dato en caché (**hit**), responde desde Redis.
3. Si no existe (**miss**), consulta DynamoDB y luego guarda el resultado en Redis con TTL.

Configuración en `Backend/.env`:

```env
REDIS_URL=redis://redis:6379/0
CACHE_TTL_SECONDS=120
```

## Instructivo de pruebas: demostrar Cache-Aside

Este flujo permite evidenciar que:
1. La primera consulta es **miss** (lee DynamoDB y guarda en Redis).
2. La segunda consulta es **hit** (responde desde Redis).
3. El payload de ambas respuestas es el mismo.

### 1) Reiniciar estado de caché y validar métricas en cero

```bash
docker exec redis redis-cli FLUSHDB
curl -s http://localhost:8050/cache/metrics
```

Resultado esperado: `{}`.

### 2) Probar caché en perfil de usuario

```bash
curl -s -o /tmp/profile1.json -w "t1=%{time_total}\n" http://localhost:8050/user/001/profile
curl -s -o /tmp/profile2.json -w "t2=%{time_total}\n" http://localhost:8050/user/001/profile
curl -s http://localhost:8050/cache/metrics
curl -s "http://localhost:8050/cache/keys?limit=20"
sha256sum /tmp/profile1.json /tmp/profile2.json
```

Resultado esperado:
- Métricas con `profile_misses: 1` y `profile_hits: 1`.
- Clave `cache:data:user:profile:001` con TTL positivo.
- `t2 < t1` (normalmente notablemente menor).
- Hash idéntico entre `profile1.json` y `profile2.json`.

### 3) Probar caché en órdenes y detalle de orden

```bash
curl -s -o /tmp/orders1.json -w "t1=%{time_total}\n" http://localhost:8050/user/001/orders
curl -s -o /tmp/orders2.json -w "t2=%{time_total}\n" http://localhost:8050/user/001/orders
curl -s -o /tmp/orderd1.json -w "t1=%{time_total}\n" http://localhost:8050/order/030426
curl -s -o /tmp/orderd2.json -w "t2=%{time_total}\n" http://localhost:8050/order/030426
curl -s http://localhost:8050/cache/metrics
curl -s "http://localhost:8050/cache/keys?limit=20"
sha256sum /tmp/orders1.json /tmp/orders2.json
sha256sum /tmp/orderd1.json /tmp/orderd2.json
```

Resultado esperado:
- Incrementos en `orders_misses/orders_hits` y `order_detail_misses/order_detail_hits`.
- Claves:
  - `cache:data:user:orders:001`
  - `cache:data:order:detail:030426`
- Segunda llamada más rápida y mismo contenido (hash igual).
