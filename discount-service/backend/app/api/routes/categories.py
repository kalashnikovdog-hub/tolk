"""Categories endpoints"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.schemas import CategoryResponse, CategoryCreate
from app.models.database import Category
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    parent_id: Optional[int] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of categories with optional filtering"""
    query = db.query(Category).filter(Category.is_active == is_active)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    else:
        # By default, show only root categories
        query = query.filter(Category.parent_id == None)
    
    categories = query.all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get category by ID with children"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("Category", category_id)
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category (admin only)"""
    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete category (admin only)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("Category", category_id)
    
    db.delete(category)
    db.commit()
    return None
