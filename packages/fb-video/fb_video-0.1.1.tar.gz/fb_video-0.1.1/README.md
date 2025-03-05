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
fb-scraper --url "https://www.facebook.com/watch/?v=971981951549911"
```
Or use it in Python:

```python
from facebook_scraper import FacebookVideoScraper

scraper = FacebookVideoScraper()
info = scraper.get_video_info("https://www.facebook.com/watch/?v=971981951549911")
print(info.to_dict())
```