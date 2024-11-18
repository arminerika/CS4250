#-------------------------------------------------------------------------
# AUTHOR: Armin Erika Polanco
# FILENAME: crawler.py
# SPECIFICATION: CPP CompSci Website Crawler
# FOR: CS 4250 - Assignment #3, Question 5
# TIME SPENT: 3 hours
#-----------------------------------------------------------*/

from urllib import request
from pymongo import MongoClient
from bs4 import BeautifulSoup

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["crawlerDB"]        # Database
collection = db["pages"]      # Collection for pages

# Function to retrieve and parse HTML
def retrieveHTML(url):
    try:
        with request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed retrieving {url}: {e}")
        return None

# Function to store page in MongoDB
def storePage(url, html):
    try:
        collection.insert_one({"url": url, "html": html})
        print(f"Stored: {url}")
    except Exception as e:
        print(f"Failed to store {url}: {e}")
    
# Function to parse URLs from HTML and normalize them
def parseHTML(url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Only consider HTML or SHTML links
            if href.endswith(('.html', '.shtml')):
                full_url = request.urljoin(url, href)
                links.add(full_url)
    return links

# Function to determine if the target page is found
def target_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1', {'class': 'cpp-h1'})
    # Check if permanent faculty found
    return h1 and h1.get_text(strip=True) == "Permanent Faculty"

# Frontier class to manage URL queue
class Frontier:
    def __init__(self, start_url):
        self.queue = [start_url]
        self.visited = set()

    def nextURL(self):
        return self.queue.pop(0) if self.queue else None

    def addURL(self, url):
        if url not in self.visited:
            self.queue.append(url)

    def markVisited(self, url):
        self.visited.add(url)

    def done(self):
        return not self.queue

# Main crawl() function
def crawl(frontier):
    while not frontier.done():
        url = frontier.nextURL()
        if url is None:
            break
        print(f"Crawling: {url}")

        # Retrieve HTML
        html = retrieveHTML(url)
        if not html:
            continue

        # Store page in MongoDB
        storePage(url, html)

        # Check if the target page is found
        if target_page(html):
            print(f"Target page found: {url}")
            return  # Stop the crawler

        # Parse and add new URLs to the frontier
        new_urls = parseHTML(url, html)
        for new_url in new_urls:
            frontier.addURL(new_url)

        # Mark URL as visited
        frontier.markVisited(url)

# Main and starting point
if __name__ == "__main__":
    start_url = "https://www.cpp.edu/sci/computer-science/"
    frontier = Frontier(start_url)
    crawl(frontier)
    print("Crawling finished.")