import requests
from .config import get_api_key, get_base_url
import contextlib
import functools
import logging

logger = logging.getLogger(__name__)

def handle_api_exceptions(func):
    """Decorator to handle API request exceptions gracefully."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except requests.exceptions.HTTPError as e:
            response = e.response
            status_code = response.status_code
            if status_code == 403:
                logger.error("❌ [bold red]Invalid API key! Please verify your API credentials.[/bold red]", extra={"markup": True})
                raise ValueError("Invalid API key. Please set a valid API key.")
            logger.error(f"❌ API request failed ({status_code}): {e}")
            raise ValueError(f"API request failed ({status_code}): {e}")

        except requests.exceptions.ConnectionError:
            logger.error("❌ [bold red]Connection error! Unable to reach the API.[/bold red]", extra={"markup": True})
            raise ValueError("Failed to connect to API. Check your internet connection.")

        except requests.exceptions.Timeout:
            logger.warning("⚠️ [bold yellow]API request timed out. Try again later.[/bold yellow]", extra={"markup": True})
            raise ValueError("API request timed out. Try again later.")

        except requests.exceptions.RequestException as e:
            logger.exception(f"❌ [bold red]Unexpected API error:[/bold red] {e}", extra={"markup": True})
            raise ValueError(f"Unexpected API error: {e}")

        except Exception as e:
            logger.exception(f"⚠️ [bold red]Unhandled Exception:[/bold red] {e}", extra={"markup": True})
            raise ValueError(f"An unexpected error occurred: {e}")

    return wrapper

class GPRStudioAPI:
    """Base class for API interactions with shared configurations."""

    def __init__(self):
        self.api_key = get_api_key()
        if not self.api_key:
            logger.error("[bold red]API key is required![/bold red] Use `gprstudio.set_api_key()` to set it.", extra={"markup": True})
            raise ValueError("API key is required. Set it using `gprstudio.set_api_key()`.")

        self.base_uri = get_base_url()
        self.headers = {
            "X-GPRSTUDIO-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        logger.info("[bold green]✅ GPRStudioAPI initialized successfully![/bold green]", extra={"markup": True})

    @handle_api_exceptions
    def request(self, method, endpoint, params=None, data=None):
        """Sends an API request with error handling."""
        url = f"{self.base_uri}/{endpoint}"
        logger.info(f"[cyan]Sending {method} request to:[/cyan] {url}", extra={"markup": True})

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data
        )
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

        logger.info(f"[bold green]✅ API request successful![/bold green] [dim]({response.status_code})[/dim]", extra={"markup": True})
        return response.json()

    @handle_api_exceptions
    @contextlib.contextmanager
    def stream_request(self, method, endpoint, params=None):
        """Streams API response safely."""
        url = f"{self.base_uri}/{endpoint}"
        logger.info(f"[cyan]Starting streaming request:[/cyan] {url}",extra={"markup": True})

        response = self.session.request(method=method, url=url, params=params, stream=True)
        response.raise_for_status()
        yield response


