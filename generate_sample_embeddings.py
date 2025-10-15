import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Create index directory if it doesn't exist
os.makedirs('index', exist_ok=True)

# Load the model
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load chunks
print("Loading chunks...")
with open('index/chunks.json', 'r') as f:
    chunks = json.load(f)

# Extract texts
texts = [chunk['text'] for chunk in chunks]

# Generate embeddings
print(f"Generating embeddings for {len(texts)} chunks...")
embeddings = model.encode(texts, show_progress_bar=True)

# Save embeddings
print("Saving embeddings...")
np.save('index/embeddings.npy', embeddings)

print(f"✅ Done! Generated embeddings with shape: {embeddings.shape}")
print(f"Saved to: index/embeddings.npy")