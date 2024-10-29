from abc import ABC, abstractmethod
from typing import Dict, List
from bs4 import BeautifulSoup

from core.types import HTMLString
from core.enums import Portal
from core.models import SearchResult
from core.exception import ParseError


class SearchPageParser(ABC):
    @staticmethod
    @abstractmethod
    def parse_search_page(page: HTMLString, portal: Portal) -> List[SearchResult]:
        """Parse search results from single search page"""
        pass

    @staticmethod
    @abstractmethod
    def parse_search_pages_for_portal(pages: List[HTMLString], portal: Portal) -> List[SearchResult]:
        """Parse search results from multiple search pages"""
        pass

    @staticmethod
    @abstractmethod
    def parse_search_pages_for_portals(
        pages_by_portal: Dict[Portal, List[HTMLString]]
    ) -> Dict[Portal, List[SearchResult]]:
        """Parse search results from multiple portals"""
        pass


class DefaultSearchPageParser(SearchPageParser):
    """Default implementation using BeautifulSoup"""

    @staticmethod
    def parse_search_page(page: HTMLString, portal: Portal) -> List[SearchResult]:
        """Parse search results from a single search page using BeautifulSoup"""
        soup = BeautifulSoup(page, "html.parser")
        results = []

        for job_tile in soup.find_all("li", class_="job-tile"):
            try:
                desktop_section = job_tile.find("div", class_="sub-section-desktop")
                if not desktop_section:
                    raise ParseError("Could not find desktop section in job tile")

                job_stream_elem = desktop_section.find(
                    "div", id=lambda x: x and "desktop-section-department-value" in x
                )
                job_stream = job_stream_elem.text.strip() if job_stream_elem else None

                result = SearchResult(
                    job_id=[cls for cls in job_tile["class"] if cls.startswith("job-id-")][0].replace("job-id-", ""),
                    relative_url=job_tile["data-url"],
                    title=desktop_section.find("a", class_="jobTitle-link").text.strip(),
                    job_stream=job_stream,
                    position_type=desktop_section.find(
                        "div", id=lambda x: x and "desktop-section-shifttype-value" in x
                    ).text.strip(),
                    posting_date=desktop_section.find(
                        "div", id=lambda x: x and "desktop-section-date-value" in x
                    ).text.strip(),
                    portal=portal.value,
                )
                results.append(result)

            except (AttributeError, KeyError, IndexError) as e:
                raise ParseError(f"Failed to parse job tile: {str(e)}")

        return results

    @staticmethod
    def parse_search_pages_for_portal(pages: List[HTMLString], portal: Portal) -> List[SearchResult]:
        """Parse search results from multiple search pages for a portal"""
        all_results = []
        for content in pages:
            results = DefaultSearchPageParser.parse_search_page(content, portal)
            all_results.extend(results)
        return all_results

    @staticmethod
    def parse_search_pages_for_portals(
        pages_by_portal: Dict[Portal, List[HTMLString]]
    ) -> Dict[Portal, List[SearchResult]]:
        """Parse search results from multiple portals"""
        return {
            portal: DefaultSearchPageParser.parse_search_pages_for_portal(pages, portal)
            for portal, pages in pages_by_portal.items()
        }
