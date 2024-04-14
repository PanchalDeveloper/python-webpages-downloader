import os
import json
import re
import requests
import concurrent.futures
import asyncio
import validators
from concurrent import futures
from bs4 import BeautifulSoup

## Save Options
DOWNLOAD_FOLDER = 'documentation-pages'
URLS_JSON_FILE = 'urls.json'

# Additional  Options
FILES_PREFIX=''
FILES_SUFFIX=''

def scrape_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.prettify()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_html_to_file(url, html_content):
    if not validators.url(url):
        print(f'\'{url}\' is not a URL')
        return
        
    if url.endswith('/'):
        filename = os.path.join(DOWNLOAD_FOLDER, f"{FILES_PREFIX}{url.split('/')[-2]}{FILES_SUFFIX}")
    else:
        filename = os.path.join(DOWNLOAD_FOLDER, f"{FILES_PREFIX}{url.split('/')[-1]}{FILES_SUFFIX}")
        
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"Saved {url} to {filename}")

def main(urls:list[str]):
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    # Using concurrent.futures for parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_url, url) for url in urls]
        for future, url in zip(concurrent.futures.as_completed(futures), urls):
            html_content = future.result()
            if html_content:
                save_html_to_file(url, html_content)

    # Using asyncio for asynchronous execution
    async def scrape_async(url):
        html_content = await loop.run_in_executor(None, scrape_url, url)
        if html_content:
            save_html_to_file(url, html_content)

    loop = asyncio.get_event_loop()
    tasks = [scrape_async(url) for url in urls]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    with open(URLS_JSON_FILE) as file:
        urls = json.load(file)
        main(urls)