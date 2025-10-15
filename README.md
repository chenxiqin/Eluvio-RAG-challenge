# eluvio-rag

Workflow & Procedure

1. Download ollama and get the ollama model we choose:
ollama pull llama3.2:3b

2. Build virtual environment and dependency installation: 
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Embedding generation from scraped data
python generate_sample_embeddings.py

4. Start main server
python server.py

5. Ask question and interact
sample format: 
curl -X POST "http://localhost:5000/ask" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What does Eluvio do?"}'





potential improvement:
1. covers multi-topic questions
2. Cross-Encoder✅
added a reranker using CrossEncoder
3. refine prompt --- can be more tailored later
4. 





Testing:
Potential Question asked for muti-perspective testing