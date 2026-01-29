"""
Custom pagination classes for the E-commerce API.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class used across the API.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for endpoints that may return large datasets.
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for endpoints with smaller datasets.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
