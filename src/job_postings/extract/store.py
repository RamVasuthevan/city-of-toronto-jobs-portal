from abc import ABC, abstractmethod
from typing import Dict, List

from core.enums import Portal
from core.types import HTMLString, JobId


class SearchPageStore(ABC):
    @staticmethod
    @abstractmethod
    def store_search_page(job_id: JobId, content: HTMLString) -> None:
        pass

    @staticmethod
    @abstractmethod
    def store_search_pages_for_portal(job_ids: List[JobId], pages: Dict[JobId, HTMLString]) -> None:
        pass

    @staticmethod
    @abstractmethod
    def store_search_pages_for_portals(
        job_ids_by_portal: Dict[Portal, List[JobId]], pages_by_portal: Dict[Portal, Dict[JobId, HTMLString]]
    ) -> None:
        pass


class DirectorySearchPageStore(SearchPageStore):
    @staticmethod
    def store_search_page(portal: Portal, job_id: JobId, content: HTMLString) -> None:
        pass

    @staticmethod
    def store_search_pages_for_portal(portal: Portal, pages: Dict[JobId, HTMLString]) -> None:
        pass

    @staticmethod
    def store_search_pages_for_portals(pages_by_portal: Dict[Portal, Dict[JobId, HTMLString]]) -> None:
        pass
