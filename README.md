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
- **Framework:** React
- **Librerías:**
  - `react-router-dom` (ruteo)
  - `react-scripts`

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
│       │   ├── components/   # Componentes reutilizables
│       │   └── pages/        # Páginas de la app
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

- **Arquitectura hexagonal**: separación de lógica de negocio, adaptadores y puertos (facilita testing y evolución).
- **DynamoDB gestionado localmente:** via LocalStack y AWS CDK (infraestructura reproducible, rápido arranque/destrucción).
- **Caché Aside sobre Redis:** para endpoints críticos reduce latencia en lecturas repetidas.
- **Seeds de datos automáticos**: init_db.py crea la tabla y carga datos idempotentemente en DynamoDB (útil para pruebas/no requiere scripts manuales).
- **Infraestructura como Código (IaC) para DynamoDB:** Desde `/Infra/cdk-local`. Usa scripts npm y AWS CDK local para crear/eliminar recursos.
- **Frontend desacoplado:** UI moderna en React, consumiendo API REST documentada en Swagger.
- **Flujo de desarrollo 100% local:** No requiere AWS real (LocalStack + CDK + Redis + Docker Compose).
- **API auto-documentada:** Swagger/OpenAPI en `/docs` (FastAPI).
- **Contenedores robustos:** Cada servicio con su Dockerfile; integración con Docker Compose.
- **Orquestación completa:** Incluye Redis, Backend, Frontend, LocalStack y CDK listos para desarrollo colaborativo.

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

## ⚙️ Estrategia Cache-Aside en Backend

El backend cachea resultados de endpoints intensivos en lectura usando Redis. Flujos clave:

1. **Consulta perfil de usuario:**
    - `GET /user/{user_id}/profile`
2. **Órdenes del usuario:**
    - `GET /user/{user_id}/orders`
3. **Detalle de orden:**
    - `GET /order/{order_id}`

**Flujo:**
- 1º revisa Redis; si HIT responde desde caché. Si MISS, consulta a DynamoDB y almacena en Redis con TTL.

Variables .env:
```ini
REDIS_URL=redis://redis:6379/0
CACHE_TTL_SECONDS=120
```

---

## 🧪 Test rápido de cache-aside (ejemplo)

```bash
# Limpiar el caché (opcional, para métricas)
docker exec redis redis-cli FLUSHDB

# Primera consulta (MISS, tarda más)
curl -s -o /tmp/profile1.json -w "t1=%{time_total}\n" http://localhost:8050/user/001/profile

# Segunda consulta (HIT, mucho más rápido)
curl -s -o /tmp/profile2.json -w "t2=%{time_total}\n" http://localhost:8050/user/001/profile

# Métricas de caché:
curl -s http://localhost:8050/cache/metrics

# Claves activas
docker exec redis redis-cli KEYS 'cache:data:*'

# Los JSON deberían tener el mismo hash:
sha256sum /tmp/profile1.json /tmp/profile2.json
```
**Esperado:** Métrica "miss" en primera, "hit" en segunda, mismo contenido en ambas respuestas, segundo request más rápido.

---

## 🏛️ Arquitectura Hexagonal: Resumen

**Dominios y sus adaptadores:**
- **Entidades:** User, OrderItem, OrderSummary, OrderDetail (`Backend/domain/`)
- **Adaptadores de entrada:** FastAPI en `Backend/api.py`, validación con Pydantic
- **Adaptadores de salida:** `Backend/adapters/dynamodb.py`, implementando los puertos definidos en `Backend/ports/`

---

## 📜 Documentación y Endpoints

- API documentada en Swagger en `/docs` (FastAPI)
- CDK Infraestructura local en `/Infra/cdk-local/` y scripts npm (`bootstrap:local`, `deploy:local`)

---

## 📝 Notas finales y buenas prácticas

- **Infraestructura reproducible:** Terraform/Cognito no requeridos, sólo Docker y Docker Compose
- **CDK + LocalStack:** Completamente automáticos
- **Seeds idempotentes:** No hay duplicados, siempre tienes entorno funcional al arrancar
- **Frontend y backend desacoplados:** Puedes conectar UI o Postman al REST API
- **Testing local fácil:** Simple con Docker Compose, sin dependencias externas
- **Actualizado a mayo 2026**
