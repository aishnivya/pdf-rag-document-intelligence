
# End-to-End Retrieval-Augmented Generation (RAG) System for PDF Document Intelligence

**Tech Stack:** Python 3.12 | Google Gemini | Semantic Embeddings | Scikit-learn | Streamlit

## Project Overview

An end-to-end **Retrieval-Augmented Generation (RAG)** application designed to enable users to upload PDF documents and ask natural-language questions about their content.

The system integrates **document ingestion, semantic text chunking, vector embedding generation, cosine similarity search, Top-K retrieval, and Large Language Model (LLM) inference** to generate context-aware answers grounded in the retrieved PDF content.

The application uses **Google Gemini** for embedding generation and LLM-based question answering, with **Streamlit** providing an interactive user interface.

## System Architecture

```text
                     PDF Document
                           |
                           v
                   PDF Text Extraction
                           |
                           v
                Sentence-Aware Text Chunking
                           |
                           v
                  Gemini Embeddings
                           |
                           v
                 Cached Chunk Vectors
                           |
                           |
User Question ------------+
       |
       v
Question Embedding
       |
       v
Cosine Similarity Search
       |
       v
Top-3 Relevant PDF Chunks
       |
       v
Context-Augmented Prompt
       |
       v
Google Gemini LLM
       |
       v
Generated Answer
       |
       v
Streamlit User Interface
```

## Key Features

- **PDF Document Processing:** Extracts readable text from uploaded PDF documents using PyPDF.
- **Sentence-Aware Text Chunking:** Splits document content into overlapping chunks while preserving sentence boundaries.
- **Vector Embedding Generation:** Converts document chunks and user queries into semantic vector representations using the Gemini Embedding API.
- **Semantic Similarity Search:** Computes cosine similarity between query and document embeddings.
- **Top-K Retrieval:** Retrieves the three highest-ranked document chunks based on semantic similarity scores.
- **Retrieval-Augmented Generation:** Uses retrieved document content as context for Gemini-powered answer generation.
- **Embedding Caching:** Implements Streamlit caching to reduce redundant embedding API calls.
- **Session State Management:** Preserves generated answers and retrieved context across Streamlit reruns.
- **Interactive User Interface:** Supports PDF uploads, question submission, and retrieved-context inspection.
- **API Error Handling:** Displays user-friendly messages and logs API errors for debugging.

## Technology Stack

| Component | Technology |
|-----------|------------|
| Programming Language | Python 3.12 |
| Web Application Framework | Streamlit |
| PDF Text Extraction | PyPDF |
| Text Chunking | Custom Sentence-Aware Chunking |
| Embedding Model | Google Gemini Embedding |
| Large Language Model | Google Gemini |
| Similarity Search | Scikit-learn (Cosine Similarity) |
| Retrieval Strategy | Top-3 Semantic Retrieval |
| Embedding Cache | Streamlit `@st.cache_data` |
| Session Management | Streamlit Session State |
| Environment Configuration | python-dotenv |
| Development Environment | Visual Studio Code |

## RAG Pipeline Implementation

### 1. Document Ingestion

The application accepts PDF documents through the Streamlit file uploader.

- Reads uploaded PDF documents using `PdfReader`.
- Extracts readable text from individual pages.
- Combines extracted text for downstream processing.

### 2. Sentence-Aware Text Chunking

The extracted text is segmented into smaller chunks using a custom Python function.

- Identifies sentence boundaries.
- Groups sentences into manageable chunks.
- Maintains overlapping context between consecutive chunks.
- Reduces the likelihood of splitting sentences across chunk boundaries.

**Purpose:** Improve the quality of contextual information available during semantic retrieval.

### 3. Vector Embedding Generation

Each document chunk is converted into a numerical embedding using the **Gemini Embedding API**.

**Embedding Model:** `gemini-embedding-001`

Embeddings represent the semantic meaning of text in a high-dimensional vector space.

Streamlit caching is implemented to reduce repeated embedding requests when the application reruns.

### 4. Query Embedding

The user's natural-language question is converted into an embedding using the same embedding model.

This allows semantic comparison between the user query and document chunks.

### 5. Semantic Similarity Search

The system uses **cosine similarity** to compare the query embedding against document embeddings.

Cosine similarity is calculated as:

**Cosine Similarity = (A · B) / (||A|| × ||B||)**

The resulting similarity scores are ranked to identify the most relevant document chunks.

### 6. Top-K Context Retrieval

The system selects the **Top 3 document chunks** with the highest semantic similarity scores.

The retrieved chunks are combined to form the context provided to the LLM.

**Current Retrieval Strategy:**

- Embedding-based semantic search
- Cosine similarity ranking
- Top-K selection (`K = 3`)
- In-memory embedding comparison

**Note:** The current implementation does not require a dedicated vector database.

### 7. Context-Augmented Answer Generation

The retrieved document chunks and user question are incorporated into a structured prompt.

The prompt instructs Gemini to:

- Answer using the supplied PDF context.
- Avoid relying on information outside the retrieved content.
- Indicate when the requested information cannot be found in the PDF.

**LLM:** Google Gemini Flash-Lite

### 8. Answer Presentation

The generated answer is displayed through the Streamlit interface.

Users can also expand the **View Retrieved PDF Content** section to inspect the retrieved text used during answer generation.

## Installation and Setup

### Prerequisites

- Python 3.12
- Git
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace the placeholders with your actual GitHub username and repository name.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Security Note:** Never commit your actual API key to GitHub. The `.env` file must be excluded through `.gitignore`.

### 5. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal:

```text
http://localhost:8501
```

## Current Implementation Status

**Status: Functional Proof of Concept (POC)**

The following capabilities have been implemented:

- [x] PDF document upload
- [x] PDF text extraction
- [x] Sentence-aware text chunking
- [x] Gemini embedding generation
- [x] Embedding caching
- [x] Query embedding generation
- [x] Cosine similarity search
- [x] Top-3 semantic retrieval
- [x] Context-augmented LLM generation
- [x] Interactive Streamlit interface
- [x] Session state management
- [x] Retrieved document context inspection
- [x] Basic API error handling

## Engineering Concepts Demonstrated

This project demonstrates practical experience with:

- **Retrieval-Augmented Generation (RAG)**
- **Large Language Model (LLM) Integration**
- **Semantic Vector Embeddings**
- **Natural Language Processing (NLP)**
- **Cosine Similarity and Vector Search**
- **Top-K Information Retrieval**
- **Prompt Engineering**
- **Python Application Development**
- **REST API Integration**
- **Caching and State Management**
- **AI Application Prototyping**

## Author

Developed as a hands-on **AI Engineering Portfolio Project** focused on building practical experience in Retrieval-Augmented Generation, semantic search, document intelligence, and LLM-powered application development.
