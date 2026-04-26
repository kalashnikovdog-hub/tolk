"""
Users endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.schemas import UserResponse, UserUpdate
from app.services.auth_service import get_current_user
from app.models.database import User
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user profile
    
    - **full_name**: Optional full name
    - **phone**: Optional phone number
    """
    # Update fields
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.phone is not None:
        current_user.phone = user_data.phone
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID (admin or self only)"""
    # Check permission
    if current_user.id != user_id:
        # In production, check for admin role
        raise ForbiddenException("Access denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User", user_id)
    
    return user
