"""
Tests for the accounts app.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/v1/auth/register/", data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_register_user_password_mismatch(self, api_client):
        """Test registration with mismatched passwords."""
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/v1/auth/register/", data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_duplicate_email(self, api_client, user):
        """Test registration with existing email."""
        data = {
            "email": user.email,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/v1/auth/register/", data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, api_client, user):
        """Test successful login."""
        data = {
            "email": user.email,
            "password": "TestPass123!",
        }
        response = api_client.post("/api/v1/auth/login/", data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_password(self, api_client, user):
        """Test login with wrong password."""
        data = {
            "email": user.email,
            "password": "WrongPassword123!",
        }
        response = api_client.post("/api/v1/auth/login/", data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user."""
        data = {
            "email": "nonexistent@example.com",
            "password": "SomePass123!",
        }
        response = api_client.post("/api/v1/auth/login/", data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Tests for user profile endpoints."""

    def test_get_profile_authenticated(self, authenticated_client, user):
        """Test getting profile when authenticated."""
        response = authenticated_client.get("/api/v1/auth/me/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["email"] == user.email

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile when not authenticated."""
        response = api_client.get("/api/v1/auth/me/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile."""
        data = {"first_name": "Updated"}
        response = authenticated_client.patch("/api/v1/auth/me/", data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        user.refresh_from_db()
        assert user.first_name == "Updated"


@pytest.mark.django_db
class TestAddresses:
    """Tests for user addresses."""

    def test_create_address(self, authenticated_client, user):
        """Test creating a new address."""
        data = {
            "name": "Work",
            "recipient_name": "Test User",
            "street": "Rua Augusta",
            "number": "500",
            "neighborhood": "Consolação",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "01304000",
        }
        response = authenticated_client.post("/api/v1/auth/addresses/", data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Work"

    def test_list_addresses(self, authenticated_client, address):
        """Test listing user addresses."""
        response = authenticated_client.get("/api/v1/auth/addresses/")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_delete_address(self, authenticated_client, address):
        """Test deleting an address."""
        response = authenticated_client.delete(f"/api/v1/auth/addresses/{address.id}/")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
