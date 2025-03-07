"""
Main client class for interacting with the Leja Recharge API.
"""

import base64
import httpx
from typing import List, Optional, Union

from .exceptions import APIError, AuthenticationError, NetworkError
from .models import (
    AirtimePurchaseRequest,
    AirtimeRecipient,
    BalanceResponse,
    CountryResponse,
    TransactionResponse,
    AsyncTransactionResponse
)


class LejaRechargeClient:
    """
    Client for interacting with the Leja Recharge API.
    
    Args:
        client_id (str): Your Client ID for authentication
        api_key (str): Your API key for authentication
        base_url (str, optional): Base URL for the API. Defaults to production URL.
        timeout (int, optional): Request timeout in seconds. Defaults to 30.
    """

    def __init__(
        self,
        client_id: str,
        api_key: str,
        base_url: str = "https://recharge.leja.co.ke/api/v1",
        timeout: int = 30
    ):
        if not client_id or not api_key:
            raise AuthenticationError("Both client_id and api_key are required")
        
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # Create Basic Auth header
        auth_string = f"{client_id}:{api_key}"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Basic {base64_auth}",
                "Content-Type": "application/json",
                "User-Agent": "leja-recharge-python/0.1.3",
            }
        )

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            raise APIError(
                f"API request failed: {e.response.text}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise NetworkError(f"Network error occurred: {str(e)}")

    def purchase_airtime(
        self,
        phone_number: str,
        recipients: List[AirtimeRecipient],
        is_async: bool = True,
        callback_url: Optional[str] = None
    ) -> Union[TransactionResponse, AsyncTransactionResponse]:
        """
        Purchase airtime for one or more recipients.
        
        Args:
            phone_number (str): Sender's phone number
            recipients (List[AirtimeRecipient]): List of recipients
            is_async (bool, optional): Whether to process asynchronously. Defaults to True.
            callback_url (Optional[str], optional): Callback URL for async requests.
            
        Returns:
            TransactionResponse or AsyncTransactionResponse: Transaction details
        """
        request = AirtimePurchaseRequest(
            phone_number=phone_number,
            recipients=recipients,
            is_async=is_async,
            callback_url=callback_url
        )
        
        response = self._client.post("/airtime/purchase", json=request.model_dump())
        data = self._handle_response(response)
        return TransactionResponse(**data) if not is_async else AsyncTransactionResponse(**data)

    def get_transaction(
        self,
        external_id: Optional[str] = None,
        tracking_id: Optional[str] = None
    ) -> TransactionResponse:
        """
        Retrieve transaction details.
        
        Args:
            external_id (Optional[str]): External transaction ID
            tracking_id (Optional[str]): Tracking ID
            
        Returns:
            TransactionResponse: Transaction details
        """
        if not external_id and not tracking_id:
            raise ValueError("Either external_id or tracking_id must be provided")
            
        params = {}
        if external_id:
            params["external_id"] = external_id
        if tracking_id:
            params["tracking_id"] = tracking_id
            
        response = self._client.get("/airtime/query/transaction", params=params)
        data = self._handle_response(response)
        return TransactionResponse(**data)

    def get_balance(self) -> BalanceResponse:
        """
        Get account balance.
        
        Returns:
            BalanceResponse: Account balance details
        """
        response = self._client.get(f"/accounts/{self.client_id}/balance")
        data = self._handle_response(response)
        return BalanceResponse(**data)

    def get_countries(
        self,
        page: int = 1,
        limit: int = 20
    ) -> List[CountryResponse]:
        """
        Get list of supported countries.
        
        Args:
            page (int, optional): Page number. Defaults to 1.
            limit (int, optional): Items per page. Defaults to 20.
            
        Returns:
            List[CountryResponse]: List of country details
        """
        params = {"page": page, "limit": limit}
        response = self._client.get("/countries", params=params)
        data = self._handle_response(response)
        return [CountryResponse(**country) for country in data.get("data", [])]

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._client.close() 