"""Tests for the authentication service module"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

# Set SECRET_KEY before importing auth_service to ensure consistent token encoding/decoding
import os
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'

from app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    authenticate_user,
)
from app.models.database import User
from app.models.schemas import TokenData
from app.config.settings import settings


class TestPasswordHashing:
    """Test suite for password hashing functions"""

    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_get_password_hash_different_hashes(self):
        """Test that same password produces different hashes"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Bcrypt includes salt, so hashes should be different
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_get_password_hash_length(self):
        """Test that hash has appropriate length"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert len(hashed) > 0
        assert isinstance(hashed, str)


class TestTokenCreation:
    """Test suite for JWT token creation"""

    def test_create_access_token_returns_string(self):
        """Test that access token is a string"""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": 1, "email": "test@example.com"}
        expires_delta = timedelta(hours=2)
        
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert isinstance(token, str)

    def test_create_refresh_token_returns_string(self):
        """Test that refresh token is a string"""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_data(self):
        """Test that token contains the provided data"""
        user_id = 123
        email = "test@example.com"
        data = {"sub": user_id, "email": email}
        
        token = create_access_token(data)
        
        # Decode to verify content
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded.user_id == user_id
        assert decoded.email == email


class TestTokenDecoding:
    """Test suite for JWT token decoding"""

    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        data = {"sub": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert isinstance(decoded, TokenData)
        assert decoded.user_id == 1
        assert decoded.email == "test@example.com"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token"""
        invalid_token = "invalid.token.here"
        
        decoded = decode_token(invalid_token)
        
        assert decoded is None

    def test_decode_expired_token(self):
        """Test decoding an expired token"""
        data = {"sub": 1, "email": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        
        token = create_access_token(data, expires_delta=expires_delta)
        
        decoded = decode_token(token)
        
        assert decoded is None

    def test_decode_token_missing_user_id(self):
        """Test decoding token without user_id"""
        with patch('app.services.auth_service.jwt.encode') as mock_encode:
            # Mock a token with missing sub
            mock_encode.return_value = "mocked.token"
            
            with patch('app.services.auth_service.jwt.decode') as mock_decode:
                mock_decode.return_value = {"email": "test@example.com"}
                
                decoded = decode_token("mocked.token")
                
                assert decoded is None

    def test_decode_token_missing_email(self):
        """Test decoding token without email"""
        with patch('app.services.auth_service.jwt.encode') as mock_encode:
            mock_encode.return_value = "mocked.token"
            
            with patch('app.services.auth_service.jwt.decode') as mock_decode:
                mock_decode.return_value = {"sub": 1}
                
                decoded = decode_token("mocked.token")
                
                assert decoded is None


class TestGetCurrentUser:
    """Test suite for get_current_user function"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        db = Mock(spec=Session)
        return db

    @pytest.fixture
    def mock_user(self):
        """Create a mock active user"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, mock_db, mock_user):
        """Test getting current user with valid token"""
        # Create a valid token
        token_str = create_access_token({"sub": 1, "email": "test@example.com"})
        
        # Setup mock to return user
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        with patch('app.services.auth_service.oauth2_scheme', return_value=token_str):
            user = await get_current_user(token=token_str, db=mock_db)
            
            assert user is not None
            assert user.id == 1

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_db):
        """Test getting current user with invalid token"""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid.token", db=mock_db)
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self, mock_db):
        """Test getting current user when account is deactivated"""
        from fastapi import HTTPException
        
        # Create inactive user mock
        inactive_user = Mock(spec=User)
        inactive_user.id = 1
        inactive_user.email = "test@example.com"
        inactive_user.is_active = False
        
        token_str = create_access_token({"sub": 1, "email": "test@example.com"})
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = inactive_user
        mock_db.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token_str, db=mock_db)
        
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, mock_db):
        """Test getting current user when user doesn't exist"""
        from fastapi import HTTPException
        
        token_str = create_access_token({"sub": 999, "email": "nonexistent@example.com"})
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token_str, db=mock_db)
        
        assert exc_info.value.status_code == 401


class TestAuthenticateUser:
    """Test suite for authenticate_user function"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        db = Mock(spec=Session)
        return db

    @pytest.fixture
    def mock_user(self):
        """Create a mock user with hashed password"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.password_hash = get_password_hash("correctpassword")
        user.is_active = True
        return user

    def test_authenticate_user_success(self, mock_db, mock_user):
        """Test successful authentication"""
        # Setup mock to return user
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        authenticated = authenticate_user(mock_db, "test@example.com", "correctpassword")
        
        assert authenticated is not None
        assert authenticated.id == 1

    def test_authenticate_user_wrong_password(self, mock_db, mock_user):
        """Test authentication with wrong password"""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        authenticated = authenticate_user(mock_db, "test@example.com", "wrongpassword")
        
        assert authenticated is None

    def test_authenticate_user_not_found(self, mock_db):
        """Test authentication when user doesn't exist"""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        authenticated = authenticate_user(mock_db, "nonexistent@example.com", "password")
        
        assert authenticated is None
