import requests
from .config import get_api_key, get_base_url

class GPRStudioAPI:
    """Base class for API interactions with shared configurations."""

    def __init__(self):
        self.api_key = get_api_key()
        if not self.api_key:
            raise ValueError("API key is required. Set it using gprstudio.set_api_key().")

        self.base_uri = get_base_url()

        # Setup authentication headers
        self.headers = {
            "X-GPRSTUDIO-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        # Use a persistent session for performance
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def request(self, method, endpoint, params=None, data=None):
        """Generic method to send API requests."""
        url = f"{self.base_uri}/{endpoint}"  # Append endpoint to base URI
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data  # Payload for POST/PUT requests
            )
            response.raise_for_status()  # Raise error for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"API request failed: {e}")
