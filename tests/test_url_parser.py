import pytest

from instagram_post_scraper.exceptions import InvalidURLError
from instagram_post_scraper.url_parser import extract_shortcode


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www.instagram.com/p/CxYzAbC123/", "CxYzAbC123"),
        ("https://instagram.com/p/CxYzAbC123/", "CxYzAbC123"),
        ("http://www.instagram.com/p/CxYzAbC123/", "CxYzAbC123"),
        ("instagram.com/p/CxYzAbC123/", "CxYzAbC123"),
        ("https://www.instagram.com/p/CxYzAbC123", "CxYzAbC123"),
        ("https://www.instagram.com/p/CxYzAbC123/?utm_source=ig", "CxYzAbC123"),
        ("https://www.instagram.com/reel/CxYzAbC123/", "CxYzAbC123"),
        ("https://www.instagram.com/reels/CxYzAbC123/", "CxYzAbC123"),
        ("https://www.instagram.com/tv/CxYzAbC123/", "CxYzAbC123"),
        ("https://www.instagram.com/p/Cx-Yz_123/", "Cx-Yz_123"),
    ],
)
def test_valid_urls(url: str, expected: str) -> None:
    assert extract_shortcode(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/p/CxYzAbC123/",
        "https://www.instagram.com/stories/user/123/",
        "https://www.instagram.com/user123/",
        "not a url at all",
        "",
    ],
)
def test_invalid_urls(url: str) -> None:
    with pytest.raises(InvalidURLError):
        extract_shortcode(url)
