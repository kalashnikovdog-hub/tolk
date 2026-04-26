"""
Integration tests for the Discount Service API
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config.database import get_db, Base
from app.models.database import User, Store, Category, Discount
from app.services.auth_service import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def client(test_db):
    """Create async test client"""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create test user"""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_store(test_db):
    """Create test store"""
    db = TestingSessionLocal()
    store = Store(
        name="Test Store",
        description="Test Description",
        store_type="grocery",
        is_active=True
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    db.close()
    return store


@pytest.fixture
def test_category(test_db):
    """Create test category"""
    db = TestingSessionLocal()
    category = Category(
        name="Test Category",
        slug="test-category",
        is_active=True
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    db.close()
    return category


@pytest.fixture
def test_discount(test_db, test_store, test_category):
    """Create test discount"""
    db = TestingSessionLocal()
    discount = Discount(
        title="Test Discount",
        description="Test Description",
        discount_type="percentage",
        discount_value=20.0,
        store_id=test_store.id,
        category_id=test_category.id,
        is_active=True,
        is_verified=True
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)
    db.close()
    return discount


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test basic health check"""
        response = await client.get("/api/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client):
        """Test user registration"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "newpassword123",
                "full_name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
        """Test registering with duplicate email"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "anotherpassword123"
            }
        )
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """Test successful login"""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401


class TestDiscountEndpoints:
    """Test discount endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_discounts(self, client, test_discount):
        """Test getting list of discounts"""
        response = await client.get("/api/discounts/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_discount_by_id(self, client, test_discount):
        """Test getting single discount"""
        response = await client.get(f"/api/discounts/{test_discount.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_discount.id
        assert data["title"] == "Test Discount"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_discount(self, client):
        """Test getting nonexistent discount"""
        response = await client.get("/api/discounts/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_popular_discounts(self, client, test_discount):
        """Test getting popular discounts"""
        response = await client.get("/api/discounts/popular")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_increment_view(self, client, test_discount):
        """Test incrementing view count"""
        response = await client.post(f"/api/discounts/{test_discount.id}/view")
        assert response.status_code == 200


class TestStoreEndpoints:
    """Test store endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_stores(self, client, test_store):
        """Test getting list of stores"""
        response = await client.get("/api/stores/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_store_by_id(self, client, test_store):
        """Test getting single store"""
        response = await client.get(f"/api/stores/{test_store.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_store.id
        assert data["name"] == "Test Store"


class TestCategoryEndpoints:
    """Test category endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_categories(self, client, test_category):
        """Test getting list of categories"""
        response = await client.get("/api/categories/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestValidation:
    """Test input validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_email_registration(self, client):
        """Test registration with invalid email"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_short_password_registration(self, client):
        """Test registration with short password"""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_pagination(self, client):
        """Test invalid pagination parameters"""
        response = await client.get("/api/discounts/?page=0&page_size=-1")
        assert response.status_code == 422
