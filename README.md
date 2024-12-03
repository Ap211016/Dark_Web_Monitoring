![License](https://img.shields.io/badge/license-MIT-blue.svg)

# Dark Web Scraping and Keyword Monitoring with Tor

This Python project allows you to crawl a list of URLs, monitor specific keywords, and save the results in an Excel file. It utilizes the Tor network for anonymous web scraping and searches for predefined keywords within the page content.

## Features

Crawl multiple URLs while maintaining anonymity through the Tor network.
   + Monitor specific keywords across the webpages.
   + Prioritize and track keyword frequency dynamically.
   +  Handle pagination and follow links within pages.
   +  Store found .onion URLs during the crawl.
   +  Export the results to an Excel file for further analysis.

## Prerequisite Libraries and Tools

Before running the code, make sure you have the following libraries and tools installed:
Libraries:

    httpx - For making HTTP requests through Tor.
    pandas - For saving the results to an Excel file.
    beautifulsoup4 - For parsing HTML content.
    stem - For controlling the Tor network connection.
    requests - For making regular HTTP requests.
    lxml (optional but recommended) - For faster parsing with BeautifulSoup.

## Software:
+ Tor: Make sure you have the Tor software installed and running locally. The code will connect to Tor using the default proxy settings (127.0.0.1:9050).


+ Python 3.x: Ensure Python 3 is installed on your system.

## Steps to Install from GitHub Repo


```bash
# Clone the repository:

git clone https://github.com/yourusername/apman.git
cd apman

# Create and activate a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  
# On Windows use `venv\Scripts\activate`
```

## Install the required libraries:

You can install all the dependencies listed in requirements.txt (if available) or install manually using:

```bash
    pip install httpx pandas beautifulsoup4 stem requests lxml
```
## Ensure Tor is running:

   Download and install Tor from https://www.torproject.org/download/.
   Start the Tor service, which will listen on 127.0.0.1:9050.

## Prepare Target URLs:

   Create a file named url.txt in the same directory as the script.
    List the URLs (one per line) you want to monitor.

## Run the script:

```bash
# Simply run the main.py script:

    python main.py
```
   ## View Results:

   After the script finishes running, it will generate an Excel file with the keyword search results. The file will be named something like monitoring_results_YYYY-MM-DD_HH-MM-SS.xlsx.

   ## Log Outputs:

   The script will log information about keyword matches, URLs being crawled, and errors, in the terminal.

## Additional Notes

   The script uses ThreadPoolExecutor for concurrent URL processing to speed up the crawling.
    It handles keyword matching using both plain text and regular expressions.
    You can modify the list of KEYWORDS in the script to tailor it to your needs.

## Contributing

If you'd like to contribute to this project, please fork the repository and create a pull request. We welcome improvements, bug fixes, and new features!
