import time
from abc import ABC, abstractmethod
from typing import Dict, List
import os
import requests

from core.types import HTMLString
from core.enums import Portal
from core.exception import DownloadError


class SearchPageProvider(ABC):
    @staticmethod
    @abstractmethod
    def search_page(portal: Portal, page_number: int) -> HTMLString:
        """Fetch single search results page"""
        pass

    @staticmethod
    @abstractmethod
    def search_pages_for_portal(portal: Portal) -> List[HTMLString]:
        """Fetch all search pages for a portal"""
        pass

    @staticmethod
    @abstractmethod
    def search_pages_for_portals(portals: List[Portal] = None) -> Dict[Portal, List[HTMLString]]:
        """Fetch all search pages for multiple portals"""
        pass


class DownloadSearchPageProvider(SearchPageProvider):
    """Implementation that downloads pages from web"""

    ITEMS_PER_PAGE = 25
    SLEEP_BETWEEN_REQUESTS = 2
    END_OF_JOBS_MARKER = "<!DOCTYPE HTML>"

    @staticmethod
    def search_page(portal: Portal, page_number: int) -> HTMLString:
        params = {
            "q": "",
            "startrow": page_number * DownloadSearchPageProvider.ITEMS_PER_PAGE,
            "_": int(time.time() * 1000),
            # 'sortColumn': 'referencedate',  # Sort by reference/posting date
            # 'sortDirection': 'desc',        # Sort direction (ascending/descending)
        }

        try:
            response = requests.get(portal.search_page_url, params=params, timeout=30)
            response.raise_for_status()

            if "text/html" not in response.headers.get("Content-Type", ""):
                raise DownloadError(
                    f"Expected HTML content but received '{response.headers.get('Content-Type')}' on page {page_number}"
                )

            return HTMLString(response.text)

        except requests.RequestException as e:
            raise DownloadError(f"Failed to download page {page_number}: {str(e)}")

    @staticmethod
    def search_pages_for_portal(portal: Portal) -> List[HTMLString]:
        pages = []
        page_number = 0

        while True:
            content = DownloadSearchPageProvider.search_page(portal, page_number)

            if content.strip().lower() == DownloadSearchPageProvider.END_OF_JOBS_MARKER.lower():
                break

            pages.append(content)
            page_number += 1
            time.sleep(DownloadSearchPageProvider.SLEEP_BETWEEN_REQUESTS)

        return pages

    @staticmethod
    def search_pages_for_portals(portals: List[Portal] = None) -> Dict[Portal, List[HTMLString]]:
        if portals is None:
            portals = list(Portal)

        return {portal: DownloadSearchPageProvider.search_pages_for_portal(portal) for portal in portals}


class DirectorySearchPageProvider(SearchPageProvider):
    """Implementation that reads from filesystem"""

    BASE_DIR = "downloaded/search_pages"

    @staticmethod
    def search_page(portal: Portal, page_number: int) -> HTMLString:
        file_path = os.path.join(DirectorySearchPageProvider.BASE_DIR, portal.value, f"{page_number}.html")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return HTMLString(f.read())
        except FileNotFoundError:
            raise DownloadError(f"Page {page_number} not found for {portal.value}")

    @staticmethod
    def search_pages_for_portal(portal: Portal) -> List[HTMLString]:
        pages = []
        page_number = 0

        while True:
            try:
                page = DirectorySearchPageProvider.search_page(portal, page_number)
                pages.append(page)
                page_number += 1
            except DownloadError:
                break

        return pages

    @staticmethod
    def search_pages_for_portals(portals: List[Portal] = None) -> Dict[Portal, List[HTMLString]]:
        if portals is None:
            portals = list(Portal)

        return {portal: DirectorySearchPageProvider.search_pages_for_portal(portal) for portal in portals}
