class ScraperError(Exception):
    """Base exception for all scraper errors."""


class InvalidURLError(ScraperError):
    """The provided URL is not a valid Instagram post URL."""


class PostNotAccessibleError(ScraperError):
    """The post does not exist or is private."""
