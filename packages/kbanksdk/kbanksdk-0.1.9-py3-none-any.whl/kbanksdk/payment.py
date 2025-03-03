from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import requests
from datetime import datetime


class CardChargeRequest(BaseModel):
    """Request model for card charge API"""

    amount: float = Field(..., ge=0.01)
    currency: str = Field(..., max_length=3)
    description: str = Field(..., max_length=500)
    source_type: str = Field(default="card")
    mode: str = Field(..., pattern="^(token|customer)$")
    token: Optional[str] = Field(None, max_length=50)
    customer_id: Optional[str] = Field(None, max_length=50)
    card_id: Optional[str] = Field(None, max_length=50)
    reference_order: str = Field(..., max_length=50)
    reference_1: Optional[str] = Field(None, max_length=50)
    reference_2: Optional[str] = Field(None, max_length=50)
    reference_3: Optional[str] = Field(None, max_length=50)
    webhook_url: Optional[str] = Field(None, max_length=500)
    save_card: bool = False
    metadata: Optional[Dict[str, str]] = None

    def to_api_payload(self) -> dict:
        """Convert the model to API payload format"""
        payload = self.model_dump(by_alias=True, exclude_none=True)
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


class KBankPaymentGateway:
    """KBank Payment Gateway API client"""

    SANDBOX_URL = "https://dev-kpaymentgateway-services.kasikornbank.com"
    PRODUCTION_URL = "https://kpaymentgateway-services.kasikornbank.com"

    def __init__(self, api_key: str, secret_key: str, environment: str = "sandbox"):
        """Initialize the payment gateway client

        Args:
            api_key: API key from KBank
            secret_key: Secret key from KBank
            environment: Either 'sandbox' or 'production'
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = (
            self.SANDBOX_URL if environment == "sandbox" else self.PRODUCTION_URL
        )
        self.environment = environment

    def _get_headers(self) -> Dict[str, str]:
        """Get required headers for API requests"""
        return {"x-api-key": self.api_key, "Content-Type": "application/json"}

    def create_charge(self, charge_request: CardChargeRequest) -> Dict[str, Any]:
        """Create a new charge

        Args:
            charge_request: CardChargeRequest object containing charge details

        Returns:
            Dict containing the API response

        Raises:
            KBankAPIError: If the API request fails
        """
        try:
            headers = self._get_headers()
            payload = charge_request.to_api_payload()

            response = requests.post(
                f"{self.base_url}/card/v2/charge", headers=headers, json=payload
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise KBankAPIError(f"Failed to create charge: {str(e)}")


class KBankAPIError(Exception):
    """Custom exception for KBank API errors"""

    pass
