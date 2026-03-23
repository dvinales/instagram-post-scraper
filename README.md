# instagram-post-scraper

CLI tool to extract image URLs or download images from public Instagram posts with carousel support.

## Installation

Requires Python >= 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync

# Or install globally
uv tool install .
```

## Usage

```bash
# Get image URLs as JSON
instagram-post-scraper "https://www.instagram.com/p/SHORTCODE/"

# Pretty-print output
instagram-post-scraper --pretty "https://www.instagram.com/p/SHORTCODE/"

# Download images to ./images/
instagram-post-scraper -d "https://www.instagram.com/p/SHORTCODE/"

# Download to a custom directory
instagram-post-scraper -d -o ./photos "https://www.instagram.com/p/SHORTCODE/"
```

If running from the project directory without installing globally, prefix with `uv run`:

```bash
uv run instagram-post-scraper --pretty "https://www.instagram.com/p/SHORTCODE/"
```

## Options

| Option | Description |
|---|---|
| `-d`, `--download` | Download images to disk |
| `-o`, `--output-dir PATH` | Directory for downloaded images (default: `./images`) |
| `--pretty` | Pretty-print JSON output |
| `--version` | Show version and exit |
| `--help` | Show help and exit |

## Output

### URL mode (default)

```json
{
  "shortcode": "ABC123",
  "description": "Post caption text",
  "images": [
    "https://scontent.cdninstagram.com/..."
  ]
}
```

### Download mode (`-d`)

```json
{
  "shortcode": "ABC123",
  "description": "Post caption text",
  "images": [
    "/absolute/path/to/images/ABC123_1.jpg",
    "/absolute/path/to/images/ABC123_2.jpg"
  ]
}
```

### Errors

Errors are output as JSON to stderr with distinct exit codes:

| Exit code | Meaning |
|---|---|
| 0 | Success |
| 1 | Scraper/network error |
| 2 | Invalid URL |
| 3 | Post not found or private |

```json
{"error": "Not a valid Instagram post URL: 'bad-url'. Expected format: https://www.instagram.com/p/SHORTCODE/"}
```

## Supported URL formats

- `https://www.instagram.com/p/SHORTCODE/`

## Notes

- Only public posts are supported (no login required).
- For carousel posts, only images are extracted; videos are filtered out.
- Instagram CDN URLs contain signed tokens that expire within hours. Use them promptly or use download mode.
- Instagram may rate-limit or block requests from datacenter/cloud IPs. For best results, run from a residential network.

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ -v --cov=instagram_post_scraper
```

## License

MIT
