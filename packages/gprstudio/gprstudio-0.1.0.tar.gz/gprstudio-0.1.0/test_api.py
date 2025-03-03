import gprstudio

# Set API credentials and base URL before making requests
gprstudio.set_api_key("d341eda8625d4a42a2a9defa7ddca2cb")
gprstudio.set_base_url("http://localhost:8081/")

# Fetch projects and datasets
projects = gprstudio.Projects().get_projects()
datasets = gprstudio.Datasets().get_datasets()

