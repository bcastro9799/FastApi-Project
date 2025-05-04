import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.bookmarks import Bookmark
from models.user import User
from schemas.bookmark import BookmarkCreate, BookmarkUpdate
from schemas.token_data import TokenData

# Configura el logger
logger = logging.getLogger("bookmarks")
logging.basicConfig(level=logging.INFO)


class CrudBookMark:
    @staticmethod
    async def get_by_id(db: AsyncSession, bookmark_id: int):
        result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
        bookmark = result.scalar_one_or_none()
        logger.info(f"Fetched bookmark by id={bookmark_id}: {bookmark}")
        return bookmark

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 10):
        result = await db.execute(select(Bookmark).offset(skip).limit(limit))
        logger.info(f"Fetched bookmarks")
        return result.scalars().all()

    @staticmethod
    async def get_by_user(
        db: AsyncSession, token_data: TokenData, skip: int = 0, limit: int = 10
    ):
        result = await db.execute(
            select(Bookmark)
            .join(User, User.id == Bookmark.user_id)
            .where(User.username == token_data.username)
            .offset(skip)
            .limit(limit)
        )
        bookmarks = result.scalars().all()
        logger.info(
            f"Fetched {len(bookmarks)} bookmarks for username={token_data.username} (skip={skip}, limit={limit})"
        )
        return bookmarks

    @staticmethod
    async def get_by_url(db: AsyncSession, url: str):
        result = await db.execute(select(Bookmark).where(Bookmark.url.ilike(f"{url}")))
        bookmark = result.scalar_one_or_none()
        logger.info(f"Fetched bookmark by url={url}: {bookmark}")
        return bookmark

    @staticmethod
    async def create(db: AsyncSession, bookmark_data: BookmarkCreate):

        bookmark = Bookmark(**bookmark_data.model_dump())
        db.add(bookmark)
        await db.commit()
        await db.refresh(bookmark)
        logger.info(f"Created bookmark id={bookmark.id} for user_id={bookmark.user_id}")
        return bookmark

    @staticmethod
    async def update(
        db: AsyncSession, bookmark_id: int, bookmark_data: BookmarkUpdate, user_id: int
    ):
        result = await db.execute(
            select(Bookmark).where(
                Bookmark.id == bookmark_id, Bookmark.user_id == user_id
            )
        )
        bookmark = result.scalar_one_or_none()
        if not bookmark:
            logger.warning(
                f"Attempted update: Bookmark id={bookmark_id} not found or not owned by user_id={user_id}"
            )
            return None

        data = bookmark_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            if key != "id":
                setattr(bookmark, key, value)
        await db.commit()
        await db.refresh(bookmark)
        logger.info(f"Updated bookmark id={bookmark.id} for user_id={user_id}")
        return bookmark

    @staticmethod
    async def update_as_admin(
        db: AsyncSession, bookmark_id: int, bookmark_data: BookmarkUpdate
    ):
        result = await db.execute(
            select(Bookmark).where(Bookmark.id == bookmark_id)
        )
        bookmark = result.scalar_one_or_none()
        if not bookmark:
            logger.warning(
                f"Admin attempted update: Bookmark id={bookmark_id} not found"
            )
            return None

        data = bookmark_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            if key != "id":
                setattr(bookmark, key, value)
        await db.commit()
        await db.refresh(bookmark)
        logger.info(f"Admin updated bookmark id={bookmark.id}")
        return bookmark
    
    @staticmethod
    async def delete(db: AsyncSession, bookmark_id: int, user_id: int):
        result = await db.execute(
            select(Bookmark).where(
                Bookmark.id == bookmark_id, Bookmark.user_id == user_id
            )
        )
        bookmark = result.scalar_one_or_none()
        if not bookmark:
            logger.warning(
                f"Attempted delete: Bookmark id={bookmark_id} not found or not owned by user_id={user_id}"
            )
            return False
        await db.delete(bookmark)
        await db.commit()
        logger.info(f"Deleted bookmark id={bookmark_id} for user_id={user_id}")
        return True

    @staticmethod
    async def delete_as_admin(db: AsyncSession, bookmark_id: int):
        result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
        bookmark = result.scalar_one_or_none()
        if not bookmark:
            logger.warning(f"Admin attempted delete: Bookmark id={bookmark_id} not found")
            return False
        await db.delete(bookmark)
        await db.commit()
        logger.info(f"Deleted bookmark id={bookmark_id} ")
        return True
