from .base import GPRStudioAPI

class Projects(GPRStudioAPI):
    """Handles project-related API operations."""

    def get_projects(self, params=None):
        """Fetch all projects with optional query parameters."""
        return self.request("GET", "project", params=params)
