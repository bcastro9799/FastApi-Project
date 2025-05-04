import os

URL_PREFIX = "/library"

USER_ROLE = "user"
ADMIN_ROLE = "appadmin"

KEYCLOAK_AUTH_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_CLIENT_ID = "fastapi-library"
KEYCLOAK_REALM_ID = "fastapi-library"
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_SWAGGER_AUTH_URL = f"/token"


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
