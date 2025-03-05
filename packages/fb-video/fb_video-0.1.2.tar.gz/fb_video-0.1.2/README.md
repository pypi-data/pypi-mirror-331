# Facebook Video Scraper by Kehem IT

A Python package to scrape video information from Facebook.

## Installation

Install the package from PyPI:

```bash
pip install fb-video
```
## Usage
Run the scraper from the command line:

```bash 
from fb_video import FBVideoScraper

scraper = FBVideoScraper()
info = scraper.get_video_info("https://www.facebook.com/video_url")
print(info)
```
Or use it in Python:

```python
from facebook_scraper import FacebookVideoScraper

scraper = FacebookVideoScraper()
info = scraper.get_video_info("https://www.facebook.com/watch/?v=971981951549911")
print(info.to_dict())
```

#### `LICENSE`
No change needed here. Use the MIT license (or your preferred license) as before.

#### `pyproject.toml`
Update the `name` field to `fb_video`:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fb_video"  # Updated package name
version = "0.1.0"
authors = [
    { name = "Kehem IT", email = "support@kehem.com" },
]
description = "A Python package to scrape video information from Facebook URLs"
readme = "README.md"
requires-python = ">=3.7"
dependencies = [
    "requests>=2.28.0",
]
license = { file = "LICENSE" }
keywords = ["facebook", "video", "scraper"]

[project.urls]
"Homepage" = "https://github.com/yourusername/fb_video"
"Source" = "https://github.com/yourusername/fb_video"

[project.scripts]
fb-video = "fb_video.scraper:main"  # CLI command (fb-video)