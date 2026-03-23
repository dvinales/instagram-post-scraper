import os
import urllib.request
from typing import Any

import instaloader

from instagram_post_scraper.exceptions import (
    PostNotAccessibleError,
    ScraperError,
)
from instagram_post_scraper.url_parser import extract_shortcode


def scrape_post(
    url: str,
    *,
    download: bool = False,
    output_dir: str = "./images",
) -> dict[str, Any]:
    """Scrape a public Instagram post and return image data as a dict."""
    shortcode = extract_shortcode(url)
    post = _fetch_post(shortcode)
    image_urls = _collect_image_urls(post)

    if not image_urls:
        raise ScraperError("No images found in this post (may be video-only).")

    description = post.caption or ""

    if download:
        local_paths = _download_images(image_urls, shortcode, output_dir)
        return {
            "shortcode": shortcode,
            "description": description,
            "images": local_paths,
        }

    return {
        "shortcode": shortcode,
        "description": description,
        "images": image_urls,
    }


def _fetch_post(shortcode: str) -> instaloader.Post:
    """Fetch a Post by shortcode using instaloader."""
    loader = instaloader.Instaloader()
    try:
        return instaloader.Post.from_shortcode(loader.context, shortcode)
    except instaloader.QueryReturnedNotFoundException:
        raise PostNotAccessibleError(
            f"Post not found: shortcode={shortcode!r}"
        )
    except instaloader.QueryReturnedForbiddenException:
        raise PostNotAccessibleError(
            f"Post is private or not accessible: shortcode={shortcode!r}"
        )
    except instaloader.QueryReturnedBadRequestException as e:
        raise ScraperError(f"Instagram rejected the request: {e}")
    except instaloader.ConnectionException as e:
        raise ScraperError(f"Network error fetching post: {e}")
    except instaloader.InstaloaderException as e:
        raise ScraperError(f"Failed to fetch post: {e}")


def _collect_image_urls(post: instaloader.Post) -> list[str]:
    """Extract image URLs from a Post, filtering out videos."""
    typename = post.typename

    if typename == "GraphImage":
        return [post.url]

    if typename == "GraphSidecar":
        return [
            node.display_url
            for node in post.get_sidecar_nodes()
            if not node.is_video
        ]

    return []


def _download_images(
    urls: list[str],
    shortcode: str,
    output_dir: str,
) -> list[str]:
    """Download images to output_dir. Returns list of absolute file paths."""
    os.makedirs(output_dir, exist_ok=True)

    paths: list[str] = []
    for i, img_url in enumerate(urls, start=1):
        suffix = f"_{i}" if len(urls) > 1 else ""
        filename = f"{shortcode}{suffix}.jpg"
        filepath = os.path.join(output_dir, filename)

        try:
            urllib.request.urlretrieve(img_url, filepath)
        except Exception as e:
            raise ScraperError(f"Failed to download image {i}: {e}")

        paths.append(os.path.abspath(filepath))

    return paths
