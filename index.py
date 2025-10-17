import os
import json
import time
import subprocess
import shutil
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Configuration
BASE_URL = "https://eluv.io/"
DATA_DIR = "data/scraped"
INDEX_DIR = "index"
MAX_PAGES = 60  # Limit pages to crawl
SCROLL_PAUSE_TIME = 2  # Time to wait for content to load after scrolling

class SeleniumScraper:
    def __init__(self, base_url, headless=True):
        self.base_url = base_url
        self.visited = set()
        self.documents = []
        self.driver = None
        self.headless = headless

    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        print("Setting up Chrome WebDriver...")

        chrome_options = Options()
        if getattr(self, "headless", False):
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        service = Service("/opt/homebrew/bin/chromedriver")

        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ WebDriver ready!")
        
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("WebDriver closed")
    
    def scroll_page(self):
        """Scroll to bottom of page to load all dynamic content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(SCROLL_PAUSE_TIME)
            
            # Calculate new scroll height and compare with last height
            new_height = self.driver.execute_script("return document.body.scrollHeight") 
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def wait_for_page_load(self, timeout=10):
        """Wait for page to be fully loaded"""
        try:
            # Wait for body to be present
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # Wait for JavaScript to finish
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            ) 
            # Additional wait for dynamic content
            time.sleep(2)
            
            return True
        except TimeoutException:
            print(f"Timeout waiting for page to load")
            return False
    
    def is_valid_url(self, url):
        """Check if URL belongs to Eluvio domain"""
        parsed = urlparse(url)
        return parsed.netloc.endswith('eluv.io') and not url.endswith(('.pdf', '.jpg', '.png', '.svg', '.ico'))
    
    def extract_links(self):
        """Extract all links from current page"""
        links = set()
        try:
            # Find all anchor tags
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                try:
                    href = element.get_attribute("href")
                    if href:
                        full_url = urljoin(self.driver.current_url, href)
                        # Remove fragment identifiers
                        full_url = full_url.split('#')[0]
                        if self.is_valid_url(full_url):
                            links.add(full_url)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error extracting links: {e}")
        
        return links
    
    def scrape_page(self, url):
        """Scrape a single page using Selenium"""
        try:
            print(f"Scraping: {url}")
            
            self.driver.get(url)
            if not self.wait_for_page_load():
                return None
            
            self.scroll_page()
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
                tag.decompose()
            
            # process text
            text = soup.get_text(separator=' ', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = ' '.join(lines)
            text = ' '.join(text.split())  # Remove extra whitespace
            
            # Extract title
            try:
                title = self.driver.title
            except:
                title_tag = soup.find('title')
                title = title_tag.get_text() if title_tag else url
            
            # Only keep pages with text > 100
            if len(text) < 100:
                print(f"  Skipped (too short): {len(text)} chars")
                return None
            
            print(f"  Extracted: {len(text)} chars")     
            return {
                'url': url,
                'title': title,
                'content': text
            }
            
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
            return None
    
    def crawl(self, start_url, max_pages=MAX_PAGES):
        """Crawl pages starting from start_url"""
        self.setup_driver()
        
        to_visit = [start_url]
        
        try:
            with tqdm(total=max_pages, desc="Crawling pages") as pbar:
                while to_visit and len(self.visited) < max_pages:
                    url = to_visit.pop(0)
                    
                    # Skip if already visited
                    if url in self.visited:
                        continue
                    
                    self.visited.add(url)
                    doc = self.scrape_page(url)
                    
                    if doc:
                        self.documents.append(doc)
                        pbar.update(1)
                        
                        # Extract links from this page
                        links = self.extract_links()
                        
                        # Add new links to queue
                        for link in links:
                            if link not in self.visited and link not in to_visit:
                                to_visit.append(link)
                        
                        print(f"  Found {len(links)} links, queue size: {len(to_visit)}")
                    
                    # Small delay between requests
                    time.sleep(1)
                    
        finally:
            self.close_driver()
        
        return self.documents


class DocumentIndexer:
    def __init__(self):
        """Initialize with sentence transformer model"""
        print(f"Loading embedding model")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = []
        self.embeddings = None
        
    def chunk_document(self, doc, chunk_size=500):
        """Split document into overlapping chunks"""
        words = doc['content'].split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # if current chunk very short, append it to last chunk
            if len(chunk_words) < 50 and chunks:
                chunks[-1]['text'] += ' ' + chunk_text
                continue
            
            chunks.append({
                'text': chunk_text,
                'title': doc['title'],
                'url': doc['url'],
                'chunk_id': len(self.chunks) + len(chunks)
            })
        
        return chunks
    
    def build_index(self, documents):
        """Build vector index from documents"""
        print("Chunking documents...")
        for doc in tqdm(documents):
            doc_chunks = self.chunk_document(doc)
            self.chunks.extend(doc_chunks)
        
        print(f"Created {len(self.chunks)} chunks")
        
        if len(self.chunks) == 0:
            return
        
        # Generate embeddings
        print("Generating embeddings...")
        texts = [chunk['text'] for chunk in self.chunks]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        print(f"Embeddings shape: {self.embeddings.shape}")
        
    def save_index(self, index_dir):
        """Save index to disk"""
        os.makedirs(index_dir, exist_ok=True)
        
        # Save chunks
        with open(os.path.join(index_dir, 'chunks.json'), 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        
        # Save embeddings
        np.save(os.path.join(index_dir, 'embeddings.npy'), self.embeddings)
        print(f"Index saved to {index_dir}")

        # Save model name
        with open(os.path.join(index_dir, 'config.json'), 'w') as f:
            json.dump({'model_name': 'all-MiniLM-L6-v2'}, f)


def main():
    """Main indexing pipeline"""
    
    # Create directories
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    # Step 1: Scrape
    print("=" * 50)
    print("Step 1: Scraping Eluvio website (SPA)")
    print("=" * 50)
    print("Using Selenium to handle JavaScript-rendered content")
    print(f"Target: {BASE_URL}")
    print(f"Max pages: {MAX_PAGES}")
    print()
    
    scraper = SeleniumScraper(BASE_URL, headless=True)
    documents = scraper.crawl(BASE_URL, max_pages=MAX_PAGES)
    
    print(f"\nScraped {len(documents)} documents")
    
    if len(documents) == 0:
        print("ERROR: No documents scraped! Please check the website URL and your internet connection.")
        return
    
    # Save raw documents
    with open(os.path.join(DATA_DIR, 'documents.json'), 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    
    print(f"Raw documents saved to {DATA_DIR}/documents.json")
    
    # Step 2: Build Index
    print("\n" + "=" * 50)
    print("Step 2: Building search index")
    print("=" * 50)
    
    indexer = DocumentIndexer()
    indexer.build_index(documents)
    
    if len(indexer.chunks) == 0:
        print("ERROR: No chunks created! Cannot build index.")
        return
    
    indexer.save_index(INDEX_DIR)
    
    print("\n" + "=" * 50)
    print("✅ Indexing complete!")
    print("=" * 50)
    print(f"Documents scraped: {len(documents)}")
    print(f"Chunks created: {len(indexer.chunks)}")
    print(f"Index location: {INDEX_DIR}")
    print("\nData scarpe finished, can now start the server!")


if __name__ == "__main__":
    main()