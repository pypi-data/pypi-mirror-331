from .base import GPRStudioAPI
import xarray as xr
import gcsfs
import zarr
import fsspec
import requests
from zarr.storage import KVStore, FSStore
from gprlibpy.core import Dataset
from rich.progress import Progress, BarColumn, DownloadColumn, TimeRemainingColumn
import logging
import os
from pathlib import Path

logger = logging.getLogger("rich")


class Datasets(GPRStudioAPI):
    """Handles dataset-related API operations."""

    def get_datasets(self, params=None):
        """Fetch all datasets."""
        return self.request("GET", "dataset", params=params)

class DatasetsDownloader(GPRStudioAPI):
    """Handles dataset-related API operations."""
    def __init__(self, cache_dir: str = ".cache"):
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_datasets(self, params=None):
        """Fetch all datasets."""
        return self.request("GET", "dataset", params=params)

    def get_cached_dataset_path(self, dataset_id):
        """Returns the local path where the dataset should be cached."""
        return os.path.join(self.cache_dir, f"{dataset_id}.zarr")

    def download(self, dataset_id):
        """Streams a dataset from the API, caches it, and reconstructs a Zarr dataset if needed."""
        cached_zarr_path = self.get_cached_dataset_path(dataset_id)

        # ✅ Check if dataset is already cached
        if os.path.exists(cached_zarr_path):
            logger.info(f"✅ Using cached dataset: {cached_zarr_path}")
            return Dataset.from_path(cached_zarr_path)

        # If not cached, proceed with download
        logger.info("⬇️  Dataset not cached. Downloading from server...")
        api_endpoint = f"dataset/download/{dataset_id}"
        temp_zip_path = os.path.join(self.cache_dir, f"{dataset_id}.zarr.zip")

        try:
            # Make a GET request to the streaming endpoint
            with self.stream_request("GET", api_endpoint) as response:
                if response.status_code != 200:
                    raise Exception(f"Failed to download dataset. HTTP {response.status_code}")

                # Extract Content-Length (if available)
                total_size = int(response.headers.get("Content-Length", 0)) if response.headers.get(
                    "Content-Length") else None

                # Display progress bar
                with open(temp_zip_path, "wb") as f, Progress(
                        "[cyan]Downloading Dataset:",
                        BarColumn(),
                        DownloadColumn(),
                        TimeRemainingColumn(),
                ) as progress:
                    task = progress.add_task("[green]Receiving...", total=total_size)

                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

                # ✅ Extract and cache the Zarr dataset
                with zarr.ZipStore(temp_zip_path, mode="r") as store:
                    xr_dataset = xr.open_zarr(store)
                    xr_dataset.to_zarr(cached_zarr_path, mode="w")

                logger.info(f"✅ Dataset saved to cache: {cached_zarr_path}")

                return Dataset.from_path(cached_zarr_path)

        except Exception as e:
            logger.error(f"❌ Failed to download dataset: {e}")
            return None

        finally:
            # Cleanup downloaded zip file after extraction
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
                logger.info(f"🗑️ Deleted temporary file: {temp_zip_path}")

