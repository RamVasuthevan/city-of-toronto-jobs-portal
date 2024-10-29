class DownloadError(Exception):
    """Raised when there's an error downloading content"""


class ParseError(Exception):
    """Raised when there's an error parsing content"""


class DirectoryStoreError(Exception):
    """Raised when there's an error storing content in a directory"""


class DirectoryLoadError(Exception):
    """Raised when there's an error loading content from a directory"""
