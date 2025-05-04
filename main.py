from fastapi.security import OAuth2PasswordRequestForm
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from constants import URL_PREFIX
from db.database import Base,engine
from dependencies import authorization,keycloak_openid
from runtimeConstants import SERVER_IP, SERVER_PORT
from schemas.token_data import TokenData
from models.user import User
from models.bookmarks import Bookmark
from api import bookmark,users



app = FastAPI(
    docs_url=f"{URL_PREFIX}/docs",
    redoc_url=f"{URL_PREFIX}/redoc",
    openapi_url=f"{URL_PREFIX}/openapi.json",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix_router = APIRouter(prefix="/api")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/token",include_in_schema=False)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = keycloak_openid.token(form_data.username, form_data.password)
        return {
            "access_token": token["access_token"],
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

@prefix_router.get("/")
def root_route(user:TokenData = Depends(authorization)):
    return "Welcome to Library API"


prefix_router.include_router(bookmark.router)
prefix_router.include_router(users.router)

app.include_router(prefix_router)


if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_IP,port=SERVER_PORT)