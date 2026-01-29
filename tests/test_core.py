"""
Tests for core utilities.
"""

import pytest
from decimal import Decimal


class TestCPFValidation:
    """Tests for CPF validation."""

    def test_valid_cpf(self):
        """Test valid CPF numbers."""
        from apps.core.utils import validate_cpf
        
        # Valid CPF numbers
        assert validate_cpf("529.982.247-25") is True
        assert validate_cpf("52998224725") is True

    def test_invalid_cpf(self):
        """Test invalid CPF numbers."""
        from apps.core.utils import validate_cpf
        
        # Invalid CPF numbers
        assert validate_cpf("111.111.111-11") is False
        assert validate_cpf("123.456.789-00") is False
        assert validate_cpf("12345") is False

    def test_cpf_formatting(self):
        """Test CPF formatting."""
        from apps.core.utils import format_cpf
        
        assert format_cpf("52998224725") == "529.982.247-25"


class TestCNPJValidation:
    """Tests for CNPJ validation."""

    def test_valid_cnpj(self):
        """Test valid CNPJ numbers."""
        from apps.core.utils import validate_cnpj
        
        # Valid CNPJ
        assert validate_cnpj("11.222.333/0001-81") is True
        assert validate_cnpj("11222333000181") is True

    def test_invalid_cnpj(self):
        """Test invalid CNPJ numbers."""
        from apps.core.utils import validate_cnpj
        
        # Invalid CNPJ numbers
        assert validate_cnpj("11.111.111/1111-11") is False
        assert validate_cnpj("12.345.678/0001-00") is False


class TestCurrencyFormatting:
    """Tests for currency formatting."""

    def test_format_currency(self):
        """Test Brazilian currency formatting."""
        from apps.core.utils import format_currency
        
        assert format_currency(Decimal("1234.56")) == "R$ 1.234,56"
        assert format_currency(Decimal("99.90")) == "R$ 99,90"
        assert format_currency(Decimal("0.01")) == "R$ 0,01"


class TestPhoneFormatting:
    """Tests for phone number formatting."""

    def test_format_phone_11_digits(self):
        """Test 11-digit phone formatting."""
        from apps.core.utils import format_phone
        
        assert format_phone("11987654321") == "(11) 98765-4321"

    def test_format_phone_10_digits(self):
        """Test 10-digit phone formatting."""
        from apps.core.utils import format_phone
        
        assert format_phone("1133334444") == "(11) 3333-4444"


class TestCEPFormatting:
    """Tests for CEP (postal code) formatting."""

    def test_normalize_cep(self):
        """Test CEP normalization."""
        from apps.core.utils import normalize_cep
        
        assert normalize_cep("01310-100") == "01310100"
        assert normalize_cep("01310100") == "01310100"

    def test_format_cep(self):
        """Test CEP formatting."""
        from apps.core.utils import format_cep
        
        assert format_cep("01310100") == "01310-100"


class TestOrderNumberGeneration:
    """Tests for order number generation."""

    def test_generate_order_number_format(self):
        """Test order number format."""
        from apps.core.utils import generate_order_number
        
        order_number = generate_order_number()
        
        assert order_number.startswith("ORD-")
        parts = order_number.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 4  # Year
        assert len(parts[2]) == 8  # Unique ID

    def test_generate_order_number_unique(self):
        """Test that order numbers are unique."""
        from apps.core.utils import generate_order_number
        
        numbers = [generate_order_number() for _ in range(100)]
        
        assert len(set(numbers)) == 100  # All unique


class TestDiscountCalculation:
    """Tests for discount percentage calculation."""

    def test_calculate_discount_percentage(self):
        """Test discount percentage calculation."""
        from apps.core.utils import calculate_discount_percentage
        
        # 10% discount
        assert calculate_discount_percentage(Decimal("100"), Decimal("90")) == 10
        # 25% discount
        assert calculate_discount_percentage(Decimal("200"), Decimal("150")) == 25
        # 50% discount
        assert calculate_discount_percentage(Decimal("100"), Decimal("50")) == 50

    def test_no_discount(self):
        """Test when there's no discount."""
        from apps.core.utils import calculate_discount_percentage
        
        # Same price
        assert calculate_discount_percentage(Decimal("100"), Decimal("100")) is None
        # Higher sale price (invalid)
        assert calculate_discount_percentage(Decimal("100"), Decimal("120")) is None
