# config.py
_api_key = None
_base_url = "https://gprstudio-api.cropphenomics.com"  # Default API base URL

def set_api_key(api_key: str):
    """Set the global API key."""
    global _api_key
    _api_key = api_key

def set_base_url(base_url: str):
    """Set the global base URL."""
    global _base_url
    _base_url = base_url

def get_api_key():
    """Retrieve the global API key."""
    return _api_key

def get_base_url():
    """Retrieve the global base URL."""
    return _base_url
