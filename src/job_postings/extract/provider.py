from abc import ABC, abstractmethod
from typing import Dict, List

from core.enums import Portal
from core.types import HTMLString, JobId


class JobPostingProvider(ABC):
    @staticmethod
    @abstractmethod
    def search_page(portal: Portal, relative_url: str) -> HTMLString:
        pass

    @staticmethod
    @abstractmethod
    def search_pages_for_portal(portal: Portal, relative_urls: List[str]) -> Dict[JobId, HTMLString]:
        pass

    @staticmethod
    @abstractmethod
    def search_pages_for_portals(
        relative_urls_by_portal: Dict[Portal, List[str]]
    ) -> Dict[Portal, Dict[JobId, HTMLString]]:
        pass


class DownloadJobPostingProvider(JobPostingProvider):
    @staticmethod
    def search_page(portal: Portal, relative_url: str) -> HTMLString:
        pass

    @staticmethod
    def search_pages_for_portal(portal: Portal, relative_urls: List[str]) -> Dict[JobId, HTMLString]:
        pass

    @staticmethod
    def search_pages_for_portals(
        relative_urls_by_portal: Dict[Portal, List[str]]
    ) -> Dict[Portal, Dict[JobId, HTMLString]]:
        pass


class DirectoryJobPostingProvider(JobPostingProvider):
    @staticmethod
    def search_page(portal: Portal, job_id: JobId) -> HTMLString:
        pass

    @staticmethod
    def search_pages_for_portal(portal: Portal, job_ids: List[JobId]) -> Dict[JobId, HTMLString]:
        pass

    @staticmethod
    def search_pages_for_portals(job_ids_by_portal: Dict[Portal, List[JobId]]) -> Dict[Portal, Dict[JobId, HTMLString]]:
        pass
