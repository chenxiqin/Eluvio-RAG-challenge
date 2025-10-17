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
4. neighbor-based context expansion：
The agent will add neighbors before and after the chosen K chunk to the context, the addded neighbor is bounded by the url page,
which means only chunks in the same website page as the current chunk will be considered. By doing this, I hope to maximize both the relatability and comprehensiveness of the context. 
choose neighbor expansion over whole page expansion:
理由：
# 1. 文档结构清晰，相邻 chunks 相关性高
# 2. 平衡速度和质量
# 3. 适度增加上下文，不会超限
5. add other related website/url besides the official company website








Testing:
Test potential Question asked for muti-perspective testing
1. basic question: main business/
2. technical questions:  Content Fabric/blockchain/security features
3. factual questions: time founded/ location/ industry partner
4. application questions: use case
5. out of scope question
6. little grammar/ unclear questions

## Tested out Edge case 
including Empty prompt, missing prompt field, very long prompt, very short prompt,special character, miss spelling name questions, essay like prompt, 

not work well:
Testing: Very long prompt
Server response: {
  "response": "Sorry, I don't have enough information to answer that question."
}
✓ Handled edge case successfully

Testing: Very short prompt
✗ Error: HTTPConnectionPool(host='localhost', port=5000): Read timed out. (read timeout=30)

Testing: typo question
Server response: {
  "response": "Sorry, I don't have enough information to answer that question."
}
✓ Handled edge case successfully

Testing: Special characters
Server response: {
  "response": "I'm not sure about the answer to that question right now. You can visit the company\u2019s website to learn more: https://eluv.io/"
}
✓ Handled edge case successfully

Testing: Essay like prompt
✗ Error: HTTPConnectionPool(host='localhost', port=5000): Read timed out. (read timeout=30)


## Test out question in different format


## Test question Answer Result:

{
      "question": "What is Eluvio's main business?",
      "answer": "Eluvio's main business is providing a next-generation platform for storing, delivering, and monetizing digital content. Specifically, it offers a Content Fabric Protocol that transforms the distribution and monetization of premium video and digital media by solving the generational problems of video over the Internet.",
      "time": 22.119462728500366
    },
    {
      "question": "What is the Eluvio Content Fabric?",
      "answer": "The Eluvio Content Fabric is a blockchain-controlled, decentralized system designed to manage and distribute content through a unified architecture, utilizing a built-in commerce and access control framework. It provides functions conventionally provided by separate services and software stacks, including content storage and retrieval, data storage and query APIs, and more.",
      "time": 18.269644021987915
    },
    {
      "question": "How does Eluvio use blockchain?",
      "answer": "Eluvio utilizes blockchain technology in its Content Fabric platform to provide a decentralized, global network for Internet video distribution, monetization, and content management. The blockchain design enables low latency, high-quality (4K) content distribution, as well as just-in-time streaming, without the need for file copies.\n\nUnder the control of blockchain smart contracts, video content is dynamically served from the source, ensuring authenticity and integrity. This approach also facilitates on-chain monetization, cross-chain authorization, and on-chain payments, providing a secure and transparent way to manage digital media content at scale.
         Key benefits of Eluvio's use of blockchain include:
              Low latency and high-quality content distribution
              Just-in-time streaming without file copies
              On-chain monetization and authorization
              Secure and transparent content management
      Overall, Eluvio's integration of blockchain technology enables the creation of a decentralized, global platform for Internet video distribution, providing transformational benefits for sports teams, leagues, brands, and content owners.",
      "time": 28.892870903015137
    },
    {
      "question": "What security features does Eluvio provide?",
      "answer": "Based on the provided context, Eluvio provides several security features, including:
      1. Blockchain-based smart contracts that control the distribution and monetization of video content, ensuring secure and transparent management.
      2. Decentralized architecture, which distributes content across a global network of nodes, reducing reliance on centralized systems and minimizing potential single-point failures.\n\nThese security features are designed to provide low latency, high-quality content distribution, and just-in-time streaming, while also enabling content monetization and authentication.
      
      Key takeaways:
      Eluvio's blockchain-based smart contracts ensure secure and transparent management of video content.
      The decentralized architecture of the Content Fabric reduces reliance on centralized systems and minimizes potential single-point failures.
      These security features are a key advantage of the Eluvio platform, providing a secure and reliable way to distribute and monetize digital media content.",
      "time": 26.339545249938965
    },
    {
      "question": "When was Eluvio founded?",
      "answer": "Eluvio was founded by Michelle Munson and Serban Simu, who are also the founders and inventors of Aspera (an Emmy Award-winning company acquired by IBM in 2014). The exact date of Eluvio's founding is not explicitly mentioned in the provided context. However, it can be inferred that Eluvio has received several notable awards and recognitions since its inception, including the NAB Product of the Year in 2024 and the prestigious Engineering Excellence Award by the Hollywood Professional Association.",
      "time": 33.26696968078613
    },
     ------> potential future improvemnet for this question

    {
      "question": "What are Eluvio's use cases?",
      "answer": "Eluvio's use cases include:
      Transforming the distribution and monetization of premium video and digital media through its next-generation content distribution and storage protocol, known as the Content Fabric.
      Solving the fundamental challenges of video delivery over the Internet, including distribution, monetization, provenance, and authenticity.
      Enabling sports teams, leagues, brands, and content owners to provide transformational streaming, monetization, and authenticity of any digital media content at scale.
      Supporting instant royalty settlements and payments to multiple parties directly on the blockchain for content owners.
      Powering new streaming platforms for fans, such as Bedrock's platform, which is launching for the 2025/26 season, and URC\u2019s partner, European Professional Club Rugby (EPCR), which will stream over 280 live games in over 90 countries.
      
      These use cases highlight Eluvio's focus on providing innovative solutions for the video content industry, including streaming, monetization, and distribution.",
      "time": 35.91717600822449
    },
    {
      "question": "Who invented the internet?",
      "answer": "Sorry, I don't have enough information to answer that question.",
      "time": 1.57840895652771
    },
    {
      "question": "Where is ELuvio at",
      "answer": "Eluvio is based in Berkeley, California.",
      "time": 17.51778817176819
    },
    {
      "question": "Which industries or partners use Eluvio?",
      "answer": "Eluvio partners with various industries and companies across multiple sectors, including:
      Sports teams, leagues, brands, and content owners
      Entertainment companies such as Amazon Studios/MGM, FOX, SONY Pictures, Telstra Broadcast Services/UEFA, United Rugby Championship, Warner Bros., WPALiveTV, WWE, and others.
      Music industry artists like Black Eyed Peas and Dolly Parton.
      Broadcasting and media organizations.
      These partners leverage Eluvio's Content Fabric to transform their streaming, monetization, and AI discovery of digital media content at scale.",
      "time": 27.889963150024414
    }


