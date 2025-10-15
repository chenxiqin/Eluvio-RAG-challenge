

# page crawling

import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from tqdm import tqdm


BASE_URL = "https://eluv.io/"
DATA_DIR = "data/scraped"
INDEX_DIR = "index"
MAX_PAGES = 50  

class EluvioScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.documents = []
        
    def is_valid_url(self, url):
        """Check if URL belongs to Eluvio domain"""
        parsed = urlparse(url)
        return parsed.netloc.endswith('eluv.io') and not url.endswith(('.pdf', '.jpg', '.png'))
    
    
    def scrape_page(self, url):
        """Scrape a single page"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style 
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            text = ' '.join(text.split())
            
            title = soup.find('title')
            title = title.get_text() if title else 'na'
            
            return {
                'url': url,
                'title': title,
                'content': text
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def crawl(self, start_url, max_pages=MAX_PAGES):
        """Recursively crawl pages"""
        to_visit = [start_url]
        
        with tqdm(total=max_pages, desc="Crawling pages") as pbar:
            while to_visit and len(self.visited) < max_pages:
                url = to_visit.pop(0)
                
                if url in self.visited:
                    continue
                
                self.visited.add(url)
                doc = self.scrape_page(url)
                
                #if doc and len(doc['content']) > 50:  # keep page > 50 word
                self.documents.append(doc)
                pbar.update(1)
                    
                # Find more links
                try:
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                        
                    for link in soup.find_all('a', href=True):
                        full_url = urljoin(url, link['href'])
                        if self.is_valid_url(full_url) and full_url not in self.visited:
                            to_visit.append(full_url)
                except:
                    pass
        
        return self.documents

class DocumentIndexer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize with sentence transformer model"""
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.chunks = []
        self.embeddings = None
        
    def chunk_document(self, doc, chunk_size=500, overlap=100):
        """Split document into overlapping chunks"""
        words = doc['content'].split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
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
        
        # Generate embeddings
        print("Generating embeddings...")
        texts = [chunk['text'] for chunk in self.chunks]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        print(f"Embeddings shape: {self.embeddings.shape}")
        
    def save_index(self, index_dir):
        """Save index to disk"""
        os.makedirs(index_dir, exist_ok=True)
        
        # Save chunks
        with open(os.path.join(index_dir, 'chunks.json'), 'w') as f:
            json.dump(self.chunks, f, indent=2)
        
        # Save embeddings
        np.save(os.path.join(index_dir, 'embeddings.npy'), self.embeddings)
        
        # Save model name
        with open(os.path.join(index_dir, 'config.json'), 'w') as f:
            json.dump({'model_name': self.model.model_name}, f)
        
        print(f"Index saved to {index_dir}")

def main():
    """Main indexing pipeline"""
    
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    
    print("Step 1: Scraping")
    
    scraper = EluvioScraper(BASE_URL)
    documents = scraper.crawl(BASE_URL)
    
    print(f"\nScraped {len(documents)} documents")
    
    # Save raw documents
    with open(os.path.join(DATA_DIR, 'documents.json'), 'w') as f:
        json.dump(documents, f, indent=2)
    
    # Step 2: Build Index
    
    print("Step 2: Building search index")
    
    
    indexer = DocumentIndexer()
    indexer.build_index(documents)
    indexer.save_index(INDEX_DIR)
    
    
    print("Indexing complete!")
   
    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(indexer.chunks)}")
    print(f"Index location: {INDEX_DIR}")

if __name__ == "__main__":
    main()