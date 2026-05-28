# E-commerce NoSQL – Proyecto con DynamoDB, LocalStack y Arquitectura Hexagonal

Este proyecto es una plataforma de e-commerce que utiliza **Amazon DynamoDB** como base de datos NoSQL, infraestructura definida por código (IaC) con AWS CDK y despliegue local en LocalStack, aplicando arquitectura hexagonal (Ports & Adapters).

---

## 🧑‍💻 Información del Grupo
- **Número de Grupo:** 5
- **Integrantes:**
  - Andrés Idarraga
  - Julio Curiel
  - Jhon Galofre
  - Jabes Borre

---

## 🚀 Stack Tecnológico

### Backend
- **Lenguaje:** Python 3.9+
- **Framework:** FastAPI
- **Base de Datos:** Amazon DynamoDB (simulada con LocalStack)
- **Caché:** Redis (estrategia Cache-Aside)
- **Infraestructura:** AWS CDK (Python) + LocalStack
- **Librerías principales:**
  - `boto3` (AWS SDK Python)
  - `pydantic` (modelos/validación de datos)
  - `redis` (cliente Redis Python)
  - `python-dotenv` (manejo de variables de entorno)
  - `uvicorn` (servidor FastAPI)

### Frontend
- **Framework:** React 18
- **Librerías:**
  - `react-router-dom` v6 (ruteo + `useSearchParams` para estado en URL)
  - `react-scripts`
- **Estado:** React hooks nativos (`useState`, `useEffect`, `useRef`) — sin Redux
- **Hook propio:** `useDebounce` para búsqueda diferida

### Infraestructura & DevOps
- **Contenedores:** Docker y Docker Compose
- **Servidor Web:** Nginx (para producción frontend)
- **Servicio de caché:** Redis (`6379`)
- **AWS Local:** LocalStack (puerto `4566`) + CDK Local

---

## 📁 Estructura del Proyecto

```text
/E-commerce-NoSQL/
├── Backend/                  # Backend (API, Dominio, Adapters, Puertos)
│   ├── adapters/             # Adaptadores de persistencia (DynamoDB)
│   ├── domain/               # Dataclasses de negocio
│   ├── ports/                # Interfaces (puertos hexagonales)
│   ├── services/             # Servicios core
│   ├── api.py                # Endpoints (FastAPI)
│   ├── init_db.py            # Inicializador/semilla de datos DynamoDB
│   └── requirements.txt      # Dependencias Python
├── Frontend/
│   └── e-commerce/
│       ├── src/
│       │   ├── components/   # Nav (header con búsqueda, carrito, perfil)
│       │   ├── pages/        # HomePage, CartPage, LoginPage, OrdersPage
│       │   ├── hooks/        # useDebounce (búsqueda diferida)
│       │   ├── config.js     # URL del API (placeholder reemplazado en runtime)
│       │   ├── App.js        # Rutas + estado global del carrito
│       │   └── App.css       # Estilos globales
│       └── Dockerfile
├── Infra/
│   └── cdk-local/            # AWS CDK app para infraestructura local
│       ├── app.py, stacks/
│       └── package.json, requirements.txt
├── docker-compose.yml        # Orquestación completa (API, Frontend, Redis, LocalStack, CDK)
└── README.md
```

---

## ✨ Principales Características y Funcionalidades

### Arquitectura y backend
- **Arquitectura hexagonal**: separación de lógica de negocio, adaptadores y puertos (facilita testing y evolución).
- **DynamoDB gestionado localmente:** via LocalStack y AWS CDK (infraestructura reproducible, rápido arranque/destrucción).
- **Backend serverless:** una sola Lambda (`ecommerce-handler`) detrás de API Gateway, con router interno por regex.
- **Caché-Aside sobre Redis:** endpoints críticos cacheados con TTL configurable e invalidación automática tras escrituras (checkout).
- **Seeds de datos automáticos**: `init_db.py` crea la tabla y carga datos idempotentemente en DynamoDB.
- **Infraestructura como Código:** AWS CDK en `/Infra/cdk-local` con dos stacks (`PersistenceStack`, `ApiStack`).

### Funcionalidades del usuario (frontend)
- **Catálogo completo** con imágenes, precios en COP, stock y filtro por categoría (Electrónica, Ropa, Hogar, Deportes).
- **Búsqueda con debounce (350 ms)** tolerante a tildes y mayúsculas (`audífono` ≈ `Audifono`).
- **Sistema de ofertas:** productos con descuento, badge `−N%`, precio anterior tachado, vista dedicada `/?ofertas=1`.
- **Carrito persistente** con selector de cantidad (botones `−/+` + input numérico) — cap automático al stock disponible.
- **Checkout atómico:** `TransactWriteItems` crea la orden + decrementa stock con `ConditionExpression` (evita oversell concurrente).
- **Fecha de entrega automática:** se calcula como `fecha_compra + 5 días`.
- **Mis pedidos:** historial con estados de color, fecha de entrega y detalle por orden.
- **Login con perfil:** dropdown del navbar muestra nombre y dirección de envío por defecto.

### DevOps y testing
- **Flujo de desarrollo 100% local:** No requiere AWS real (LocalStack + CDK + Redis + Docker Compose).
- **Contenedores robustos:** cada servicio con su Dockerfile; orquestación completa con Docker Compose.
- **URL del API inyectada en runtime:** el frontend usa un placeholder reemplazado por `sed` al arrancar nginx, así el mismo bundle sirve para cualquier deploy.

---

## ⚡ Instalación y Ejecución Rápida

**Requisitos:** [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/)

```bash
# 1. Clona el repositorio
 git clone https://github.com/Andres-brek/E-commerce-NoSQL.git
 cd E-commerce-NoSQL

# 2. Levanta todos los servicios
 docker-compose up --build
```

**Servicios:**
- **Frontend:** http://localhost:3000
- **Backend (API):** http://localhost:8050
- **Swagger Docs:** http://localhost:8050/docs
- **LocalStack AWS Endpoint:** http://localhost:4566
- **Redis:** localhost:6379

---

## 🏗️ Despliegue de DynamoDB y recursos con CDK/LocalStack

**Gestiona la infraestructura DynamoDB usando AWS CDK y LocalStack para pruebas locales.**

1. **Inicia LocalStack & cdk-local:**
   ```bash
   docker-compose up -d --build
   ```
2. **Instala dependencias CDK dentro del contenedor cdk-local:**
   ```bash
   docker compose exec cdk-local sh -lc "apt-get update && apt-get install -y python3 python3-pip && npm install && pip3 install -r requirements.txt"
   ```
3. **Bootstrap y despliega stack DynamoDB local:**
   ```bash
   docker compose exec cdk-local npm run bootstrap:local
   docker compose exec cdk-local npm run deploy:local
   ```
4. **Verifica backend con seed de datos:**
   ```bash
   curl -s http://localhost:8050/user/001/profile
   ```

**Notas:**
- El backend debe tener `DYNAMODB_URL=http://localstack:4566`
- El script `Backend/init_db.py` carga datos iniciales cada vez que inicia (idempotente)

---

## 🛰️ Arquitectura Serverless (LocalStack + CDK + Lambda + API Gateway)

El backend **no corre como un servidor tradicional** (no hay un proceso `uvicorn` ni `gunicorn` escuchando un puerto). Todo el API se ejecuta como una **función Lambda** detrás de **API Gateway**, ambos emulados localmente por LocalStack.

### Componentes y flujo de una request

```
Navegador (React :3000)
        │  fetch("https://<api-id>.execute-api.localhost.localstack.cloud:4566/prod/...")
        ▼
API Gateway  (LocalStack :4566)
        │  Lambda proxy integration
        ▼
Lambda  ecommerce-handler  (Python 3.12, runtime LocalStack)
        │  ├─► Redis (contenedor aparte, :6379)   ◄── cache-aside
        │  └─► DynamoDB  (LocalStack)             ◄── fuente de verdad
        ▼
Respuesta JSON (proxy response) → API Gateway → Navegador
```

### Una sola Lambda, múltiples rutas

`Backend/lambdas/ecommerce.py` es el **único handler** del API. En lugar de tener una Lambda por endpoint, todas las rutas (`/login`, `/user/{id}/profile`, `/products`, etc.) están integradas como **Lambda Proxy** sobre la misma función, y un router interno por regex (`_ROUTES`) despacha al servicio correcto según `httpMethod` y `path` del evento de API Gateway. Ventaja: un solo cold start, un solo zip, wiring compartido (clientes de DynamoDB y Redis se reutilizan entre invocaciones tibias).

### Cold start vs warm

- **Cold start:** primera invocación tras desplegar. El módulo `lambdas/ecommerce.py` se carga, se instancian los clientes (`boto3` para DynamoDB, `redis.Redis` si `REDIS_URL` está seteada), se envuelven los repos con los decoradores cache-aside y se imprime `[CACHE] Redis enabled at ...` en stdout.
- **Warm:** invocaciones siguientes reutilizan los clientes ya creados (variables a nivel de módulo). Solo se ejecuta el `handler(event, context)`.

### Infraestructura como Código (CDK)

La infra está definida en [Infra/cdk-local/](Infra/cdk-local/) usando AWS CDK en Python. Hay dos stacks:

| Stack | Archivo | Qué define |
|-------|---------|-----------|
| `PersistenceStack` | [stacks/persistence_stack.py](Infra/cdk-local/stacks/persistence_stack.py) | Tabla DynamoDB `EcommerceTable` (PK + SK), 5 RCU / 5 WCU, single-table design |
| `ApiStack` | [stacks/api_stack.py](Infra/cdk-local/stacks/api_stack.py) | Función Lambda + REST API Gateway con todos los endpoints y CORS preflight |

El deploy se ejecuta con `cdklocal` (CDK apuntando a LocalStack en vez de AWS real), gracias a la dependencia `aws-cdk-local`. Scripts en [package.json](Infra/cdk-local/package.json):

```bash
npm run bootstrap:local   # prepara el toolkit stack de CDK en LocalStack
npm run deploy:local      # despliega PersistenceStack + ApiStack
npm run destroy:local     # destruye ambos stacks
```

### Cómo se conecta el frontend al API

API Gateway en LocalStack expone cada REST API en un subdominio `<api-id>.execute-api.localhost.localstack.cloud:4566`. El `api-id` cambia en cada redeploy, así que el contenedor `cdk-local`:

1. Espera a que CDK termine de desplegar.
2. Consulta el `api-id` actual con `boto3` contra el API Gateway de LocalStack.
3. Escribe la URL completa en `/shared/api_url.txt` (volumen compartido).
4. El contenedor `frontend` lee ese archivo y reemplaza el placeholder `__API_URL__` en los archivos JS de React **al iniciar nginx** (no en build-time), así el mismo bundle sirve para cualquier deploy.

### Por qué `REDIS_URL` se inyecta vía el contenedor `cdk-local`

El Lambda recibe variables de entorno solo si están definidas en su `environment` al momento del deploy. El [api_stack.py:35](Infra/cdk-local/stacks/api_stack.py#L35) hace:

```python
"REDIS_URL": os.environ.get("REDIS_URL", "")
```

Eso lee la variable **del shell donde corre `cdk deploy`** — que es el contenedor `cdk-local`. Por eso `docker-compose.yml` la setea ahí, no en el Lambda directamente.

### Diferencia con un backend tradicional

| Backend tradicional (FastAPI / Express) | Este backend (Lambda) |
|----------------------------------------|----------------------|
| Proceso permanente escuchando un puerto | Función efímera invocada por evento |
| Estado en memoria persiste mientras vive el proceso | Estado solo persiste entre invocaciones tibias (no garantizado) |
| Logs en stdout van directo al contenedor | Logs van a CloudWatch (emulado) — se leen con `awslocal logs tail` |
| Escala vertical / añadiendo réplicas | Escala automática por concurrencia de invocaciones |
| Conexión a Redis/DB de larga duración | Conexión se crea en cold start y se reusa en warm |

### Cómo inspeccionar la infraestructura desplegada

```bash
# Listar APIs Gateway
docker exec localstack awslocal apigateway get-rest-apis

# Listar funciones Lambda
docker exec localstack awslocal lambda list-functions

# Ver la URL completa del API que usa el frontend
docker exec cdk-local cat /shared/api_url.txt

# Invocar el Lambda directamente (sin pasar por API Gateway)
docker exec localstack sh -c 'echo "{\"httpMethod\":\"GET\",\"path\":\"/products\"}" > /tmp/p.json && \
  awslocal lambda invoke --function-name ecommerce-handler --payload file:///tmp/p.json /tmp/out.json && \
  cat /tmp/out.json'

# Ver logs del Lambda en vivo
docker exec localstack awslocal logs tail /aws/lambda/ecommerce-handler --follow
```

---

## 🎨 Frontend — Mi Mercado Global

El frontend es una **SPA en React** que consume el API serverless. Está dividido en 4 páginas y un componente de navegación compartido. Todo el estado del carrito vive en `App.js` y se pasa por props (sin Redux ni Context).

### 📄 Páginas y rutas

| Ruta | Página | Acceso | Función |
|------|--------|--------|---------|
| `/` | `HomePage` | Pública | Catálogo de productos con filtro por categoría y soporte para `?q=`, `?categoria=`, `?ofertas=1` |
| `/cart` | `CartPage` | Pública (compra requiere login) | Resumen del carrito + checkout |
| `/login` | `LoginPage` | Pública | Autenticación contra `POST /login` |
| `/orders` | `OrdersPage` | Requiere login | Lista de pedidos del usuario + detalle de cada uno |

La rutas están en [src/App.js](Frontend/e-commerce/src/App.js). Si el usuario no está logueado e intenta entrar a `/orders`, se redirige a `/login` (guard básico).

### 🧭 Navbar (componente `Nav`)

El [Nav](Frontend/e-commerce/src/components/Nav.js) es un **grid de 4 columnas** que se adapta a pantallas grandes y pequeñas:

```
[ Logo ]  [ ─── Buscador (centrado) ─── ]  [ Links ]  [ 🛒 Carrito | 👤 Perfil ]
```

- **Buscador con debounce (350ms)**: escribir actualiza `?q=` en la URL después de la pausa, evitando peticiones por cada tecla. Si estás en `/cart` u `/orders` y buscas, te lleva al home automáticamente.
- **Link de Ofertas**: navega a `/?ofertas=1` — la HomePage filtra solo productos con descuento.
- **Dropdown de perfil**: si hay sesión, muestra nombre, dirección por defecto, enlace a "Mis Pedidos" y "Cerrar sesión". Si no hay sesión, muestra "Iniciar sesión".
- **Badge del carrito**: contador rojo en la esquina del icono 🛒 con la cantidad total de ítems.
- **Responsive**: en pantallas `<1100px` se ocultan los links (solo quedan logo + buscador + carrito + perfil). En `<640px` el padding se reduce más.

### 🛍️ HomePage — Catálogo

[HomePage.js](Frontend/e-commerce/src/pages/HomePage.js) lee el estado de la URL (`useSearchParams`) y consulta `/products` con los filtros aplicables. La URL es la **fuente única de verdad** del estado de filtrado, así Nav y página quedan sincronizados sin estado global.

**Sidebar de categorías:** Todas, Electrónica, Ropa, Hogar, Deportes. Click cambia `?categoria=X` en la URL.

**Cards de producto** muestran:
- Imagen del producto (URL externa de Unsplash)
- Nombre, precio formateado en COP, stock disponible
- Si el producto está en oferta: **badge rojo `−N%`** en la esquina superior derecha, precio anterior tachado y precio final en rojo
- Botón "Añadir al Carrito" o, si ya está en el carrito, un **selector −/input/+** para ajustar la cantidad manualmente (no permite pasar del stock disponible)
- Si `stock === 0`: botón "Sin stock" deshabilitado

### 🔍 Búsqueda con debounce y tolerancia a tildes

El hook [useDebounce.js](Frontend/e-commerce/src/hooks/useDebounce.js) retrasa la propagación del valor del input 350 ms tras la última pulsación. Cada cambio cancela el timer previo, así una consulta solo viaja al backend cuando el usuario para de escribir.

Para que `audífono`, `audifono`, `AUDIFONO` y `Audífono` devuelvan los mismos resultados, el backend normaliza ambas cadenas (consulta + nombre del producto) con `unicodedata.normalize("NFD", ...)` antes de comparar. Eso elimina diacríticos y baja a minúsculas. Implementado en [Backend/adapters/dynamodb.py](Backend/adapters/dynamodb.py).

### 🏷️ Sistema de ofertas

Los productos pueden tener un campo `descuento` (porcentaje 0-100) en DynamoDB. El backend expone:

```
GET /products?ofertas=1     → solo productos con Descuento > 0
GET /products?ofertas=1&categoria=Ropa  → ofertas filtradas por categoría
```

Cada producto del response incluye `descuento` y `precio_final` (calculado como `precio * (100 - descuento) / 100`). El frontend usa `precio_final` para el carrito, así el checkout cobra el precio correcto sin lógica adicional.

Productos sembrados con oferta (ver [Backend/init_db.py](Backend/init_db.py)):

| Producto | Descuento |
|----------|-----------|
| Tenis Running Air | **40%** 🔥 |
| Camiseta Algodón Hombre | 30% |
| Auriculares Bluetooth Z5 | 25% |
| Mochila de Viaje | 20% |
| Teléfono Inteligente X100 | 15% |
| Balón Fútbol Pro | 10% |

### 🛒 Carrito y checkout

El estado del carrito vive en [App.js](Frontend/e-commerce/src/App.js) como un array `[{id, nombre, precio, qty, ...}]`. Dos handlers se pasan por props:

- `onAddToCart(product)`: añade o suma uno (capeando al stock).
- `onSetQty(product, qty)`: setea la cantidad exacta (qty=0 elimina, valores mayores al stock se capean).

Al añadir un producto en oferta, [App.js](Frontend/e-commerce/src/App.js) lo "normaliza" — guarda el `precio_final` como `precio` y conserva el original en `precio_original`. Así la lógica del carrito (subtotales, totales, checkout) no necesita preguntarse por descuentos.

[CartPage.js](Frontend/e-commerce/src/pages/CartPage.js) muestra los items con sus subtotales, dirección de envío por defecto del perfil, y un botón "Proceder al pago" que hace:

```js
POST /checkout
{
  "user_id": "001",
  "direccion_envio": "Concepcion 2 mz v casa 20",
  "items": [{ "product_id": "P003", "cantidad": 2 }]
}
```

El backend crea la orden de forma **atómica** con `TransactWriteItems` (ver [Backend/adapters/dynamodb.py](Backend/adapters/dynamodb.py)):
1. Valida que cada producto exista y haya stock suficiente
2. En una sola transacción: escribe el header de la orden en `USER#<uid>` y en `ORD#<oid>`, escribe los items, **decrementa el stock** con `ConditionExpression: Stock >= :q` (evita oversell si dos checkouts compiten)
3. Calcula la **fecha de entrega = fecha actual + 5 días**
4. Devuelve `order_id`, `fecha_creacion`, `fecha_entrega`, `total`, `estado`

Tras el éxito, el carrito se vacía y se muestra una **pantalla de confirmación** con el número de orden, total cobrado y fecha estimada de entrega.

### 📦 OrdersPage — Mis Pedidos

[OrdersPage.js](Frontend/e-commerce/src/pages/OrdersPage.js) muestra una tabla de pedidos con estado, fecha de creación y **entrega estimada**. Click en un pedido carga el detalle (items, precios, subtotales, dirección, fecha de entrega) en la columna derecha.

El estado del pedido se muestra con un **badge de color** según el valor:

| Estado | Badge |
|--------|-------|
| Pago exitoso, Entregado | 🟢 Verde |
| En camino | 🟠 Naranja |
| Pendiente | 🟡 Amarillo |
| Cancelado | 🔴 Rojo |

### 🔗 Cómo se entera el frontend de la URL del API

El frontend nunca conoce la URL del API en build-time. En su lugar, [src/config.js](Frontend/e-commerce/src/config.js) contiene un placeholder:

```js
const API = '__API_URL__';
```

Al **arrancar nginx**, el contenedor `frontend` lee `/shared/api_url.txt` (volumen compartido con `cdk-local`) y hace un `sed` sobre los `.js` ya compilados para reemplazar el placeholder. Así el mismo bundle sirve en cualquier deploy — el `api-id` de API Gateway cambia y el frontend se adapta sin rebuild.

---

## ⚙️ Estrategia Cache-Aside con Redis

El Lambda `ecommerce-handler` (desplegado en LocalStack vía CDK) cachea en Redis los resultados de los endpoints más leídos. Flujos cacheados:

1. **Login (credenciales):** `POST /login` → clave `cache:data:user:credentials:<correo>`
2. **Perfil de usuario:** `GET /user/{user_id}/profile` → `cache:data:user:profile:<user_id>`
3. **Órdenes del usuario:** `GET /user/{user_id}/orders` → `cache:data:user:orders:<user_id>`
4. **Detalle de orden:** `GET /order/{order_id}` → `cache:data:order:detail:<order_id>`
5. **Catálogo completo:** `GET /products` → `cache:data:products:all`
6. **Producto por categoría / id / búsqueda:** claves `cache:data:products:*`
7. **Ofertas:** `GET /products?ofertas=1` → `cache:data:products:on_sale`

**Invalidación al hacer checkout:** cuando se crea una orden, el `CachedOrderRepository` invalida automáticamente:
- `cache:data:user:orders:<uid>` — la lista de pedidos del usuario quedó desactualizada
- `cache:data:products:*` — el stock de los productos comprados cambió

Así la próxima lectura va a DynamoDB y refresca el cache con los datos correctos.

### Cómo funciona internamente

- **Redis corre fuera de LocalStack**, como un contenedor aparte de Docker Compose (`redis:7-alpine` en el puerto `6379`). LocalStack solo emula servicios AWS (DynamoDB, API Gateway, Lambda, S3, etc.) y **no** emula ElastiCache — por eso Redis va separado.
- El `docker-compose.yml` inyecta `REDIS_URL=redis://redis:6379/0` en el contenedor `cdk-local`. El CDK, al hacer el deploy del Lambda, propaga esa variable al `environment` de la función (`Infra/cdk-local/stacks/api_stack.py`).
- En el cold start del Lambda (`Backend/lambdas/ecommerce.py`), si `REDIS_URL` está definida, los repos de DynamoDB se envuelven con los decoradores cache-aside de `Backend/adapters/cache.py` (`CachedUserRepository`, `CachedOrderRepository`, `CachedProductRepository`). Si no, el Lambda usa DynamoDB directo sin caché.
- El paquete `redis` se instala dentro de `Backend/` antes del deploy (`pip install --target /workspace/Backend redis`), porque `Code.from_asset` sube todo el directorio al Lambda y no procesa `requirements.txt` automáticamente.

### Patrón Cache-Aside

1. El Lambda revisa Redis. Si HIT → responde desde caché y registra hit en `cache:metrics`.
2. Si MISS → consulta DynamoDB, guarda el resultado en Redis con TTL y registra miss.
3. El TTL por defecto es **120 segundos** (`CACHE_TTL_SECONDS`).

### Variables de entorno relevantes

```ini
REDIS_URL=redis://redis:6379/0
CACHE_TTL_SECONDS=120
```

---

## 🧪 Cómo verificar que Redis está sirviendo

Como `docker logs redis` solo muestra el arranque (Redis no logea operaciones por defecto), hay que mirar adentro:

### Ver el tráfico de Redis en vivo

```bash
docker exec -it redis redis-cli MONITOR
```

Esto imprime cada comando (`GET`, `SET`, `HINCRBY`...) en tiempo real mientras navegas la app. Es la forma más directa de **confirmar que Redis está sirviendo**.

### Listar las claves cacheadas

```bash
docker exec redis redis-cli KEYS "cache:*"
```

Ejemplo de salida después de hacer login y abrir el catálogo:

```
cache:metrics
cache:data:user:profile:001
cache:data:user:credentials:l@x.com
cache:data:products:all
cache:data:user:orders:001
cache:data:order:detail:030426
```

### Ver métricas de hits / misses

```bash
docker exec redis redis-cli HGETALL cache:metrics
```

### Ver el TTL restante de una clave

```bash
docker exec redis redis-cli TTL "cache:data:products:all"
```

### Ver los `print` del Lambda (CloudWatch emulado)

El Lambda imprime `[CACHE HIT]` / `[CACHE MISS]` en stdout. Esos logs no aparecen en `docker logs localstack`; van al CloudWatch emulado:

```bash
docker exec localstack awslocal logs tail /aws/lambda/ecommerce-handler --follow
```

### Test rápido

```bash
# 1. Limpia el caché
docker exec redis redis-cli FLUSHDB

# 2. Primera llamada → MISS (consulta DynamoDB y cachea)
curl -s http://localhost:3000  # carga la app
# … haz login y abre el catálogo en el navegador

# 3. Segunda llamada → HIT (respuesta desde Redis)
# Refresca la página y revisa MONITOR — deberías ver solo GETs, no escrituras

# 4. Métricas acumuladas
docker exec redis redis-cli HGETALL cache:metrics
```

**Esperado:** la primera carga genera misses; los refrescos siguientes (dentro de 120s) generan hits y son notablemente más rápidos.

---

## 🏛️ Arquitectura Hexagonal: Resumen

**Dominios y sus adaptadores:**
- **Entidades:** User, Product, OrderItem, OrderSummary, OrderDetail, CheckoutItem, CheckoutResult (`Backend/domain/`)
- **Puertos (interfaces):** `UserRepository`, `OrderRepository`, `ProductRepository` en `Backend/ports/repositories.py`
- **Servicios de dominio:** `UserService`, `OrderService`, `ProductService` en `Backend/services/` — solo dependen de los puertos
- **Adaptadores de entrada:** Lambda handler con router por regex en `Backend/lambdas/ecommerce.py`
- **Adaptadores de salida:**
  - `DynamoUserRepository`, `DynamoOrderRepository`, `DynamoProductRepository` en `Backend/adapters/dynamodb.py`
  - `CachedUserRepository`, `CachedOrderRepository`, `CachedProductRepository` en `Backend/adapters/cache.py` (decoradores cache-aside)

---

## 📜 Endpoints disponibles

Todas las rutas pasan por API Gateway de LocalStack y se enrutan a la Lambda `ecommerce-handler`. El router interno está en [Backend/lambdas/ecommerce.py](Backend/lambdas/ecommerce.py).

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/login` | Autenticación con `correo` + `password`. Devuelve perfil del usuario. |
| `POST` | `/checkout` | Crea una orden (atómico). Body: `{ user_id, items: [{product_id, cantidad}], direccion_envio }`. |
| `GET` | `/user/{user_id}/profile` | Perfil del usuario. |
| `GET` | `/user/{user_id}/orders` | Lista de pedidos del usuario (incluye `Fecha_entrega`). |
| `GET` | `/order/{order_id}` | Detalle de un pedido (items, totales, estado, fechas). |
| `GET` | `/products` | Catálogo completo. Acepta query params: |
|        |              | `?q=texto` → búsqueda libre (tolerante a tildes) |
|        |              | `?categoria=Ropa` → filtro por categoría |
|        |              | `?ofertas=1` → solo productos con descuento |
| `GET` | `/products/{id}` | Detalle de un producto. |
| `GET` | `/cache/metrics` | Métricas de hits/misses por scope. |
| `GET` | `/cache/keys?limit=N` | Lista las claves cacheadas y su TTL. |

**CORS**: habilitado para todos los orígenes con `default_cors_preflight_options` en `ApiStack`.

---

## 📝 Notas finales y buenas prácticas

- **Infraestructura reproducible:** Terraform/Cognito no requeridos, sólo Docker y Docker Compose
- **CDK + LocalStack:** Completamente automáticos
- **Seeds idempotentes:** No hay duplicados, siempre tienes entorno funcional al arrancar
- **Frontend y backend desacoplados:** Puedes conectar UI o Postman al REST API
- **Testing local fácil:** Simple con Docker Compose, sin dependencias externas
- **Actualizado a mayo 2026** — última iteración incluye sistema completo de catálogo, búsqueda, ofertas, carrito y checkout
