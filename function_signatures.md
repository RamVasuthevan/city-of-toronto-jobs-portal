# Job Portal Function Signatures

## Core Types

```python
from typing import NewType, Dict, List
from enum import Enum
from abc import ABC, abstractmethodto

HTMLString = NewType('HTMLString', str)

class DownloadError(Exception): pass
class ParseError(Exception): pass

class SearchResult(SQLModel): pass
class Job(SQLModel): pass

class Portal(Enum):
    JOBS_AT_CITY = "jobsatcity"
    RECREATION = "recreation"

    @property
    def search_page_url(self) -> str: ...
    
    @property 
    def job_page_url_template(self) -> str
```

## Search Pages

### Extract

#### SearchPageProvider

```python
class SearchPageProvider(ABC):
    @staticmethod
    @abstractmethod
    def search_page(portal: Portal, page_number: int) -> HTMLString:
        """Fetch single search results page"""
        
    @staticmethod
    @abstractmethod
    def search_pages_for_portal(portal: Portal) -> List[HTMLString]:
        """Fetch all search pages for a portal"""
        
    @staticmethod
    def search_pages_for_portals(portals: List[Portal] = [portal.value for portal in Portal]) -> Dict[Portal, List[HTMLString]]:
        """Fetch all search pages for multiple portals"""

class DownloadJobPostProvider(SearchPageProvider):
    """Implementation that downloads pages from web"""
    pass

class DirectoryJobPostProvider(SearchPageProvider): 
    """Implementation that reads from filesystem"""
    pass
```

#### SearchPageStore

```python
class SearchPageStore(ABC):
    @staticmethod
    @abstractmethod
    def store_search_page(portal: Portal, page_number: int, content: HTMLString) -> None:
        """Store single search page"""
        
    @staticmethod
    @abstractmethod
    def store_search_pages_for_portal(portal: Portal, pages: List[HTMLString]) -> None:
        """Store multiple search pages"""
        
    @staticmethod
    @abstractmethod
    def store_search_pages_for_portals(pages_by_portal: Dict[Portal, List[HTMLString]]) -> None:
        """Store search pages for multiple portals"""

class DirectorySearchPageStore(SearchPageStore):
    """Implementation that stores to filesystem"""
    pass
```

### Transform

#### SearchPageParser 

```python
class SearchPageParser(ABC):
    @staticmethod
    @abstractmethod
    def parse_search_page(page: HTMLString) -> SearchResult:
        """Parse jobs from single search page"""
        
    @staticmethod
    @abstractmethod
    def parse_search_pages_for_portal(pages: List[HTMLString]) -> List[SearchResult]:
        """Parse jobs from multiple search pages"""
        
    @staticmethod
    @abstractmethod
    def parse_search_pages_for_portals(pages_by_portal: Dict[Portal, List[HTMLString]]) -> Dict[Portal, List[SearchResult]]:
        """Parse jobs from multiple portals"""

class SearchPageParser(SearchPageParser):
    """Implementation using BeautifulSoup"""
    pass
```

### Load

#### SearchResultLoader

```python
class SearchResultLoader(ABC):
    @staticmethod
    @abstractmethod
    def save_search_results_for_portal(portal: Portal, jobs: List[Job]) -> None:
        """Save search results for single portal"""
        
    @staticmethod
    @abstractmethod
    def save_search_results_for_portals(jobs_by_portal: Dict[Portal, List[Job]]) -> None:
        """Save search results for multiple portals"""

class JSONDirectorySearchResultLoader(SearchResultLoader):
    """Implementation using SQLModel"""
    pass
```

## Job Posts

### Extract

#### JobPostProvider

```python
class JobPostProvider(ABC):
    @staticmethod
    @abstractmethod
    def job_post(portal: Portal, job_id: str) -> HTMLString:
        """Fetch single job post"""
        
    @staticmethod
    @abstractmethod
    def job_posts_for_portal(portal: Portal, job_ids: List[str]) -> Dict[str, HTMLString]:
        """Fetch multiple job posts"""
        
    @staticmethod
    @abstractmethod
    def job_posts_for_portals(portals: List[Portal]) -> Dict[Portal, Dict[str, HTMLString]]:
        """Fetch job posts for multiple portals"""

class DownloadJobPostProvider(JobPostProvider):
    """Implementation that downloads from web"""
    pass

class FileJobPostProvider(JobPostProvider):
    """Implementation that reads from filesystem"""
    pass
```

#### JobPostStore

```python
class JobPostStore(ABC):
    @staticmethod
    @abstractmethod
    def store_job_post(portal: Portal, job_id: str, content: HTMLString) -> None:
        """Store single job post"""
        
    @staticmethod
    @abstractmethod
    def store_job_posts_for_portal(portal: Portal, posts: Dict[str, HTMLString]) -> None:
        """Store multiple job posts"""
        
    @staticmethod
    @abstractmethod
    def store_job_posts_for_portals(posts_by_portal: Dict[Portal, Dict[str, HTMLString]]) -> None:
        """Store job posts for multiple portals"""

class FileJobPostStore(JobPostStore):
    """Implementation that stores to filesystem"""
    pass
```

### Transform

#### JobPostParser

```python
class JobPostParser(ABC):
    @staticmethod
    @abstractmethod
    def parse_job_post(content: HTMLString) -> Job:
        """Parse single job post"""
        
    @staticmethod
    @abstractmethod
    def parse_job_posts_for_portal(posts: Dict[str, HTMLString]) -> List[Job]:
        """Parse multiple job posts"""
        
    @staticmethod
    @abstractmethod
    def parse_job_posts_for_portals(posts_by_portal: Dict[Portal, Dict[str, HTMLString]]) -> Dict[Portal, List[Job]]:
        """Parse job posts from multiple portals"""

class BeautifulSoupJobPostParser(JobPostParser):
    """Implementation using BeautifulSoup"""
    pass
```

### Load

#### JobPostLoader

```python
class JobLoader(ABC):
    @staticmethod
    @abstractmethod
    def save_job_post(portal: Portal, job: Job) -> None:
        """Save single job post"""
        
    @staticmethod
    @abstractmethod
    def save_job_posts_for_portal(portal: Portal, jobs: List[Job]) -> None:
        """Save multiple job posts"""
        
    @staticmethod
    @abstractmethod
    def save_job_posts_for_portals(jobs_by_portal: Dict[Portal, List[Job]]) -> None:
        """Save job posts for multiple portals"""

class JSONDirectoryJobLoader(JobLoader):
    """Implementation using SQLModel"""
    pass
```