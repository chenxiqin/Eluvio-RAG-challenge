

# chunk division and verctorization

from flask import Flask, request, jsonify
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
import ollama
import os

app = Flask(__name__)

class RAGAgent:
    def __init__(self, index_dir='index'):
        """Initialize RAG agent"""
        print("Loading RAG agent...")
       
        with open(os.path.join(index_dir, 'config.json'), 'r') as f:
            config = json.load(f)
        
        # Load embedding model
        self.model = SentenceTransformer(config['model_name'])
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        # Load chunks
        with open(os.path.join(index_dir, 'chunks.json'), 'r') as f:
            self.chunks = json.load(f)
        
        # Load embeddings
        self.embeddings = np.load(os.path.join(index_dir, 'embeddings.npy'))
        
        print(f"Loaded {len(self.chunks)} chunks")
        
        # LLM settings
        self.llm_model = "llama3.2:3b"
        
    def retrieve(self, query, top_k=5):
        """Retrieve most relevant chunks for query"""
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Cosine similarity
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        similarities = np.dot(embeddings_norm, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return top chunks with scores
        results = []
        for idx in top_indices:
            results.append({
                'chunk': self.chunks[idx],
                'score': float(similarities[idx])
            })
        
        return results
    
    def generate_response(self, query, retrieved_chunks):
        """Generate response using LLM with retrieved context"""
        
        # Build context from retrieved chunks
        context_parts = []
        for i, result in enumerate(retrieved_chunks, 1):
            chunk = result['chunk']
            context_parts.append(f"[Source {i}] {chunk['text'][:500]}")
        
        context = "\n\n".join(context_parts)
        
        # Prompting
        prompt = f"""You are an intelligent assistant working at Eluv.io—a company that provides a new, next-generation platform for storing, delivering, and monetizing digital content. Your current responsibility is to answer questions about Eluvio accurately and clearly based on the provided context.

            Context:
            {context}

            Question:
            {query}

            Instructions:
            1. Base your answer strictly on the context above. Do not make up or assume information.
                - If the context does not contain enough information, reply:
                "Sorry, I’m not sure about the answer to that question right now. You can visit the company’s website to learn more: https://eluv.io/"
            2. Adapt your tone naturally to the question type:
                - For **“how”** or **“why”** questions: provide a comprehensive, smooth, and logically organized explanation. Be as detailed as needed.
                - For **“what”** or **“who”** questions: keep the response factual, concise, and accurate—1–2 sentences if that fully answers the query.
                - For **“news”** or **“impact”** questions: include interpretation or analysis, and explain the significance or implications.
            3. When appropriate, highlight key takeaways, technical advantages, or the broader meaning of the information.
            4. Maintain a confident, professional, and objective tone throughout.

Answer:"""
        
        # Call Ollama
        try:
            response = ollama.generate(
                model=self.llm_model,
                prompt=prompt,
                options={
                    'temperature': 0.2,         # temperature:  fact-based to more nutural/divergent
                    'top_p': 0.9,
                    'top_k': 40,
                    'num_predict': 200          # length of words
                }
            )
            return response['response'].strip()
       
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "Sorry, I encountered an error generating the response."
    
    # optimization 1:  reranking
    def rerank_results(self, query, retrieved_chunks, top_k=5):
        pairs = [[query, c['chunk']['text']] for c in retrieved_chunks]
        scores = self.reranker.predict(pairs)
        for i, c in enumerate(retrieved_chunks):
            c['rerank_score'] = float(scores[i])
        retrieved_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
        return retrieved_chunks[:top_k]
    
    def ask(self, query):
        """Main RAG pipeline"""

        retrieved = self.retrieve(query, top_k=5)
        retrieved = self.rerank_results(query, retrieved)
        
        # debug
        for r in retrieved:
            print(f"[DEBUG] chunk {r['chunk']['chunk_id']} - {r['chunk']['title']} (score={r['score']:.3f})")
        
        # minimum similarity threshold : change from 0.3 to 0.1
        MIN_SIMILARITY = 0.1
        retrieved = [r for r in retrieved if r['score'] > MIN_SIMILARITY]
        
        if not retrieved:
            return "I don't have enough information to answer that question."
        
        response = self.generate_response(query, retrieved)
        return response
    
    def rerank_results(self, query, retrieved_chunks, top_k=5):
        pairs = [[query, c['chunk']['text']] for c in retrieved_chunks]
        scores = self.reranker.predict(pairs)
        for i, c in enumerate(retrieved_chunks):
            c['rerank_score'] = float(scores[i])
        retrieved_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
        return retrieved_chunks[:top_k]

# Initialize agent globally
agent = None

@app.before_request
def initialize_agent():
    """Initialize agent before first request"""
    global agent
    if agent is None:
        agent = RAGAgent()

@app.route('/ask', methods=['POST'])
def ask():
    """Handle question endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt field'}), 400
        
        query = data['prompt']
        response = agent.ask(query)
        
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return jsonify({
        'message': 'Eluvio RAG Agent',
        'endpoints': {
            '/ask': 'POST - Ask a question (JSON: {"prompt": "your question"})',
            '/health': 'GET - Health check'
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Eluvio RAG Server")
    print("=" * 50)
    print("Server running at: http://localhost:5000")
    print("Use POST /ask to query the agent")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
