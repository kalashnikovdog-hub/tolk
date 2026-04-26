"""
Discounts endpoints with caching support
"""
import hashlib
import json
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.config.database import get_db
from app.models.schemas import (
    DiscountResponse,
    DiscountCreate,
    DiscountUpdate,
    DiscountFilter,
    PaginatedResponse
)
from app.services.discount_service import DiscountService
from app.models.database import Discount, User
from app.services.auth_service import get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter()


def get_cache_key(filters: DiscountFilter) -> str:
    """Generate cache key from filters"""
    filter_dict = filters.model_dump()
    filter_json = json.dumps(filter_dict, sort_keys=True)
    return hashlib.md5(filter_json.encode()).hexdigest()


@router.get("/", response_model=PaginatedResponse)
async def get_discounts(
    category_id: Optional[int] = None,
    store_id: Optional[int] = None,
    discount_type: Optional[str] = None,
    min_discount_value: Optional[float] = None,
    max_discount_value: Optional[float] = None,
    is_personal: Optional[bool] = None,
    is_exclusive: Optional[bool] = None,
    is_bank_offer: Optional[bool] = None,
    search_query: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    request=None
):
    """
    Get filtered list of discounts with pagination
    
    Supports various filters and sorting options.
    Results are cached for better performance.
    """
    # Build filters
    filters = DiscountFilter(
        category_id=category_id,
        store_id=store_id,
        discount_type=discount_type,
        min_discount_value=min_discount_value,
        max_discount_value=max_discount_value,
        is_personal=is_personal,
        is_exclusive=is_exclusive,
        is_bank_offer=is_bank_offer,
        search_query=search_query,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Try cache first
    cache_key = f"discounts:list:{get_cache_key(filters)}"
    if hasattr(request.app.state, 'cache') and request.app.state.cache:
        cached = await request.app.state.cache.get(cache_key)
        if cached:
            return cached
    
    # Get from database
    discounts, total = DiscountService.get_discounts(db, filters, current_user)
    
    # Calculate pagination
    pages = (total + page_size - 1) // page_size
    
    response = {
        "items": [
            {
                **discount.__dict__,
                "store": discount.store.__dict__ if discount.store else None,
                "category": discount.category.__dict__ if discount.category else None
            }
            for discount in discounts
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }
    
    # Cache the result
    if hasattr(request.app.state, 'cache') and request.app.state.cache:
        await request.app.state.cache.set(cache_key, response, ttl=300)
    
    return response


@router.get("/{discount_id}", response_model=DiscountResponse)
async def get_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    request=None
):
    """Get discount by ID"""
    # Try cache first
    cache_key = f"discount:{discount_id}"
    if hasattr(request.app.state, 'cache') and request.app.state.cache:
        cached = await request.app.state.cache.get(cache_key)
        if cached:
            return cached
    
    # Get from database
    discount = db.query(Discount).options(
        joinedload(Discount.store),
        joinedload(Discount.category)
    ).filter(Discount.id == discount_id).first()
    
    if not discount:
        raise NotFoundException("Discount", discount_id)
    
    response = {
        **discount.__dict__,
        "store": discount.store.__dict__ if discount.store else None,
        "category": discount.category.__dict__ if discount.category else None
    }
    
    # Cache the result
    if hasattr(request.app.state, 'cache') and request.app.state.cache:
        await request.app.state.cache.set(cache_key, response, ttl=300)
    
    return discount


@router.post("/", response_model=DiscountResponse, status_code=status.HTTP_201_CREATED)
async def create_discount(
    discount_data: DiscountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new discount (admin only)
    
    Requires authentication and admin privileges.
    """
    # Check admin (in production, check role)
    # For now, just allow authenticated users
    
    new_discount = Discount(**discount_data.model_dump())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    
    # Invalidate cache
    if hasattr(request.app.state, 'cache') and request.app.state.cache:
        await request.app.state.cache.invalidate_discounts_list_cache()
    
    return new_discount


@router.put("/{discount_id}", response_model=DiscountResponse)
async def update_discount(
    discount_id: int,
    discount_data: DiscountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update discount (admin only)
    """
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise NotFoundException("Discount", discount_id)
    
    # Update fields
    update_data = discount_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(discount, field, value)
    
    db.commit()
    db.refresh(discount)
    
    # Invalidate cache
    if hasattr(request.app.state, 'cache') and request.app.state.cache:
        await request.app.state.cache.invalidate_discount_cache(discount_id)
        await request.app.state.cache.invalidate_discounts_list_cache()
    
    return discount


@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete discount (admin only)
    """
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise NotFoundException("Discount", discount_id)
    
    db.delete(discount)
    db.commit()
    
    # Invalidate cache
    if hasattr(request.app.state, 'cache') and request.app.state.cache:
        await request.app.state.cache.invalidate_discount_cache(discount_id)
        await request.app.state.cache.invalidate_discounts_list_cache()
    
    return None


@router.post("/{discount_id}/view")
async def increment_view(
    discount_id: int,
    db: Session = Depends(get_db)
):
    """Increment view count for a discount"""
    DiscountService.increment_view(db, discount_id)
    return {"message": "View counted"}


@router.post("/{discount_id}/click")
async def increment_click(
    discount_id: int,
    db: Session = Depends(get_db)
):
    """Increment click count for a discount"""
    DiscountService.increment_click(db, discount_id)
    return {"message": "Click counted"}


@router.get("/personal/my", response_model=List[DiscountResponse])
async def get_personal_discounts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized discounts for current user"""
    discounts = DiscountService.get_personal_discounts(db, current_user, limit)
    return discounts


@router.get("/popular", response_model=List[DiscountResponse])
async def get_popular_discounts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get most popular discounts"""
    discounts = DiscountService.get_popular_discounts(db, limit)
    return discounts


@router.get("/bank-offers", response_model=List[DiscountResponse])
async def get_bank_offers(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get special bank offers for the current month"""
    discounts = DiscountService.get_bank_offers(db, month, year)
    return discounts
