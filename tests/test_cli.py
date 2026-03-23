import json
from unittest.mock import patch

from click.testing import CliRunner

from instagram_post_scraper.cli import main
from instagram_post_scraper.exceptions import (
    InvalidURLError,
    PostNotAccessibleError,
    ScraperError,
)


@patch("instagram_post_scraper.cli.scrape_post")
class TestCLI:
    def test_url_mode(self, mock_scrape):
        mock_scrape.return_value = {
            "shortcode": "ABC123",
            "description": "hello",
            "images": ["https://cdn.example.com/img.jpg"],
        }
        runner = CliRunner()
        result = runner.invoke(main, ["https://www.instagram.com/p/ABC123/"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["shortcode"] == "ABC123"
        assert data["images"] == ["https://cdn.example.com/img.jpg"]

    def test_pretty_output(self, mock_scrape):
        mock_scrape.return_value = {
            "shortcode": "ABC123",
            "description": "hello",
            "images": ["https://cdn.example.com/img.jpg"],
        }
        runner = CliRunner()
        result = runner.invoke(main, ["--pretty", "https://www.instagram.com/p/ABC123/"])
        assert result.exit_code == 0
        assert "  " in result.output  # indented

    def test_download_flag(self, mock_scrape):
        mock_scrape.return_value = {
            "shortcode": "ABC123",
            "description": "hello",
            "images": ["/tmp/ABC123.jpg"],
        }
        runner = CliRunner()
        result = runner.invoke(main, ["-d", "https://www.instagram.com/p/ABC123/"])
        assert result.exit_code == 0
        mock_scrape.assert_called_once_with(
            "https://www.instagram.com/p/ABC123/",
            download=True,
            output_dir="./images",
        )

    def test_output_dir_flag(self, mock_scrape):
        mock_scrape.return_value = {
            "shortcode": "ABC123",
            "description": "hello",
            "images": ["/custom/ABC123.jpg"],
        }
        runner = CliRunner()
        result = runner.invoke(
            main, ["-d", "-o", "/custom", "https://www.instagram.com/p/ABC123/"]
        )
        assert result.exit_code == 0
        mock_scrape.assert_called_once_with(
            "https://www.instagram.com/p/ABC123/",
            download=True,
            output_dir="/custom",
        )

    def test_invalid_url_exit_code_2(self, mock_scrape):
        mock_scrape.side_effect = InvalidURLError("bad url")
        runner = CliRunner()
        result = runner.invoke(main, ["garbage"])
        assert result.exit_code == 2

    def test_post_not_accessible_exit_code_3(self, mock_scrape):
        mock_scrape.side_effect = PostNotAccessibleError("private")
        runner = CliRunner()
        result = runner.invoke(main, ["https://www.instagram.com/p/ABC123/"])
        assert result.exit_code == 3

    def test_scraper_error_exit_code_1(self, mock_scrape):
        mock_scrape.side_effect = ScraperError("network fail")
        runner = CliRunner()
        result = runner.invoke(main, ["https://www.instagram.com/p/ABC123/"])
        assert result.exit_code == 1


class TestCLIHelp:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Extract image URLs" in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
