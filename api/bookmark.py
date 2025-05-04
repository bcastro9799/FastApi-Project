from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import constants
from crud.bookmark import CrudBookMark
from crud.user import CrudUser
from dependencies import authorization, get_db
from schemas.bookmark import BookmarkCreate, BookmarkRead, BookmarkUpdate
from schemas.token_data import TokenData

router = APIRouter(prefix="/bookmark")


@router.get("/list/", response_model=List[BookmarkRead])
async def list_bookmarks(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(authorization),
):
    """
    Retrieve a paginated list of bookmarks.

    - If the authenticated user has the admin role, all bookmarks in the system are returned.
    - If the user has the user role, only their own bookmarks are returned.
    - If the user has neither role, a 403 Forbidden error is returned.
    """

    async def get_all_bookmarks(db, skip, limit, token_data):
        return await CrudBookMark.get_all(db, skip=skip, limit=limit)

    async def get_user_bookmarks(db, skip, limit, token_data):
        return await CrudBookMark.get_by_user(db, token_data, skip=skip, limit=limit)

    ROLE_QUERY_MAP = {
        constants.ADMIN_ROLE: get_all_bookmarks,
        constants.USER_ROLE: get_user_bookmarks,
    }
    try:
        roles = token_data.realm_access.roles
        for role in roles:
            if role in ROLE_QUERY_MAP:
                return await ROLE_QUERY_MAP[role](db, skip, limit, token_data)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view bookmarks.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.post("/", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(authorization),
):
    """
    Create a new bookmark.

    - Admins can create bookmarks for any user by specifying `user_id` in the request body.
    - Regular users can only create bookmarks for themselves; any `user_id` in the request will be ignored.
    """
    roles = token_data.realm_access.roles

    if constants.ADMIN_ROLE in roles:
        if not bookmark.user_id:
            raise HTTPException(
                status_code=400, detail="user_id must be provided by admin"
            )
    else:
        target_user = await CrudUser.get_by_username(
            db=db, username=token_data.username
        )
        if not target_user:
            raise HTTPException(status_code=400, detail="No user in the database")
        bookmark.user_id = target_user.id

    new_bookmark = await CrudBookMark.create(db, bookmark)
    return new_bookmark


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: int = Query(..., description="ID of the bookmark to delete"),
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(authorization),
):
    """
    Delete a bookmark by its ID.

    - Admins can delete any bookmark.
    - Regular users can only delete their own bookmarks.
    """
    roles = token_data.realm_access.roles

    if constants.ADMIN_ROLE in roles:
        deleted = await CrudBookMark.delete_as_admin(db, bookmark_id)
    else:
        target_user = await CrudUser.get_by_username(
            db=db, username=token_data.username
        )
        if not target_user:
            raise HTTPException(status_code=400, detail="No user in the database")
        deleted = await CrudBookMark.delete(db, bookmark_id, target_user.id)

    if not deleted:
        raise HTTPException(
            status_code=404, detail="Bookmark not found or not authorized to delete"
        )
    return None


@router.patch("/", response_model=BookmarkRead)
async def update_bookmark(
    bookmark: BookmarkUpdate,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(authorization),
):
    """
    Update a bookmark.

    - Admins can update any bookmark.
    - Regular users can only update their own bookmarks.
    """
    roles = token_data.realm_access.roles

    if constants.ADMIN_ROLE in roles:
        updated = await CrudBookMark.update_as_admin(db, bookmark.id, bookmark)
    else:
        target_user = await CrudUser.get_by_username(
            db=db, username=token_data.username
        )
        if not target_user:
            raise HTTPException(status_code=400, detail="No user in the database")
        updated = await CrudBookMark.update(db, bookmark.id, bookmark, target_user.id)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found or not authorized to update",
        )
    return updated
