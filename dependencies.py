from keycloak import KeycloakOpenID, KeycloakAdmin
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db.database import AsyncSessionLocal
from schemas.token_data import TokenData
import constants as constants


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=constants.KEYCLOAK_SWAGGER_AUTH_URL)

keycloak_openid = KeycloakOpenID(
    server_url=constants.KEYCLOAK_AUTH_URL,
    client_id=constants.KEYCLOAK_CLIENT_ID,
    realm_name=constants.KEYCLOAK_REALM_ID,
    client_secret_key=constants.KEYCLOAK_CLIENT_SECRET,
    verify=True,
)

keycloak_admin = KeycloakAdmin(
    server_url=constants.KEYCLOAK_AUTH_URL,
    client_id=constants.KEYCLOAK_CLIENT_ID,
    realm_name=constants.KEYCLOAK_REALM_ID,
    user_realm_name=constants.KEYCLOAK_REALM_ID,
    client_secret_key=constants.KEYCLOAK_CLIENT_SECRET,
    verify=True,
)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)


def get_attributes_by_user(user_id: str) -> dict:
    try:
        return keycloak_admin.get_user(user_id)["attributes"]
    except Exception:
        return None


def get_query_token(token: str = Depends(oauth2_scheme)):
    data = keycloak_openid.introspect(token)
    return TokenData.model_validate(data)


def authorization(token: TokenData = Depends(get_query_token)):
    if token is None:
        raise credentials_exception

    if token.active == False:
        raise credentials_exception
    
    return token


def role_authorization(token: TokenData = Depends(authorization)):
    if token.realm_access is None:
        raise credentials_exception

    if token.realm_access.roles is None:
        raise credentials_exception

    return token


def user_authorization(token: TokenData = Depends(role_authorization)):
    if constants.USER_ACCESS in token.realm_access.roles:
        raise credentials_exception

    return token

def admin_authorization(token: TokenData = Depends(role_authorization)):
    if constants.ADMIN_ACCESS in token.realm_access.roles:
        raise credentials_exception



def get_api_key(x_api_key: str = Header(...)):
    return x_api_key


def api_key_authorization(api_key: str = Depends(get_api_key)):
    if api_key != constants.API_KEY:
        raise credentials_exception
    


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session