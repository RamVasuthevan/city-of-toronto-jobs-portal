class DownloadError(Exception):
    """Raised when there's an error downloading content"""
    pass

class ParseError(Exception):
    """Raised when there's an error parsing content"""
    pass

class DirectoryStoreError(Exception):
    """Raised when there's an error storing content in a directory"""
    pass

class DirectoryLoadError(Exception):
    """Raised when there's an error loading content from a directory"""
    pass