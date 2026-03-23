from unittest.mock import MagicMock, patch

import pytest

import instaloader
from instagram_post_scraper.exceptions import (
    PostNotAccessibleError,
    ScraperError,
)
from instagram_post_scraper.scraper import scrape_post


def _make_mock_post(typename, url=None, caption="test caption", sidecar_nodes=None):
    post = MagicMock(spec=instaloader.Post)
    post.typename = typename
    post.url = url or "https://cdn.example.com/img.jpg"
    post.caption = caption
    if sidecar_nodes is not None:
        post.get_sidecar_nodes.return_value = sidecar_nodes
    return post


def _make_sidecar_node(display_url, is_video=False):
    node = MagicMock()
    node.display_url = display_url
    node.is_video = is_video
    return node


class TestSingleImagePost:
    @patch("instagram_post_scraper.scraper._fetch_post")
    def test_returns_single_url(self, mock_fetch):
        mock_fetch.return_value = _make_mock_post(
            "GraphImage", url="https://cdn.example.com/photo.jpg"
        )
        result = scrape_post("https://www.instagram.com/p/ABC123/")
        assert result["shortcode"] == "ABC123"
        assert result["description"] == "test caption"
        assert result["images"] == ["https://cdn.example.com/photo.jpg"]


class TestCarouselPost:
    @patch("instagram_post_scraper.scraper._fetch_post")
    def test_returns_image_urls_only(self, mock_fetch):
        nodes = [
            _make_sidecar_node("https://cdn.example.com/1.jpg"),
            _make_sidecar_node("https://cdn.example.com/video.mp4", is_video=True),
            _make_sidecar_node("https://cdn.example.com/2.jpg"),
        ]
        mock_fetch.return_value = _make_mock_post("GraphSidecar", sidecar_nodes=nodes)
        result = scrape_post("https://www.instagram.com/p/ABC123/")
        assert result["images"] == [
            "https://cdn.example.com/1.jpg",
            "https://cdn.example.com/2.jpg",
        ]

    @patch("instagram_post_scraper.scraper._fetch_post")
    def test_all_videos_raises(self, mock_fetch):
        nodes = [
            _make_sidecar_node("https://cdn.example.com/v1.mp4", is_video=True),
            _make_sidecar_node("https://cdn.example.com/v2.mp4", is_video=True),
        ]
        mock_fetch.return_value = _make_mock_post("GraphSidecar", sidecar_nodes=nodes)
        with pytest.raises(ScraperError, match="No images found"):
            scrape_post("https://www.instagram.com/p/ABC123/")


class TestVideoPost:
    @patch("instagram_post_scraper.scraper._fetch_post")
    def test_raises_no_images(self, mock_fetch):
        mock_fetch.return_value = _make_mock_post("GraphVideo")
        with pytest.raises(ScraperError, match="No images found"):
            scrape_post("https://www.instagram.com/p/ABC123/")


class TestNoneCaption:
    @patch("instagram_post_scraper.scraper._fetch_post")
    def test_none_caption_becomes_empty_string(self, mock_fetch):
        mock_fetch.return_value = _make_mock_post("GraphImage", caption=None)
        result = scrape_post("https://www.instagram.com/p/ABC123/")
        assert result["description"] == ""


class TestErrorHandling:
    @patch("instagram_post_scraper.scraper.instaloader.Instaloader")
    @patch("instagram_post_scraper.scraper.instaloader.Post.from_shortcode")
    def test_not_found(self, mock_from_shortcode, _mock_loader):
        mock_from_shortcode.side_effect = instaloader.QueryReturnedNotFoundException("404")
        with pytest.raises(PostNotAccessibleError, match="Post not found"):
            scrape_post("https://www.instagram.com/p/ABC123/")

    @patch("instagram_post_scraper.scraper.instaloader.Instaloader")
    @patch("instagram_post_scraper.scraper.instaloader.Post.from_shortcode")
    def test_forbidden(self, mock_from_shortcode, _mock_loader):
        mock_from_shortcode.side_effect = instaloader.QueryReturnedForbiddenException("403")
        with pytest.raises(PostNotAccessibleError, match="private or not accessible"):
            scrape_post("https://www.instagram.com/p/ABC123/")

    @patch("instagram_post_scraper.scraper.instaloader.Instaloader")
    @patch("instagram_post_scraper.scraper.instaloader.Post.from_shortcode")
    def test_bad_request(self, mock_from_shortcode, _mock_loader):
        mock_from_shortcode.side_effect = instaloader.QueryReturnedBadRequestException("400")
        with pytest.raises(ScraperError, match="rejected the request"):
            scrape_post("https://www.instagram.com/p/ABC123/")

    @patch("instagram_post_scraper.scraper.instaloader.Instaloader")
    @patch("instagram_post_scraper.scraper.instaloader.Post.from_shortcode")
    def test_connection_error(self, mock_from_shortcode, _mock_loader):
        mock_from_shortcode.side_effect = instaloader.ConnectionException("timeout")
        with pytest.raises(ScraperError, match="Network error"):
            scrape_post("https://www.instagram.com/p/ABC123/")


class TestDownloadMode:
    @patch("instagram_post_scraper.scraper.urllib.request.urlretrieve")
    @patch("instagram_post_scraper.scraper._fetch_post")
    def test_downloads_and_returns_paths(self, mock_fetch, mock_urlretrieve, tmp_path):
        mock_fetch.return_value = _make_mock_post(
            "GraphImage", url="https://cdn.example.com/img.jpg"
        )
        result = scrape_post(
            "https://www.instagram.com/p/ABC123/",
            download=True,
            output_dir=str(tmp_path),
        )
        assert len(result["images"]) == 1
        assert result["images"][0].endswith("ABC123.jpg")
        mock_urlretrieve.assert_called_once()

    @patch("instagram_post_scraper.scraper.urllib.request.urlretrieve")
    @patch("instagram_post_scraper.scraper._fetch_post")
    def test_carousel_download_naming(self, mock_fetch, mock_urlretrieve, tmp_path):
        nodes = [
            _make_sidecar_node("https://cdn.example.com/1.jpg"),
            _make_sidecar_node("https://cdn.example.com/2.jpg"),
        ]
        mock_fetch.return_value = _make_mock_post("GraphSidecar", sidecar_nodes=nodes)
        result = scrape_post(
            "https://www.instagram.com/p/ABC123/",
            download=True,
            output_dir=str(tmp_path),
        )
        assert len(result["images"]) == 2
        assert result["images"][0].endswith("ABC123_1.jpg")
        assert result["images"][1].endswith("ABC123_2.jpg")
