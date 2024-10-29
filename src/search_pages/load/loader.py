import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List

from core.enums import Portal
from core.models import SearchResult
from core.exception import DirectoryLoadError

class SearchResultLoader(ABC):
    @staticmethod
    @abstractmethod
    def save_search_result(portal: Portal, result: SearchResult) -> None:
        """Save single search result"""
        pass

    @staticmethod
    @abstractmethod
    def save_search_results_for_portal(portal: Portal, results: List[SearchResult]) -> None:
        """Save search results for single portal"""
        pass
        
    @staticmethod
    @abstractmethod
    def save_search_results_for_portals(results_by_portal: Dict[Portal, List[SearchResult]]) -> None:
        """Save search results for multiple portals"""
        pass

class JSONSearchResultLoader(SearchResultLoader):
    """Implementation that saves search results to JSON files"""
    
    BASE_DIR = "downloaded"
    FILENAME = "search_results.json"
    
    @staticmethod
    def save_search_result(portal: Portal, result: SearchResult) -> None:
        """Save single search result to JSON file"""
        os.makedirs(JSONSearchResultLoader.BASE_DIR, exist_ok=True)
        filepath = os.path.join(JSONSearchResultLoader.BASE_DIR, JSONSearchResultLoader.FILENAME)
        
        # Load existing data if file exists
        existing_data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError as e:
                raise DirectoryLoadError(f"Failed to read existing results file: {str(e)}")
        
        # Initialize portal data if it doesn't exist
        if portal.value not in existing_data:
            existing_data[portal.value] = []
            
        # Add new result
        existing_data[portal.value].append(result.model_dump())
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, default=str)
        except IOError as e:
            raise DirectoryLoadError(f"Failed to save result for {portal.value}: {str(e)}")
    
    @staticmethod
    def save_search_results_for_portal(portal: Portal, results: List[SearchResult]) -> None:
        """Save multiple search results for a portal to JSON file"""
        os.makedirs(JSONSearchResultLoader.BASE_DIR, exist_ok=True)
        filepath = os.path.join(JSONSearchResultLoader.BASE_DIR, JSONSearchResultLoader.FILENAME)
        
        # Load existing data if file exists
        existing_data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError as e:
                raise DirectoryLoadError(f"Failed to read existing results file: {str(e)}")
        
        # Update data for this portal
        existing_data[portal.value] = [result.model_dump() for result in results]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, default=str)
        except IOError as e:
            raise DirectoryLoadError(f"Failed to save results for {portal.value}: {str(e)}")
    
    @staticmethod
    def save_search_results_for_portals(results_by_portal: Dict[Portal, List[SearchResult]]) -> None:
        """Save search results for multiple portals to JSON file"""
        os.makedirs(JSONSearchResultLoader.BASE_DIR, exist_ok=True)
        filepath = os.path.join(JSONSearchResultLoader.BASE_DIR, JSONSearchResultLoader.FILENAME)
        
        data = {
            portal.value: [result.model_dump() for result in results]
            for portal, results in results_by_portal.items()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except IOError as e:
            raise DirectoryLoadError(f"Failed to save results: {str(e)}")