"""
This code is used to collect the links in then given webpage and store them in a text file for further processing
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
START_URL = "https://docs.atlan.com/"
visited = set()
to_visit = [START_URL]
all_urls_ = set()
while to_visit:
    url = to_visit.pop(0)
    if url in visited or ".pdf" in url or "#" in url:
        continue
    try:
        resp = requests.get(url, timeout=10)
        visited.add(url)
        all_urls_.add(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            if urlparse(full_url).netloc == urlparse(START_URL).netloc and full_url not in visited:
                to_visit.append(full_url)
    except Exception as e:
        print(f"Error visiting {url}: {e}")

print(f"Discovered {len(all_urls_)} documentation URLs.")
