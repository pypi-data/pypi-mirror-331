from .base import GPRStudioAPI
import xarray as xr
import gcsfs
import zarr
import fsspec
import requests
from zarr.storage import KVStore, FSStore


class SignedURLMapper:
    def __init__(self, signed_urls, prefix="67c1564b67d58297a1d89b65.zarr/"):
        """Initialize with a dictionary of signed URLs."""
        self.signed_urls = signed_urls
        self.prefix = prefix

    def __getitem__(self, key):
        print(key)
        """Fetch file content via signed URL."""
        url = self.signed_urls.get(self.prefix + key)
        if not url:
            raise KeyError(f"Signed URL not found for {key}")

        response = requests.get(url)
        if response.status_code != 200:
            raise KeyError(f"Failed to fetch {key} from {url}")

        return response.content  # Return raw file content

    def __contains__(self, key):
        """Check if key exists in signed URL mapping."""
        return (self.prefix + key) in self.signed_urls

    def keys(self):
        """Return all available keys."""
        return [key[len(self.prefix):] for key in self.signed_urls.keys()]


class Datasets(GPRStudioAPI):
    """Handles dataset-related API operations."""

    def get_datasets(self, params=None):
        """Fetch all datasets."""
        return self.request("GET", "dataset", params=params)

    def load_dataset(self, dataset_id: str):
        #signed_url =  self.request("GET", f"dataset/getDatasetUrl/{dataset_id}")
        read_dataset = self.request("GET", f"dataset/getDatasetUrl/{dataset_id}")
        signed_url = read_dataset.json()
        zarr_dataset = zarr.open(store, mode="r")
        #signed_url = response["signedUrl"]
        #return open_zarr_dataset_from_signed_url(signed_url)
