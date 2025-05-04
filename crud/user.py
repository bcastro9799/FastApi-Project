import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import User
from schemas.user import UserCreate, UserUpdate

# Configura el logger
logger = logging.getLogger("users")
logging.basicConfig(level=logging.INFO)


class CrudUser:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 10):
        result = await db.execute(select(User).options(selectinload(User.bookmarks)).offset(skip).limit(limit))
        users = result.scalars().all()
        logger.info(f"Fetched {len(users)} users (skip={skip}, limit={limit})")
        return users

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int):
        result = await db.execute(select(User).options(selectinload(User.bookmarks)).where(User.id == user_id))
        user = result.scalar_one_or_none()
        logger.info(f"Fetched user by id={user_id}: {user}")
        return user

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str):
        result = await db.execute(select(User).options(selectinload(User.bookmarks)).where(User.username == username))
        user = result.scalar_one_or_none()
        logger.info(f"Fetched user by username={username}: {user}")
        return user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).options(selectinload(User.bookmarks)).where(User.email == email))
        user = result.scalar_one_or_none()
        logger.info(f"Fetched user by email={email}: {user}")
        return user

    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate):
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created user id={user.id}")
        return user
    
    @staticmethod
    async def update(db:AsyncSession, user_data: UserUpdate):
        result = await db.execute(select(User).where(User.id == user_data.id))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"Attempted update: User id={user_data.id} not found")
            return None

        data = user_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            if key != "id":
                setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Updated user id={user.id}")
        return user
    
    @staticmethod
    async def delete(db:AsyncSession, user_id:int):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"Attempted delete: User id={user_id} not found")
            return False
        await db.delete(user)
        await db.commit()
        logger.info(f"Deleted user id={user_id}")
        return True