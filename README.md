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
- **Base de Datos:** Amazon DynamoDB (Local)
- **Librerías principales:**
  - `boto3`: SDK de AWS para interactuar con DynamoDB.
  - `pydantic`: Validación de datos y esquemas.
  - `python-dotenv`: Manejo de variables de entorno.
  - `uvicorn`: Servidor ASGI para FastAPI.

### Frontend
- **Framework:** React
- **Librerías principales:**
  - `react-router-dom`: Enrutamiento.
  - `react-scripts`: Scripts de construcción y desarrollo.

### Infraestructura
- **Contenedores:** Docker y Docker Compose.
- **Servidor Web:** Nginx (para servir el Frontend en producción).

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
└── docker-compose.yml       # Orquestación de servicios (API, Frontend, DynamoDB Local)
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
   - **DynamoDB Local:** [http://localhost:8000](http://localhost:8000)

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
