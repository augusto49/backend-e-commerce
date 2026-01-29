"""
Correios API integration service.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ShippingOption:
    """Shipping option dataclass."""

    code: str
    name: str
    price: Decimal
    delivery_time: str
    min_days: int
    max_days: int
    error: Optional[str] = None


class CorreiosService:
    """
    Service for calculating shipping costs using Correios API.
    
    Uses the public Correios web service for price/deadline calculation.
    For tracking, uses the SRO (Sistema de Rastreamento de Objetos).
    """

    # Correios service codes
    SERVICES = {
        "sedex": "04014",      # SEDEX à vista
        "pac": "04510",        # PAC à vista
        "sedex10": "40215",    # SEDEX 10
        "sedex12": "40169",    # SEDEX 12
        "sedex_hoje": "40290", # SEDEX Hoje
    }

    # Correios API URLs
    CALC_PRICE_URL = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx/CalcPrecoPrazo"
    TRACKING_URL = "https://www.linkcorreios.com.br/"

    def __init__(
        self,
        origin_cep: Optional[str] = None,
        company_code: Optional[str] = None,
        company_password: Optional[str] = None,
    ):
        self.origin_cep = origin_cep or getattr(settings, "CORREIOS_ORIGIN_CEP", "01310100")
        self.company_code = company_code or getattr(settings, "CORREIOS_COMPANY_CODE", "")
        self.company_password = company_password or getattr(settings, "CORREIOS_PASSWORD", "")

    def calculate_shipping(
        self,
        destination_cep: str,
        weight: Decimal = Decimal("0.5"),
        length: int = 20,
        height: int = 10,
        width: int = 15,
        services: Optional[List[str]] = None,
    ) -> List[ShippingOption]:
        """
        Calculate shipping options for a destination.

        Args:
            destination_cep: Destination ZIP code (CEP)
            weight: Package weight in kg
            length: Package length in cm
            height: Package height in cm
            width: Package width in cm
            services: List of service codes to calculate (default: sedex, pac)

        Returns:
            List of ShippingOption with prices and deadlines
        """
        destination_cep = destination_cep.replace("-", "").replace(".", "")
        
        if services is None:
            services = ["sedex", "pac"]

        service_codes = ",".join(
            self.SERVICES.get(s, s) for s in services if s in self.SERVICES
        )

        params = {
            "nCdEmpresa": self.company_code,
            "sDsSenha": self.company_password,
            "nCdServico": service_codes,
            "sCepOrigem": self.origin_cep,
            "sCepDestino": destination_cep,
            "nVlPeso": str(weight),
            "nCdFormato": 1,  # Box format
            "nVlComprimento": length,
            "nVlAltura": height,
            "nVlLargura": width,
            "nVlDiametro": 0,
            "sCdMaoPropria": "N",
            "nVlValorDeclarado": 0,
            "sCdAvisoRecebimento": "N",
        }

        try:
            response = requests.get(self.CALC_PRICE_URL, params=params, timeout=10)
            response.raise_for_status()
            return self._parse_response(response.text)
        except requests.RequestException as e:
            logger.exception("Correios API error")
            # Return fallback options if API fails
            return self._get_fallback_options()

    def _parse_response(self, xml_response: str) -> List[ShippingOption]:
        """Parse Correios XML response."""
        import xml.etree.ElementTree as ET

        options = []
        
        try:
            root = ET.fromstring(xml_response)
            
            # Find all service results
            for service in root.findall(".//cServico"):
                code = service.findtext("Codigo", "")
                error_code = service.findtext("Erro", "0")
                error_msg = service.findtext("MsgErro", "")
                
                # Get service name from code
                name = self._get_service_name(code)
                
                if error_code != "0":
                    options.append(ShippingOption(
                        code=code,
                        name=name,
                        price=Decimal("0"),
                        delivery_time="",
                        min_days=0,
                        max_days=0,
                        error=error_msg,
                    ))
                    continue

                # Parse price (format: "35,90")
                price_str = service.findtext("Valor", "0").replace(".", "").replace(",", ".")
                price = Decimal(price_str)

                # Parse deadline
                deadline = int(service.findtext("PrazoEntrega", "0"))

                options.append(ShippingOption(
                    code=code,
                    name=name,
                    price=price,
                    delivery_time=f"{deadline} dias úteis",
                    min_days=deadline,
                    max_days=deadline + 2,  # Buffer for delays
                ))

        except ET.ParseError as e:
            logger.exception("Failed to parse Correios response")
            return self._get_fallback_options()

        return options

    def _get_service_name(self, code: str) -> str:
        """Get human-readable service name from code."""
        names = {
            "04014": "SEDEX",
            "04510": "PAC",
            "40215": "SEDEX 10",
            "40169": "SEDEX 12",
            "40290": "SEDEX Hoje",
        }
        return names.get(code, f"Correios ({code})")

    def _get_fallback_options(self) -> List[ShippingOption]:
        """Return fallback options when API is unavailable."""
        return [
            ShippingOption(
                code="sedex",
                name="SEDEX",
                price=Decimal("35.90"),
                delivery_time="3 a 5 dias úteis",
                min_days=3,
                max_days=5,
            ),
            ShippingOption(
                code="pac",
                name="PAC",
                price=Decimal("22.50"),
                delivery_time="8 a 12 dias úteis",
                min_days=8,
                max_days=12,
            ),
        ]

    def track_package(self, tracking_code: str) -> dict:
        """
        Track a package using the tracking code.

        Args:
            tracking_code: Correios tracking code (e.g., SS123456789BR)

        Returns:
            Dictionary with tracking events
        """
        try:
            # Using public tracking API
            url = f"{self.TRACKING_URL}{tracking_code}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return self._parse_tracking_response(response.text, tracking_code)
            
            return {
                "code": tracking_code,
                "error": "Could not retrieve tracking information",
                "events": [],
            }

        except requests.RequestException as e:
            logger.exception("Tracking API error")
            return {
                "code": tracking_code,
                "error": str(e),
                "events": [],
            }

    def _parse_tracking_response(self, html: str, tracking_code: str) -> dict:
        """Parse tracking HTML response."""
        # Simple regex-based parsing for tracking info
        import re
        
        events = []
        
        # Pattern to find tracking events
        # This is a simplified parser - in production, use BeautifulSoup
        pattern = r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s*-?\s*([^<]+)'
        matches = re.findall(pattern, html)
        
        for match in matches:
            date, time, description = match
            events.append({
                "date": date,
                "time": time,
                "description": description.strip(),
            })

        return {
            "code": tracking_code,
            "events": events[:10],  # Limit to last 10 events
        }
