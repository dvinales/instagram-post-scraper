import json
import sys

import click

from instagram_post_scraper import __version__
from instagram_post_scraper.exceptions import (
    InvalidURLError,
    PostNotAccessibleError,
    ScraperError,
)
from instagram_post_scraper.scraper import scrape_post


@click.command()
@click.argument("url")
@click.option("-d", "--download", is_flag=True, default=False,
              help="Download images to disk.")
@click.option("-o", "--output-dir", type=click.Path(), default="./images",
              help="Directory for downloaded images (used with --download).")
@click.option("--pretty", is_flag=True, default=False,
              help="Pretty-print JSON output.")
@click.version_option(version=__version__)
def main(url: str, download: bool, output_dir: str, pretty: bool) -> None:
    """Extract image URLs or download images from a public Instagram post."""
    try:
        result = scrape_post(url, download=download, output_dir=output_dir)
    except InvalidURLError as e:
        _error_exit(str(e), code=2)
    except PostNotAccessibleError as e:
        _error_exit(str(e), code=3)
    except ScraperError as e:
        _error_exit(str(e), code=1)

    indent = 2 if pretty else None
    click.echo(json.dumps(result, indent=indent, ensure_ascii=False))


def _error_exit(message: str, code: int) -> None:
    error_payload = json.dumps({"error": message})
    click.echo(error_payload, err=True)
    sys.exit(code)
