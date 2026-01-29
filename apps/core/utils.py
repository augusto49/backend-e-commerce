"""
Utility functions for the E-commerce Backend.
"""

import re
from decimal import Decimal
from typing import Optional


def validate_cpf(cpf: str) -> bool:
    """
    Validate a Brazilian CPF number.
    
    Args:
        cpf: CPF string (can contain dots and dashes)
        
    Returns:
        True if valid, False otherwise
    """
    # Remove non-numeric characters
    cpf = re.sub(r"[^0-9]", "", cpf)

    # CPF must have 11 digits
    if len(cpf) != 11:
        return False

    # Check for invalid CPFs (all same digits)
    if cpf == cpf[0] * 11:
        return False

    # Calculate first verification digit
    sum_of_products = sum(int(cpf[i]) * (10 - i) for i in range(9))
    first_digit = (sum_of_products * 10) % 11
    if first_digit == 10:
        first_digit = 0

    if int(cpf[9]) != first_digit:
        return False

    # Calculate second verification digit
    sum_of_products = sum(int(cpf[i]) * (11 - i) for i in range(10))
    second_digit = (sum_of_products * 10) % 11
    if second_digit == 10:
        second_digit = 0

    return int(cpf[10]) == second_digit


def format_cpf(cpf: str) -> str:
    """
    Format a CPF number with dots and dash.
    
    Args:
        cpf: CPF string (numbers only)
        
    Returns:
        Formatted CPF (e.g., 123.456.789-00)
    """
    cpf = re.sub(r"[^0-9]", "", cpf)
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def validate_cnpj(cnpj: str) -> bool:
    """
    Validate a Brazilian CNPJ number.
    
    Args:
        cnpj: CNPJ string (can contain dots, slashes, and dashes)
        
    Returns:
        True if valid, False otherwise
    """
    # Remove non-numeric characters
    cnpj = re.sub(r"[^0-9]", "", cnpj)

    # CNPJ must have 14 digits
    if len(cnpj) != 14:
        return False

    # Check for invalid CNPJs (all same digits)
    if cnpj == cnpj[0] * 14:
        return False

    # Calculate first verification digit
    weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_of_products = sum(int(cnpj[i]) * weights[i] for i in range(12))
    remainder = sum_of_products % 11
    first_digit = 0 if remainder < 2 else 11 - remainder

    if int(cnpj[12]) != first_digit:
        return False

    # Calculate second verification digit
    weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_of_products = sum(int(cnpj[i]) * weights[i] for i in range(13))
    remainder = sum_of_products % 11
    second_digit = 0 if remainder < 2 else 11 - remainder

    return int(cnpj[13]) == second_digit


def format_currency(value: Decimal) -> str:
    """
    Format a decimal value as Brazilian currency.
    
    Args:
        value: Decimal value
        
    Returns:
        Formatted currency string (e.g., R$ 1.234,56)
    """
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_phone(phone: str) -> str:
    """
    Format a Brazilian phone number.
    
    Args:
        phone: Phone number (numbers only)
        
    Returns:
        Formatted phone (e.g., (11) 98765-4321)
    """
    phone = re.sub(r"[^0-9]", "", phone)
    if len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    return phone


def normalize_cep(cep: str) -> str:
    """
    Normalize a Brazilian CEP (postal code).
    
    Args:
        cep: CEP string (can contain dash)
        
    Returns:
        CEP with only numbers
    """
    return re.sub(r"[^0-9]", "", cep)


def format_cep(cep: str) -> str:
    """
    Format a Brazilian CEP with dash.
    
    Args:
        cep: CEP string (numbers only)
        
    Returns:
        Formatted CEP (e.g., 01310-100)
    """
    cep = normalize_cep(cep)
    if len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"
    return cep


def generate_order_number() -> str:
    """
    Generate a unique order number.
    
    Returns:
        Order number in format ORD-YYYY-XXXXXXXX
    """
    import uuid
    from datetime import datetime

    year = datetime.now().year
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"ORD-{year}-{unique_id}"


def calculate_discount_percentage(
    original_price: Decimal, sale_price: Decimal
) -> Optional[int]:
    """
    Calculate discount percentage between original and sale price.
    
    Args:
        original_price: Original price
        sale_price: Sale price
        
    Returns:
        Discount percentage as integer, or None if no discount
    """
    if original_price <= 0 or sale_price >= original_price:
        return None
    discount = ((original_price - sale_price) / original_price) * 100
    return int(discount)
