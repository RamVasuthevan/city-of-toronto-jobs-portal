from search_pages.extract.provider import DirectorySearchPageProvider, DownloadSearchPageProvider, SearchPageProvider
from search_pages.extract.store import DirectorySearchPageStore
from search_pages.load.loader import JSONSearchResultLoader
from search_pages.transform.parser import DefaultSearchPageParser


def process_search_pages_workflow(search_page_provider: SearchPageProvider) -> None:
    """Process search pages from either website download or directory read based on provider"""
    print("Starting search pages processing workflow...")

    pages_by_portal = search_page_provider.search_pages_for_portals()

    if isinstance(search_page_provider, DownloadSearchPageProvider):
        DirectorySearchPageStore.store_search_pages_for_portals(pages_by_portal)
        print("Stored search pages to directory")

    print(pages_by_portal)

    results_by_portal = DefaultSearchPageParser.parse_search_pages_for_portals(pages_by_portal)
    print("Parsed search results")

    JSONSearchResultLoader.save_search_results_for_portals(results_by_portal)
    print("Saved search results to JSON")


if __name__ == "__main__":
    try:
        process_search_pages_workflow(DirectorySearchPageProvider())
    except Exception as e:
        print(f"Workflow failed: {str(e)}")
