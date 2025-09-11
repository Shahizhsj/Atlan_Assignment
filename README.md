# Atlan Support Ticket Classification System

An AI-powered system that automatically classifies support tickets and provides responses using RAG (Retrieval-Augmented Generation) for Atlan's data catalog platform.

## Features

- **Automatic Ticket Classification**
  - Topic categorization (How-to, Product, Connector, Feedback, Bug)
  - Sentiment analysis (Frustrated, Curious, Angry, Neutral)
  - Priority assignment (P0/High, P1/Medium, P2/Low)

- **RAG-Based Response Generation**
  - Automated responses for How-to, Product, Best practices, API/SDK, and SSO queries
  - Context-aware answers from documentation
  - Source linking to relevant documentation

- **Dual Interface**
  - Bulk classification for multiple tickets
  - Interactive chatbot for single queries

## Technology Stack

- LangChain for LLM orchestration
- Google's Gemini Pro for classification
- FAISS for vector storage
- HuggingFace embeddings (all-MiniLM-L6-v2)
- Streamlit for the user interface

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd atlan-support-classifier
```

2. Create and activate conda environment:
```bash
conda env create -f environment.yml
conda activate atlan-classifier
```

3. Set up environment variables in `.env`:
```plaintext
GOOGLE_API_KEY=your_google_api_key_here
```

4. Initialize FAISS vector store:
```bash
python webcrawlers/WebCrawler_1.py  # Collect documentation URLs
python create_vectorstore.py        # Create FAISS index
```

5. Run the application:
```bash
streamlit run main.py
```

## Project Structure

```
atlan-support-classifier/
├── main.py                 # Streamlit application
├── ticket_classifer.py     # Ticket classification logic
├── ai_agent.py            # RAG-based response generation
├── webcrawlers/           # Documentation crawling utilities
│   └── WebCrawler_1.py    # URL collector
├── environment.yml        # Conda environment file
├── .env                   # Environment variables
└── faiss_store/          # Vector store for RAG
```

## Usage

### Bulk Classification
1. Prepare a JSON file with tickets in the format:
```json
[
    {
        "id": "1",
        "body": "ticket text here"
    }
]
```
2. Load the file through the bulk classification tab
3. View classification results and statistics

### Chatbot Interface
1. Enter your question in the chatbot tab
2. Receive classified response with:
   - Topic, Sentiment, and Priority
   - Detailed response (for supported topics)
   - Source documentation links

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Atlan Documentation
- LangChain Framework
- Google Gemini Pro
- FAISS by Facebook Research