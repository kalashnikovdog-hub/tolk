"""Stores endpoints"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.schemas import StoreResponse, StoreCreate, StoreUpdate
from app.models.database import Store
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/", response_model=List[StoreResponse])
async def get_stores(
    store_type: Optional[str] = None,
    is_active: bool = True,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get list of stores with optional filtering"""
    query = db.query(Store).filter(Store.is_active == is_active)
    
    if store_type:
        query = query.filter(Store.store_type == store_type)
    
    stores = query.limit(limit).all()
    return stores


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Get store by ID"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise NotFoundException("Store", store_id)
    return store


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
async def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db)
):
    """Create a new store (admin only)"""
    new_store = Store(**store_data.model_dump())
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: int,
    store_data: StoreUpdate,
    db: Session = Depends(get_db)
):
    """Update store (admin only)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise NotFoundException("Store", store_id)
    
    update_data = store_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Delete store (admin only)"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise NotFoundException("Store", store_id)
    
    db.delete(store)
    db.commit()
    return None


@router.get("/{store_id}/catalog", response_model=List)
async def get_store_catalog(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Get all discounts for a store (digital catalog)"""
    from app.services.discount_service import DiscountService
    
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise NotFoundException("Store", store_id)
    
    discounts = DiscountService.get_store_catalog(db, store_id)
    return discounts
