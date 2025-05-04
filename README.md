# FastAPI Library API

A RESTful API for managing users and bookmarks, featuring authentication and authorization with Keycloak and persistent storage in PostgreSQL.  
Easily deployable using Docker Compose.

---

## Features

- **FastAPI**: Asynchronous, high-performance Python backend.
- **Keycloak**: User management, authentication, and authorization (OAuth2, JWT).
- **PostgreSQL**: Relational database for persistent storage.
- **Docker Compose**: Simple orchestration of the entire stack.
- **Full CRUD** for users and bookmarks, with role-based access control (admin/user).
- **Automatic Keycloak configuration import** (realms, clients, users).

---

## Architecture
[FastAPI] <--> [Keycloak] <--> [PostgreSQL]


---

## Requirements

- Docker
- Docker Compose

---

## Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/fastapi-library.git
   cd fastapi-library

2. **(Optional) Update the Keycloak import file:**

    Place your fastapi-library.json file in the keycloak/ directory.

3. **Start all services:**

   ```bash
   docker-compose up --build
4. **Access the services::**

 - FastAPI: http://localhost:8000
 - Keycloak: http://localhost:8080

 - Admin user: admin
 - Admin password: admin


5. **Main endpoints:**
 - POST /user/ — Create user (admin)
 - GET /user/ — List users (admin)
 - PATCH /user/ — Update user (admin)
 - DELETE /user/ — Delete user (admin)
 - POST /bookmark/ — Create bookmark (admin/user)
 - GET /bookmark/list/ — List bookmarks (admin/user)
 - PATCH /bookmark/ — Update bookmark (admin/user)
 - DELETE /bookmark/ — Delete bookmark (admin/user)
Note: All protected endpoints require JWT authentication via Keycloak.

---
## Authentication & Authorization
 - The system uses Keycloak for user and role management.
 - JWT tokens must be sent in the Authorization: Bearer <token> header.
