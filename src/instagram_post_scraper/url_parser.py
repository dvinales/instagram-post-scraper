import re

from instagram_post_scraper.exceptions import InvalidURLError

_SHORTCODE_RE = re.compile(
    r"(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)"
)


def extract_shortcode(url: str) -> str:
    """Extract the shortcode from an Instagram post/reel URL.

    Raises InvalidURLError if the URL does not match expected patterns.
    """
    match = _SHORTCODE_RE.search(url)
    if not match:
        raise InvalidURLError(
            f"Not a valid Instagram post URL: {url!r}. "
            "Expected format: https://www.instagram.com/p/SHORTCODE/"
        )
    return match.group(1)
