"""
Admin endpoints for managing discounts and daemon
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.config.database import get_db
from app.models.schemas import (
    DiscountResponse,
    DiscountCreate,
    DiscountUpdate,
    PaginatedResponse,
    APIResponse
)
from app.models.database import Discount, Store, Category, User, ScrapedSource
from app.services.auth_service import get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter()


def check_admin_access(current_user: User):
    """Check if user has admin privileges"""
    # In production, check user role from database
    # For now, check if email contains 'admin' or use a simple flag
    admin_emails = ["admin@tolk.ru", "admin@example.com"]
    if current_user.email not in admin_emails and not current_user.is_verified:
        raise ForbiddenException("Admin access required")
    return True


# ============== Discount Management ==============

@router.get("/discounts", response_model=PaginatedResponse)
async def admin_get_discounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    store_id: Optional[int] = None,
    category_id: Optional[int] = None,
    search_query: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Get all discounts with advanced filtering
    
    - Requires admin privileges
    - Can filter by verification status, active status, etc.
    """
    check_admin_access(current_user)
    
    query = db.query(Discount)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Discount.is_active == is_active)
    
    if is_verified is not None:
        query = query.filter(Discount.is_verified == is_verified)
    
    if store_id is not None:
        query = query.filter(Discount.store_id == store_id)
    
    if category_id is not None:
        query = query.filter(Discount.category_id == category_id)
    
    if search_query:
        query = query.filter(
            (Discount.title.ilike(f"%{search_query}%")) |
            (Discount.description.ilike(f"%{search_query}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    discounts = query.order_by(Discount.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Calculate pages
    pages = (total + page_size - 1) // page_size
    
    return {
        "items": discounts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.get("/discounts/{discount_id}", response_model=DiscountResponse)
async def admin_get_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Get discount by ID with full details
    """
    check_admin_access(current_user)
    
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise NotFoundException("Discount", discount_id)
    
    return discount


@router.post("/discounts", response_model=DiscountResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_discount(
    discount_data: DiscountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Create a new discount manually
    """
    check_admin_access(current_user)
    
    # Validate store exists
    store = db.query(Store).filter(Store.id == discount_data.store_id).first()
    if not store:
        raise NotFoundException("Store", discount_data.store_id)
    
    # Validate category if provided
    if discount_data.category_id:
        category = db.query(Category).filter(Category.id == discount_data.category_id).first()
        if not category:
            raise NotFoundException("Category", discount_data.category_id)
    
    new_discount = Discount(**discount_data.model_dump())
    new_discount.is_verified = True  # Admin-created discounts are verified
    
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    
    return new_discount


@router.put("/discounts/{discount_id}", response_model=DiscountResponse)
async def admin_update_discount(
    discount_id: int,
    discount_data: DiscountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Update discount
    """
    check_admin_access(current_user)
    
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise NotFoundException("Discount", discount_id)
    
    # Update fields
    update_data = discount_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(discount, field, value)
    
    discount.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(discount)
    
    return discount


@router.delete("/discounts/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Delete discount permanently
    """
    check_admin_access(current_user)
    
    discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not discount:
        raise NotFoundException("Discount", discount_id)
    
    db.delete(discount)
    db.commit()
    
    return None


@router.post("/discounts/bulk-delete", response_model=APIResponse)
async def admin_bulk_delete_discounts(
    discount_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Delete multiple discounts at once
    """
    check_admin_access(current_user)
    
    deleted_count = db.query(Discount).filter(Discount.id.in_(discount_ids)).delete(synchronize_session=False)
    db.commit()
    
    return {
        "success": True,
        "message": f"Successfully deleted {deleted_count} discounts",
        "data": {"deleted_count": deleted_count}
    }


@router.post("/discounts/bulk-verify", response_model=APIResponse)
async def admin_bulk_verify_discounts(
    discount_ids: List[int],
    verified: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Bulk verify/unverify discounts
    """
    check_admin_access(current_user)
    
    updated_count = db.query(Discount).filter(
        Discount.id.in_(discount_ids)
    ).update({Discount.is_verified: verified}, synchronize_session=False)
    db.commit()
    
    return {
        "success": True,
        "message": f"Successfully updated {updated_count} discounts",
        "data": {"updated_count": updated_count}
    }


# ============== Store Management ==============

@router.get("/stores", response_model=List)
async def admin_get_stores(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Get all stores
    """
    check_admin_access(current_user)
    
    query = db.query(Store)
    if is_active is not None:
        query = query.filter(Store.is_active == is_active)
    
    return query.all()


@router.post("/stores", status_code=status.HTTP_201_CREATED)
async def admin_create_store(
    name: str,
    description: Optional[str] = None,
    website_url: Optional[str] = None,
    store_type: str = "other",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Create a new store
    """
    check_admin_access(current_user)
    
    store = Store(
        name=name,
        description=description,
        website_url=website_url,
        store_type=store_type
    )
    
    db.add(store)
    db.commit()
    db.refresh(store)
    
    return store


@router.put("/stores/{store_id}")
async def admin_update_store(
    store_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Update store
    """
    check_admin_access(current_user)
    
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise NotFoundException("Store", store_id)
    
    if name is not None:
        store.name = name
    if description is not None:
        store.description = description
    if is_active is not None:
        store.is_active = is_active
    
    db.commit()
    db.refresh(store)
    
    return store


@router.delete("/stores/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Delete store
    """
    check_admin_access(current_user)
    
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise NotFoundException("Store", store_id)
    
    db.delete(store)
    db.commit()
    
    return None


# ============== Daemon Control ==============

@router.get("/daemon/status", response_model=APIResponse)
async def get_daemon_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Get daemon status and statistics
    """
    check_admin_access(current_user)
    
    # Get statistics
    total_discounts = db.query(Discount).count()
    active_discounts = db.query(Discount).filter(Discount.is_active == True).count()
    verified_discounts = db.query(Discount).filter(Discount.is_verified == True).count()
    total_sources = db.query(ScrapedSource).count()
    active_sources = db.query(ScrapedSource).filter(ScrapedSource.is_active == True).count()
    
    # Get last scrape time
    last_scrape = db.query(ScrapedSource.last_scraped).filter(
        ScrapedSource.last_scraped != None
    ).order_by(ScrapedSource.last_scraped.desc()).first()
    
    return {
        "success": True,
        "data": {
            "is_running": True,  # In production, check actual daemon status
            "total_discounts": total_discounts,
            "active_discounts": active_discounts,
            "verified_discounts": verified_discounts,
            "total_sources": total_sources,
            "active_sources": active_sources,
            "last_scrape": last_scrape[0] if last_scrape else None
        }
    }


@router.post("/daemon/start", response_model=APIResponse)
async def start_daemon(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Start the discount scraper daemon
    """
    check_admin_access(current_user)
    
    # In production, this would start the actual daemon process
    # For now, just return success
    return {
        "success": True,
        "message": "Daemon started successfully"
    }


@router.post("/daemon/stop", response_model=APIResponse)
async def stop_daemon(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Stop the discount scraper daemon
    """
    check_admin_access(current_user)
    
    # In production, this would stop the actual daemon process
    return {
        "success": True,
        "message": "Daemon stopped successfully"
    }


@router.post("/daemon/run-now", response_model=APIResponse)
async def run_daemon_now(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Trigger immediate daemon run
    """
    check_admin_access(current_user)
    
    # In production, this would trigger an immediate scrape
    return {
        "success": True,
        "message": "Daemon run triggered"
    }


@router.get("/daemon/sources", response_model=List)
async def get_scraped_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Get all scraped sources
    """
    check_admin_access(current_user)
    
    return db.query(ScrapedSource).all()


@router.post("/daemon/sources", status_code=status.HTTP_201_CREATED)
async def add_scraped_source(
    name: str,
    url: str,
    source_type: str = "website",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Add new scraped source
    """
    check_admin_access(current_user)
    
    source = ScrapedSource(
        name=name,
        url=url,
        source_type=source_type
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return source


@router.put("/daemon/sources/{source_id}")
async def update_scraped_source(
    source_id: int,
    name: Optional[str] = None,
    url: Optional[str] = None,
    is_active: Optional[bool] = None,
    scrape_frequency: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Update scraped source
    """
    check_admin_access(current_user)
    
    source = db.query(ScrapedSource).filter(ScrapedSource.id == source_id).first()
    if not source:
        raise NotFoundException("ScrapedSource", source_id)
    
    if name is not None:
        source.name = name
    if url is not None:
        source.url = url
    if is_active is not None:
        source.is_active = is_active
    if scrape_frequency is not None:
        source.scrape_frequency = scrape_frequency
    
    db.commit()
    db.refresh(source)
    
    return source


@router.delete("/daemon/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scraped_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Delete scraped source
    """
    check_admin_access(current_user)
    
    source = db.query(ScrapedSource).filter(ScrapedSource.id == source_id).first()
    if not source:
        raise NotFoundException("ScrapedSource", source_id)
    
    db.delete(source)
    db.commit()
    
    return None


# ============== Statistics ==============

@router.get("/statistics/overview", response_model=APIResponse)
async def get_statistics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin: Get overview statistics
    """
    check_admin_access(current_user)
    
    # Total discounts by type
    from sqlalchemy import func
    
    discounts_by_type = db.query(
        Discount.discount_type,
        func.count(Discount.id)
    ).group_by(Discount.discount_type).all()
    
    discounts_by_store = db.query(
        Store.name,
        func.count(Discount.id)
    ).join(Discount).group_by(Store.name).limit(10).all()
    
    recent_discounts = db.query(Discount).order_by(
        Discount.created_at.desc()
    ).limit(10).all()
    
    return {
        "success": True,
        "data": {
            "discounts_by_type": [
                {"type": t, "count": c} for t, c in discounts_by_type
            ],
            "discounts_by_store": [
                {"store": s, "count": c} for s, c in discounts_by_store
            ],
            "recent_discounts": recent_discounts
        }
    }
