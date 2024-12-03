import os
import time
import logging
import httpx
import pandas as pd
import random
import re
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
from datetime import datetime
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of keywords to monitor
KEYWORDS = [
    "BHAVYA",  
    "Bihar",
    "medixcel",
    "bihar digital health",
    "plus91",
    "Ayushman Bharat Health",
    "ABHA",
    "Hospital",
    "Health"
]   

# Global dictionary to track keyword counts
keyword_counts = defaultdict(int)

# Set to track URLs that failed to load
failed_urls = set()

# Set to track URLs that have already been processed
visited_urls = set()

# Set to store .onion links
found_onion_links = set()

# Single Tor connection check
tor_connected = False

def randomize_request_delay(min_delay=1, max_delay=5):
    """Randomize delay to reduce the risk of bot detection."""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def initialize_tor(bridges=None):
    """Set up Tor proxy with optional multiple bridges."""
    global tor_connected
    try:
        controller = Controller.from_port(port=9051)
        controller.authenticate(password="your_tor_password")  # Set your Tor password here
        if bridges:
            controller.set_conf("UseBridges", "1")
            controller.set_conf("Bridge", bridges)
        controller.signal(Signal.NEWNYM)
        logging.info("Tor connection initialized and IP rotated.")
        tor_connected = True
    except Exception as e:
        logging.error(f"Error connecting to Tor: {e}")
        tor_connected = False

def fetch_current_ip():
    """Fetch the current IP address through Tor."""
    proxies = {"http://": "socks5://127.0.0.1:9050", "https://": "socks5://127.0.0.1:9050"}
    with httpx.Client(proxies=proxies, timeout=10) as client:
        try:
            response = client.get("http://httpbin.org/ip")
            response.raise_for_status()
            return response.json().get("origin")
        except Exception as e:
            logging.error(f"Error fetching IP: {e}")
            return None

def check_tor_connection():
    """Check if Tor is connected."""
    try:
        current_ip = fetch_current_ip()
        if current_ip:
            logging.info(f"Tor is connected. Current IP: {current_ip}")
            return True
        else:
            logging.error("Tor is not connected.")
            return False
    except Exception as e:
        logging.error(f"Error checking Tor connection: {e}")
        return False

def load_target_urls(filename="url.txt"):
    """Load target URLs from a file."""
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    else:
        logging.error(f"{filename} not found.")
        return []

def is_onion_url(url):
    """Check if the URL is a .onion domain."""
    return urlparse(url).netloc.endswith(".onion")

def fetch_page(url):
    """Fetch a webpage using Tor."""
    proxies = {"http://": "socks5://127.0.0.1:9050", "https://": "socks5://127.0.0.1:9050"}
    with httpx.Client(proxies=proxies, timeout=30) as client:
        try:
            randomize_request_delay()  # Add delay before making the request
            response = client.get(url)
            response.raise_for_status()  # Raise error for bad status codes
            return response.text
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

def parse_page(html):
    """Parse the HTML content of a page."""
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_all_links(soup, base_url):
    """Extract all .onion links from the soup object, including pagination links."""
    links = set()

    # Extract .onion links
    for a_tag in soup.find_all('a', href=True):
        link = urljoin(base_url, a_tag['href'])
        if is_onion_url(link) and link not in visited_urls:
            links.add(link)
            visited_urls.add(link)  # Mark this .onion link as visited
            # Save .onion link during crawling
            with open(onion_file_path, "a") as f:
                f.write(link + "\n")

    return links

def search_keywords_on_page(soup):
    """Search for keywords using regex and return found keywords."""
    page_text = soup.get_text().lower()
    found_keywords = []
    not_found_keywords = []
    
    for keyword in KEYWORDS:
        if isinstance(keyword, re.Pattern):  # If regex pattern
            if re.search(keyword, page_text):
                found_keywords.append(keyword.pattern)  # Add regex pattern as found
            else:
                not_found_keywords.append(keyword.pattern)  # Add to not found list
        else:  # Plain text keyword
            if keyword.lower() in page_text:
                found_keywords.append(keyword)
            else:
                not_found_keywords.append(keyword)
                
    return found_keywords, not_found_keywords

def track_keyword_count(found_keywords):
    """Update keyword counts dynamically."""
    for keyword in found_keywords:
        keyword_counts[keyword] += 1

def prioritize_keywords(found_keywords):
    """Return keywords prioritized based on frequency or custom factors."""
    sorted_keywords = sorted(found_keywords, key=lambda kw: keyword_counts[kw], reverse=True)
    return sorted_keywords

def process_url(url, Link, depth=1, max_pages=5):
    """Process a single URL and return results, with link crawling depth and pagination handling."""
    results = []
    
    if depth <= 0 or max_pages <= 0:
        return results  # Stop if depth limit or page limit is reached

    if url in visited_urls:
        logging.info(f"Skipping already processed URL: {url}")
        return results  # Skip this URL if it's already been processed

    html = fetch_page(url)
    if html:
        visited_urls.add(url)
        soup = parse_page(html)
        found_keywords, not_found_keywords = search_keywords_on_page(soup)
        track_keyword_count(found_keywords)
        
        prioritized_keywords = prioritize_keywords(found_keywords)
        
        # Log keyword presence for this URL
        for keyword in prioritized_keywords:
            results.append({
                "Keyword": keyword,
                "Link": Link,
                "Findings": "Keyword found",
                "Link Response": "Success",
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Time": datetime.now().strftime("%H:%M:%S")
            })
        
        # Log keywords that were not found
        for keyword in not_found_keywords:
            results.append({
                "Keyword": keyword,
                "Link": Link,
                "Findings": "Keyword not found",
                "Link Response": "Success",
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Time": datetime.now().strftime("%H:%M:%S")
            })

        # Get all links from the page and process them
        all_links = get_all_links(soup, url)
        
        for link in all_links:
            logging.info(f"Crawling link: {link}")
            if link not in visited_urls:
                results.extend(process_url(link, Link, depth=depth-1, max_pages=max_pages-1))
    
    return results

def save_to_excel(results):
    """Save the results to an Excel file."""
    filename = f"monitoring_results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)
    logging.info(f"Saved results to {filename}")

def main():
    # Set up Tor connection
    initialize_tor()

    # Load URLs from file
    urls = load_target_urls()

    # Define path for storing .onion links
    global onion_file_path
    onion_file_path = f"found_links_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    
    # Start timing the process
    start_time = time.time()

    all_results = []

    # Use ThreadPoolExecutor to handle multiple URL crawls in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for url in urls:
            futures.append(executor.submit(process_url, url, url))

        for future in as_completed(futures):
            all_results.extend(future.result())

    save_to_excel(all_results)
    # End timing the process
    end_time = time.time()
    logging.info(f"Total time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
