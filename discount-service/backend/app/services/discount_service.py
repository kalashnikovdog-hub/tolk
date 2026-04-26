from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_, or_

from app.models.database import Discount, Category, Store, User, UserPreference, SubscriptionTier
from app.models.schemas import DiscountFilter, DiscountTypeEnum


class DiscountService:
    """Service for managing discounts"""
    
    @staticmethod
    def get_discounts(
        db: Session,
        filters: DiscountFilter,
        user: Optional[User] = None
    ) -> Tuple[List[Discount], int]:
        """Get filtered list of discounts"""
        
        query = select(Discount).where(Discount.is_active == True)
        count_query = select(func.count()).select_from(Discount).where(Discount.is_active == True)
        
        # Apply filters
        if filters.category_id:
            query = query.where(Discount.category_id == filters.category_id)
            count_query = count_query.where(Discount.category_id == filters.category_id)
        
        if filters.store_id:
            query = query.where(Discount.store_id == filters.store_id)
            count_query = count_query.where(Discount.store_id == filters.store_id)
        
        if filters.discount_type:
            query = query.where(Discount.discount_type == filters.discount_type)
            count_query = count_query.where(Discount.discount_type == filters.discount_type)
        
        if filters.min_discount_value is not None:
            query = query.where(Discount.discount_value >= filters.min_discount_value)
            count_query = count_query.where(Discount.discount_value >= filters.min_discount_value)
        
        if filters.max_discount_value is not None:
            query = query.where(Discount.discount_value <= filters.max_discount_value)
            count_query = count_query.where(Discount.discount_value <= filters.max_discount_value)
        
        if filters.is_personal is not None:
            query = query.where(Discount.is_personal == filters.is_personal)
            count_query = count_query.where(Discount.is_personal == filters.is_personal)
        
        if filters.is_exclusive is not None:
            # Only show exclusive discounts to premium/family users
            if filters.is_exclusive and user:
                if user.subscription_tier in [SubscriptionTier.FREE]:
                    query = query.where(Discount.id == -1)  # No results
            query = query.where(Discount.is_exclusive == filters.is_exclusive)
            count_query = count_query.where(Discount.is_exclusive == filters.is_exclusive)
        
        if filters.is_bank_offer is not None:
            query = query.where(Discount.is_bank_offer == filters.is_bank_offer)
            count_query = count_query.where(Discount.is_bank_offer == filters.is_bank_offer)
        
        if filters.search_query:
            search_filter = or_(
                Discount.title.ilike(f"%{filters.search_query}%"),
                Discount.description.ilike(f"%{filters.search_query}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Filter by date (only active discounts)
        now = datetime.utcnow()
        query = query.where(
            or_(
                Discount.end_date == None,
                Discount.end_date > now
            )
        )
        count_query = count_query.where(
            or_(
                Discount.end_date == None,
                Discount.end_date > now
            )
        )
        
        # Sorting
        sort_column = getattr(Discount, filters.sort_by, Discount.created_at)
        if filters.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        
        # Load relationships
        query = query.options(
            joinedload(Discount.store),
            joinedload(Discount.category)
        )
        
        discounts = db.execute(query).scalars().all()
        total = db.execute(count_query).scalar()
        
        return list(discounts), total
    
    @staticmethod
    def get_personal_discounts(db: Session, user: User, limit: int = 20) -> List[Discount]:
        """Get personalized discounts based on user preferences"""
        
        # Get user preferences
        preferences = db.execute(
            select(UserPreference).where(UserPreference.user_id == user.id)
        ).scalars().all()
        
        if not preferences:
            # Return popular discounts if no preferences
            return DiscountService.get_popular_discounts(db, limit=limit)
        
        category_ids = [p.category_id for p in preferences if p.category_id]
        store_ids = [p.store_id for p in preferences if p.store_id]
        
        query = select(Discount).where(
            Discount.is_active == True,
            or_(
                Discount.category_id.in_(category_ids) if category_ids else False,
                Discount.store_id.in_(store_ids) if store_ids else False,
            )
        )
        
        # Filter by date
        now = datetime.utcnow()
        query = query.where(
            or_(
                Discount.end_date == None,
                Discount.end_date > now
            )
        )
        
        query = query.order_by(Discount.created_at.desc()).limit(limit)
        query = query.options(
            joinedload(Discount.store),
            joinedload(Discount.category)
        )
        
        discounts = db.execute(query).scalars().all()
        return list(discounts)
    
    @staticmethod
    def get_popular_discounts(db: Session, limit: int = 20) -> List[Discount]:
        """Get most popular discounts"""
        query = select(Discount).where(
            Discount.is_active == True,
            Discount.is_verified == True
        )
        
        # Filter by date
        now = datetime.utcnow()
        query = query.where(
            or_(
                Discount.end_date == None,
                Discount.end_date > now
            )
        )
        
        query = query.order_by(Discount.views_count.desc(), Discount.clicks_count.desc())
        query = query.limit(limit)
        query = query.options(
            joinedload(Discount.store),
            joinedload(Discount.category)
        )
        
        discounts = db.execute(query).scalars().all()
        return list(discounts)
    
    @staticmethod
    def get_bank_offers(db: Session, month: Optional[int] = None, year: Optional[int] = None) -> List[Discount]:
        """Get special bank offers for the current month"""
        now = datetime.utcnow()
        
        if month is None:
            month = now.month
        if year is None:
            year = now.year
        
        # First day and last day of the month
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_of_month = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        query = select(Discount).where(
            Discount.is_active == True,
            Discount.is_bank_offer == True,
            Discount.start_date <= end_of_month,
            Discount.end_date >= start_of_month
        )
        
        query = query.options(
            joinedload(Discount.store),
            joinedload(Discount.category)
        )
        
        discounts = db.execute(query).scalars().all()
        return list(discounts)
    
    @staticmethod
    def get_store_catalog(db: Session, store_id: int) -> List[Discount]:
        """Get all discounts for a store (digital catalog)"""
        query = select(Discount).where(
            Discount.is_active == True,
            Discount.store_id == store_id
        )
        
        # Filter by date
        now = datetime.utcnow()
        query = query.where(
            or_(
                Discount.end_date == None,
                Discount.end_date > now
            )
        )
        
        query = query.order_by(Discount.discount_value.desc())
        query = query.options(
            joinedload(Discount.category)
        )
        
        discounts = db.execute(query).scalars().all()
        return list(discounts)
    
    @staticmethod
    def increment_view(db: Session, discount_id: int):
        """Increment view count for a discount"""
        discount = db.get(Discount, discount_id)
        if discount:
            discount.views_count += 1
            db.commit()
    
    @staticmethod
    def increment_click(db: Session, discount_id: int):
        """Increment click count for a discount"""
        discount = db.get(Discount, discount_id)
        if discount:
            discount.clicks_count += 1
            db.commit()
