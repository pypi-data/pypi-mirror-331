from .config import set_api_key, set_base_url
from .projects import Projects
from .datasets import Datasets, DatasetsDownloader
import logging
from rich.logging import RichHandler

__all__ = ["set_api_key", "set_base_url", "Projects", "Datasets"]

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(
        rich_tracebacks=False,
        show_path=False
    )],
)

__name__ = "gprstudio"
