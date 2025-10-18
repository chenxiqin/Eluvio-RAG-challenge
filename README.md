# Eluvio-RAG Agent

A lightweight RAG system that answers questions about Eluv.io by scraping their public website, indexing the content locally, storing embeddings in a vector database and serving responses through a Flask API.

## 🚀Quick Start
### Prerequisites

1. Install Ollama and download the model:
`ollama pull llama3.2:3b`

2. Set up Python environment:
`python3 -m venv venv
source venv/bin/activate 
`
3. Install all dependencies with:
`bashpip install -r requirements.txt`


### Running the Agent
`# 1. Build the search index from scraped data
python index.py

# 2. Start the server
python server.py

# 3. Ask questions via the API
curl -X POST "http://localhost:5000/ask" \
     -H "Content-Type: application/json" \
     -d '{"prompt":"What does Eluvio do?"}'
`

## 💡 My Approach
### Core Strategy
I focused on building a system that accurately and comprehensively scrapes the data, smartly splits into chunks, and balances accuracy with response speed. The pipeline follows these steps:
1.**Scraping Data**- Use Selenium WebDriver to handle JavaScript-rendered content on eluv.io official websites. Use an algorithm to extrtact and store all links from the current page, and visit sequentially without repeatation for information integrity. The maximum page to scrape is set to 60 pages.
- scraped 56 pages, 4691 characters in total
2.**Chunking** - Split documents into 500-word chunks with smart merging for short fragments (to previous chunk)
3. **Embedding** - Generate vector embeddings using all-MiniLM-L6-v2 from sentence-transformers
4. **Retrieval** - Find top-5 relevant chunks using cosine similarity (threshold: 0.3)  
5. **Reranking** - Apply CrossEncoder (ms-marco-MiniLM-L-6-v2) to re-score and reorder results for enhanced context relevance
6. **Context Expansion** - Include neighboring chunks (before and after the current chunk) from the **same webpage** to the context to preserve the flow
7. **Generatio**n - Generate answers using Ollama's llama3.2:3b with temperature 0.2



### Key Optimization

#### ✅Dynamic Content Handling with Selenium
Eluv.io is a single-page application with lots of JavaScript-rendered content. Regular HTTP requests wouldn't capture the full content, so I used Selenium WebDriver with:
- Automatic page scrolling to trigger content
- Wait conditions for JavaScript execution to complete
- Headless Chrome for efficient scraping without GUI overhead

This approach captured 56 pages with rich, dynamically-loaded content that static scrapers might be missing.

#### ✅Smart Chunking 
Instead of fixed-size chunks, I implemented adaptive chunking:

- Base chunk size: 500 words
- Automatic merging: chunks shorter than 50 words get appended to the previous chunk
- Metadata preservation:  Each chunk stores chunk_id, url, and title, enabling fast neighbor lookup via a pre-built url_to_chunks mapping sorted by chunk_id, which helps with later functionality of preserving context relevance. This prevents fragmented information and maintains semantic coherence.


#### ✅Cross-Encoder Reranking
After initial retrieval, I added a reranking step using a CrossEncoder model (ms-marco-MiniLM-L-6-v2). This improved answer quality by:

- Evaluating query-chunk relevance more accurately than cosine similarity alone
- Distinguishing between superficially similar chunks and truly relevant ones
- Re-scoring and reordering the top-5 results before context expansion

The reranking step added ~2-3 seconds but dramatically improved answer precision.

#### ✅Neighbor-Based Context Expansion
Instead of retrieving isolated chunks, I include 1 neighboring chunk before and after each retrieved chunk (within the same webpage). This preserves the logical flow of information without hitting token limits.
Before choosing the neighbor-based startegy, I'm also considering a full-page expansion strategy. The reason why I choose neighbor expansion over full-page expansion is mainly:

- Adjacent chunks within the same web page are semantically related and maintain document narrative flow 
- Keeps token usage reasonable (typically 9-10 chunks in total after expansion)
- Maintains document structure without overwhelming the LLM context window

I built a URL-to-chunks mapping that allows fast neighbor lookup by chunk_id, ensuring we only expand within the same source page.


#### ✅Adaptive Prompt Engineering 
I crafted a detailed system prompt that:

- Explicitly instructs the model to admit uncertainty when information is lacking
- Adapts response style based on question type (how/why → detailed and descriptive; what/who → simple and concise answer)
- Sets temperature to 0.2 for more factual, deterministic responses, limits generation to 250 tokens to maintain a balance in preserving answer comprehensiveness and not rambling
- Tone: Maintain a confident, professional, and objective tone throughout
- Ask the model to highlight key takeaways, technical advantages, or the broader meaning of the information when appropriate

The prompt also includes a fallback message directing users to eluv.io when information isn't available.



### What I Tried (and Learned)

Static scraping first - Initially I tried requests + BeautifulSoup, but captured almost no content from the SPA (only one chunk "eluv.io" and nothing else). Switching to Selenium was essential and makes the whole data scraping process comprehensive and success.
Similarity threshold tuning - Started with 0.1, but getting too many irrelevant chunks. Settled on 0.3 as a good balance between recall and precision. 
Chunk size experiments - Tested 300, 500, and 700-word chunks. 500 words hit the balance between generation speed and meaningful precise retrieval. 
Timeout issues - Sometimes very long or very short prompts caused timeouts during LLM generation. I switched the timeout control from the initial 30 s to 50s, or some of the prompts are getting the response. The issue seems related to Ollama's processing time. Still investigating optimal timeout configurations.
Factual gaps - Some questions like "When was Eluvio founded?" return partial answers about founder but was not able to give the correct answer for the year because exact dates aren't prominently featured on the website. Could expand to other potential resources like LinkedIn, Crunchbase, or press releases for more comprehensive factual coverage.


###🧪 Testing Results
#### Sample Questions & Responses
Q: What is Eluvio's main business? (test basic question)
`Eluvio's main business is providing a next-generation platform for storing, delivering, and monetizing digital content. 
Specifically, it offers a Content Fabric Protocol that transforms the distribution and monetization of premium video and digital media by 
solving the generational problems of video over the Internet.`
Response time: ~22s

Q: How does Eluvio use blockchain? (test technical question)
`Eluvio utilizes blockchain technology in its Content Fabric platform to provide a decentralized, global network for Internet 
video distribution, monetization, and content management. The blockchain design enables low latency, high-quality (4K) content 
distribution, as well as just-in-time streaming, without the need for file copies.\n\nUnder the control of blockchain smart contracts, 
video content is dynamically served from the source, ensuring authenticity and integrity. This approach also facilitates on-chain 
monetization, cross-chain authorization, and on-chain payments, providing a secure and transparent way to manage digital media content at 
scale.
Key benefits of Eluvio's use of blockchain include:
              Low latency and high-quality content distribution
              Just-in-time streaming without file copies
              On-chain monetization and authorization
              Secure and transparent content management
Overall, Eluvio's integration of blockchain technology enables the creation of a decentralized, global platform for Internet video 
distribution, providing transformational benefits for sports teams, leagues, brands, and content owners.`
Response time: ~28s

Q: What security features does Eluvio provide?
`Based on the provided context, Eluvio provides several security features, including:
      1. Blockchain-based smart contracts that control the distribution and monetization of video content, ensuring secure and transparent 
      management.
      2. Decentralized architecture, which distributes content across a global network of nodes, reducing reliance on centralized systems 
      and minimizing potential single-point failures.\n\nThese security features are designed to provide low latency, high-quality content 
      distribution, and just-in-time streaming, while also enabling content monetization and authentication.
      
      Key takeaways:
      Eluvio's blockchain-based smart contracts ensure secure and transparent management of video content.
      The decentralized architecture of the Content Fabric reduces reliance on centralized systems and minimizes potential single-point 
      failures.
      These security features are a key advantage of the Eluvio platform, providing a secure and reliable way to distribute and monetize 
      digital media content.`
Response time: ~26s

Q: Where is ELuvio at? (Test random factual question)
`Eluvio is based in Berkeley, California.`
Response time: ~17s

Q: Which industries or partners use Eluvio?
`Eluvio partners with various industries and companies across multiple sectors, including:
      Sports teams, leagues, brands, and content owners  
      Entertainment companies such as Amazon Studios/MGM, FOX, SONY Pictures, Telstra Broadcast Services/UEFA, United Rugby Championship, 
      Warner Bros., WPALiveTV, WWE, and others.
      Music industry artists like Black Eyed Peas and Dolly Parton.
      Broadcasting and media organizations.
      These partners leverage Eluvio's Content Fabric to transform their streaming, monetization, and AI discovery of digital media content 
      at scale.`
Response time: ~26s


#### Edge Test Cases
I systematically tested edge cases to identify failure modes:
- Empty prompt
` {"error": "Prompt cannot be empty"}
 ✅Validation catches it`
- Missing prompt field
  `{"error": "Missing prompt field"}
✅Proper error handling`
- Very long prompt
  `{"response": "Sorry, I don't have enough..."}
  ⚠️Sometimes returns safe fallback, sometimes times out`
- Very short prompt (1-2 words)
 ` Timeout after 30s❌Needs investigation`
- Special characters
  `{"response": "Sorry, I don't have enough information..."} ✅not run into problems but responded as not enough information`
- Misspellings
   `{"response": "Sorry, I don't have enough information..."} ✅not run into problems but responded as not enough information`
- Essay-like prompt (paragraph)
  `Timeout after 30s❌Needs investigation`


### 🔮 Future Improvements
**Expand data sources** - Scrape Eluvio's technical docs, blog posts, press releases, or GitHub repos for more comprehensive coverage of technical details and company facts
**Optimize timeout handling** - Implement dynamic timeout adjustment based on prompt length and add request queuing for better handling of edge cases
**Edge test case handling** - Add a more comprehensive edge case handling strategy to deal with cases like **special character/miss spelling/ essay like prompt/ grammar mistake prompt etc. **
Query classification - Automatically detect question type (factual/technical/comparison) and route to specialized retrieval strategies or prompts
**Evaluation framework** - Currently the test file is only evaluating the quality of reponses by matching the keywords with the response string. Maybe in the future build better and more comprehensive test suite with ground-truth Q&A pairs to measure retrieval quality and answer accuracy quantitatively


### 📁 Project Structure
`.
├── index.py                 # Selenium scraper + embedding generation
├── server.py                # Flask API with RAG pipeline
├── requirements.txt         # Python dependencies
├── data/
│   └── scraped/
│       └── documents.json   # Raw scraped content
├── index/
│   ├── chunks.json          # Processed text chunks with metadata
│   ├── embeddings.npy       # Vector embeddings (numpy array)
│   └── config.json          # Model configuration
└── README.md                # This file`



