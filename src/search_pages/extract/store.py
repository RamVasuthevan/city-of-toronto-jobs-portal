import os
from abc import ABC, abstractmethod
from typing import Dict, List

from core.types import HTMLString
from core.enums import Portal
from core.exception import DirectoryStoreError

class SearchPageStore(ABC):
    @staticmethod
    @abstractmethod
    def store_search_page(portal: Portal, page_number: int, content: HTMLString) -> None:
        """Store single search page"""
        pass
        
    @staticmethod
    @abstractmethod
    def store_search_pages_for_portal(portal: Portal, pages: List[HTMLString]) -> None:
        """Store multiple search pages"""
        pass
        
    @staticmethod
    @abstractmethod
    def store_search_pages_for_portals(pages_by_portal: Dict[Portal, List[HTMLString]]) -> None:
        """Store search pages for multiple portals"""
        pass

class DirectorySearchPageStore(SearchPageStore):
    """Implementation that stores to filesystem"""
    
    BASE_DIR = "downloaded/search_pages"
    
    @staticmethod
    def store_search_page(portal: Portal, page_number: int, content: HTMLString) -> None:
        """Store single search page to filesystem"""
        portal_dir = os.path.join(DirectorySearchPageStore.BASE_DIR, portal.value)
        os.makedirs(portal_dir, exist_ok=True)
        
        file_path = os.path.join(portal_dir, f"{page_number}.html")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            raise DirectoryStoreError(f"Failed to store page {page_number} for {portal.value}: {str(e)}")
    
    @staticmethod
    def store_search_pages_for_portal(portal: Portal, pages: List[HTMLString]) -> None:
        """Store multiple search pages for a portal"""
        for page_number, content in enumerate(pages):
            DirectorySearchPageStore.store_search_page(portal, page_number, content)
    
    @staticmethod
    def store_search_pages_for_portals(pages_by_portal: Dict[Portal, List[HTMLString]]) -> None:
        """Store search pages for multiple portals"""
        for portal, pages in pages_by_portal.items():
            DirectorySearchPageStore.store_search_pages_for_portal(portal, pages)