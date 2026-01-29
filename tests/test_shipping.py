"""
Tests for the shipping app.
"""

import pytest
from decimal import Decimal
from rest_framework import status
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestShippingCalculate:
    """Tests for shipping calculation endpoint."""

    def test_calculate_shipping_valid_cep(self, api_client):
        """Test calculating shipping with valid CEP."""
        data = {"zipcode": "01310100"}
        response = api_client.post("/api/v1/shipping/calculate/", data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "data" in response.data
        assert len(response.data["data"]) > 0

    def test_calculate_shipping_invalid_cep(self, api_client):
        """Test calculating shipping with invalid CEP."""
        data = {"zipcode": "123"}  # Invalid CEP
        response = api_client.post("/api/v1/shipping/calculate/", data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_calculate_shipping_with_weight(self, api_client):
        """Test calculating shipping with custom weight."""
        data = {
            "zipcode": "01310100",
            "weight": 2.5,
        }
        response = api_client.post("/api/v1/shipping/calculate/", data)
        
        assert response.status_code == status.HTTP_200_OK

    def test_calculate_shipping_with_dimensions(self, api_client):
        """Test calculating shipping with custom dimensions."""
        data = {
            "zipcode": "01310100",
            "weight": 1.0,
            "length": 30,
            "height": 20,
            "width": 15,
        }
        response = api_client.post("/api/v1/shipping/calculate/", data)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestShippingTrack:
    """Tests for shipment tracking endpoint."""

    def test_track_shipment_valid_code(self, api_client):
        """Test tracking with valid code."""
        response = api_client.get("/api/v1/shipping/track/SS123456789BR/")
        
        # May succeed or fail depending on API availability
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_track_shipment_invalid_code(self, api_client):
        """Test tracking with invalid code."""
        response = api_client.get("/api/v1/shipping/track/123/")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCorreiosService:
    """Tests for CorreiosService."""

    def test_shipping_option_dataclass(self):
        """Test ShippingOption dataclass."""
        from apps.shipping.services import ShippingOption
        
        option = ShippingOption(
            code="sedex",
            name="SEDEX",
            price=Decimal("35.90"),
            delivery_time="3 dias úteis",
            min_days=3,
            max_days=5,
        )
        
        assert option.code == "sedex"
        assert option.price == Decimal("35.90")
        assert option.error is None

    def test_fallback_options(self):
        """Test fallback shipping options."""
        from apps.shipping.services import CorreiosService
        
        service = CorreiosService()
        options = service._get_fallback_options()
        
        assert len(options) == 2
        assert options[0].code == "sedex"
        assert options[1].code == "pac"

    def test_get_service_name(self):
        """Test service code to name mapping."""
        from apps.shipping.services import CorreiosService
        
        service = CorreiosService()
        
        assert service._get_service_name("04014") == "SEDEX"
        assert service._get_service_name("04510") == "PAC"
        assert service._get_service_name("99999") == "Correios (99999)"

    @patch("apps.shipping.services.requests.get")
    def test_calculate_shipping_api_error(self, mock_get):
        """Test fallback when Correios API fails."""
        from apps.shipping.services import CorreiosService
        import requests
        
        mock_get.side_effect = requests.RequestException("API Error")
        
        service = CorreiosService()
        options = service.calculate_shipping("01310100")
        
        # Should return fallback options
        assert len(options) == 2
        assert options[0].code == "sedex"
