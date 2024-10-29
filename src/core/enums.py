from enum import Enum


class Portal(Enum):
    JOBS_AT_CITY = "jobsatcity"
    RECREATION = "recreation"

    @property
    def search_page_url(self) -> str:
        return f"https://jobs.toronto.ca/{self.value}/tile-search-results/"
    
    @property 
    def job_page_url_template(self) -> str:
        return f"https://jobs.toronto.ca/{self.value}/{{relative_url}}"