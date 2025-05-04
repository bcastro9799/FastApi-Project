from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

import constants
from crud.user import CrudUser
from dependencies import authorization, get_db
from schemas.token_data import TokenData
from schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/user", tags=["users"])

def admin_required(token_data: TokenData = Depends(authorization)):
    """
    Dependency to ensure the user has admin role.
    """
    if constants.ADMIN_ROLE not in token_data.realm_access.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return token_data

@router.get("/me", response_model=UserRead)
async def get_my_user(
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(authorization),
):
    """
    Retrieve  user who is logged in.
    """
    return await CrudUser.get_by_username(db, username=token_data.username)


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(admin_required),
):
    """
    Retrieve a paginated list of users. Only accessible by admins.
    """
    return await CrudUser.get_all(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(admin_required),
):
    """
    Retrieve a user by their ID. Only accessible by admins.
    """
    user = await CrudUser.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(admin_required),
):
    """
    Create a new user. Only accessible by admins.
    """
    existing = await CrudUser.get_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    existing = await CrudUser.get_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    return await CrudUser.create(db, user)

@router.patch("/", response_model=UserRead)
async def update_user(
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(admin_required),
):
    """
    Update a user by their ID. Only accessible by admins.
    """
    updated = await CrudUser.update(db, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int = Query(..., description="ID of the user to delete"),
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(admin_required),
):
    """
    Delete a user by their ID. Only accessible by admins.
    """
    deleted = await CrudUser.delete(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None