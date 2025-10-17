# Eluvio-RAG

## Reproduce Workflow & Procedure

1) Download Ollama and model
ollama pull llama3.2:3b

2) Set up virtual environment and dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3) Generate embeddings from scraped data
python generate_sample_embeddings.py

4) Start the server
python server.py

5) Interact with the API (sample)
curl -X POST "http://localhost:5000/ask" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What does Eluvio do?"}'

## Potential Optimization

1) Multi-topic Question Handling

2) Cross-Encoder Reranker✅
Added a CrossEncoder model to rerank retrieved chunks.

3) Prompt Refinement✅

4) Neighbor-based Context Expansion✅
Extend the context by including neighboring chunks before and after the selected chunk—only within the same webpage. By doing this, I hope to maximize both the relatability and comprehensiveness of the context. 
Another way to do context expansion is a whole page expansion. The reason why I choose neighbor expansion over whole page expansion in this specific scenario is that:
      Preserves logical document flow — adjacent chunks tend to be more semantically related.

      Balances speed and accuracy.

      Expands context without exceeding token limits.

5) Add additional Data Sources
maybe some questions cannot answered solely by the company's webiste


# Testing
1) Multi-Perspective Question Types: 

Basic: main business

Technical: Content Fabric / blockchain / security features

Factual: founding time, location, industry partners

Application: use cases

Out-of-scope questions

Grammar unclear questions

2) Edge-Case Coverage: 

Empty prompt

Missing prompt field

Very long prompt (essay-like)

Very short prompt

Special characters

Misspellings of entity names

## Tests result on Edge case 
including Empty prompt, missing prompt field, very long prompt, very short prompt,special character, miss spelling name questions, essay like prompt

Very long prompt
Server response:
{
"response": "Sorry, I don't have enough information to answer that question."
}
✓ Handled edge case successfully

Very short prompt
✗ Error: HTTPConnectionPool(host='localhost', port=5000): Read timed out. (read timeout=30)

Typo / misspelling
Server response:
{
"response": "Sorry, I don't have enough information to answer that question."
}
✓ Handled edge case successfully

Special characters
Server response:
{
"response": "I'm not sure about the answer to that question right now. You can visit the company\u2019s website to learn more: https://eluv.io/
"
}
✓ Handled edge case successfully

Essay-like prompt
✗ Error: HTTPConnectionPool(host='localhost', port=5000): Read timed out. (read timeout=30)


## Test out question in different format


## Test question Answer Result:
What is Eluvio's main business?

{

"question": "What is Eluvio's main business?",

"answer": "Eluvio's main business is providing a next-generation platform for storing, delivering, and monetizing digital content. 

Specifically, it offers a Content Fabric Protocol that transforms the distribution and monetization of premium video and digital media by 

solving the generational problems of video over the Internet.",

"time": 22.119462728500366
}

What is the Eluvio Content Fabric?

{

"question": "What is the Eluvio Content Fabric?",

"answer": "The Eluvio Content Fabric is a blockchain-controlled, decentralized system designed to manage and distribute content through a 

unified architecture, utilizing a built-in commerce and access control framework. It provides functions conventionally provided by separate 

services and software stacks, including content storage and retrieval, data storage and query APIs, and more.",

"time": 18.269644021987915
}


How does Eluvio use blockchain?

{

"question": "How does Eluvio use blockchain?",

"answer": "Eluvio utilizes blockchain technology in its Content Fabric platform to provide a decentralized, global network for Internet 

video distribution, monetization, and content management. The blockchain design enables low latency, high-quality (4K) content 

distribution, as well as just-in-time streaming, without the need for file copies.\n\nUnder the control of blockchain smart contracts, 

video content is dynamically served from the source, ensuring authenticity and integrity. This approach also facilitates on-chain 

monetization, cross-chain authorization, and on-chain payments, providing a secure and transparent way to manage digital media content at 

scale.\n Key benefits of Eluvio's use of blockchain include:\n Low latency and high-quality content distribution\n Just-in-time streaming 
without file copies\n On-chain monetization and authorization\n Secure and transparent content management\n Overall, Eluvio's integration 
of blockchain technology enables the creation of a decentralized, global platform for Internet video distribution, providing 
transformational benefits for sports teams, leagues, brands, and content owners.",

"time": 28.892870903015137

}

What security features does Eluvio provide?
{
"question": "What security features does Eluvio provide?",
"answer": "Based on the provided context, Eluvio provides several security features, including:\n 1. Blockchain-based smart contracts that control the distribution and monetization of video content, ensuring secure and transparent management.\n 2. Decentralized architecture, which distributes content across a global network of nodes, reducing reliance on centralized systems and minimizing potential single-point failures.\n\nThese security features are designed to provide low latency, high-quality content distribution, and just-in-time streaming, while also enabling content monetization and authentication.\n \n Key takeaways:\n Eluvio's blockchain-based smart contracts ensure secure and transparent management of video content.\n The decentralized architecture of the Content Fabric reduces reliance on centralized systems and minimizes potential single-point failures.\n These security features are a key advantage of the Eluvio platform, providing a secure and reliable way to distribute and monetize digital media content.",
"time": 26.339545249938965
}

When was Eluvio founded?
{
"question": "When was Eluvio founded?",
"answer": "Eluvio was founded by Michelle Munson and Serban Simu, who are also the founders and inventors of Aspera (an Emmy Award-winning company acquired by IBM in 2014). The exact date of Eluvio's founding is not explicitly mentioned in the provided context. However, it can be inferred that Eluvio has received several notable awards and recognitions since its inception, including the NAB Product of the Year in 2024 and the prestigious Engineering Excellence Award by the Hollywood Professional Association.",
"time": 33.26696968078613
}

What are Eluvio's use cases?
{
"question": "What are Eluvio's use cases?",
"answer": "Eluvio's use cases include:\n Transforming the distribution and monetization of premium video and digital media through its next-generation content distribution and storage protocol, known as the Content Fabric.\n Solving the fundamental challenges of video delivery over the Internet, including distribution, monetization, provenance, and authenticity.\n Enabling sports teams, leagues, brands, and content owners to provide transformational streaming, monetization, and authenticity of any digital media content at scale.\n Supporting instant royalty settlements and payments to multiple parties directly on the blockchain for content owners.\n Powering new streaming platforms for fans, such as Bedrock's platform, which is launching for the 2025/26 season, and URC\u2019s partner, European Professional Club Rugby (EPCR), which will stream over 280 live games in over 90 countries.\n \n These use cases highlight Eluvio's focus on providing innovative solutions for the video content industry, including streaming, monetization, and distribution.",
"time": 35.91717600822449
}

Who invented the internet?
{
"question": "Who invented the internet?",
"answer": "Sorry, I don't have enough information to answer that question.",
"time": 1.57840895652771
}

Where is Eluvio located?
{
"question": "Where is ELuvio at",
"answer": "Eluvio is based in Berkeley, California.",
"time": 17.51778817176819
}

Which industries or partners use Eluvio?
{
"question": "Which industries or partners use Eluvio?",
"answer": "Eluvio partners with various industries and companies across multiple sectors, including:\n Sports teams, leagues, brands, and content owners\n Entertainment companies such as Amazon Studios/MGM, FOX, SONY Pictures, Telstra Broadcast Services/UEFA, United Rugby Championship, Warner Bros., WPALiveTV, WWE, and others.\n Music industry artists like Black Eyed Peas and Dolly Parton.\n Broadcasting and media organizations.\n These partners leverage Eluvio's Content Fabric to transform their streaming, monetization, and AI discovery of digital media content at scale.",
"time": 27.889963150024414
}

