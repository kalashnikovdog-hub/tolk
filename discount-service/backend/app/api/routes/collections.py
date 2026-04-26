"""Collections endpoints"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.schemas import CollectionResponse, CollectionCreate, CollectionUpdate
from app.models.database import Collection, User
from app.services.auth_service import get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter()


@router.get("/", response_model=List[CollectionResponse])
async def get_collections(
    user_id: Optional[int] = None,
    is_public: bool = True,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get list of collections"""
    query = db.query(Collection).filter(Collection.is_public == is_public)
    
    if user_id:
        query = query.filter(Collection.owner_id == user_id)
    
    # If not authenticated, only show public collections
    if not current_user and not is_public:
        raise ForbiddenException("Authentication required")
    
    collections = query.limit(limit).all()
    return collections


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get collection by ID"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise NotFoundException("Collection", collection_id)
    
    # Check access
    if not collection.is_public and (not current_user or current_user.id != collection.owner_id):
        raise ForbiddenException("Access denied")
    
    return collection


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new collection"""
    new_collection = Collection(
        **collection_data.model_dump(exclude={'discount_ids'}),
        owner_id=current_user.id
    )
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    return new_collection


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update collection (owner only)"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise NotFoundException("Collection", collection_id)
    
    # Check ownership
    if collection.owner_id != current_user.id:
        raise ForbiddenException("Access denied")
    
    update_data = collection_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collection, field, value)
    
    db.commit()
    db.refresh(collection)
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete collection (owner only)"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise NotFoundException("Collection", collection_id)
    
    # Check ownership
    if collection.owner_id != current_user.id:
        raise ForbiddenException("Access denied")
    
    db.delete(collection)
    db.commit()
    return None
