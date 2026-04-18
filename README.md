Misinformation Detection System (SciCheck)

SciCheck is an AI-powered scientific claim verification system designed to detect and analyze misinformation by validating claims against credible research sources. The system leverages a Retrieval-Augmented Generation (RAG) pipeline to combine information retrieval with large language model reasoning for accurate, evidence-based outputs.

Overview

The system accepts a user-provided claim and evaluates its validity by retrieving relevant research papers from sources such as arXiv and PubMed. It processes and analyzes the retrieved content to generate a structured response including a verdict, confidence score, reasoning, and supporting evidence.

Key Features

- Scientific claim verification using real research data  
- Retrieval-Augmented Generation (RAG) pipeline  
- Semantic search using FAISS for efficient document retrieval  
- Integration with Large Language Models (LLMs) for reasoning and explanation  
- Structured output including verdict, confidence, and evidence summary  
- Deduplicated and traceable source references  

System Architecture

1. Data Retrieval 
   Fetches research papers using APIs (arXiv, PubMed)

2. Text Processing
   Chunks and preprocesses research content for embedding

3. Embedding & Indexing
   Generates vector embeddings and stores them using FAISS

4. Semantic Search 
   Retrieves top relevant chunks based on query similarity

5. LLM Reasoning 
   Uses a language model to analyze retrieved evidence and generate structured output

ech Stack

- Python  
- FastAPI  
- FAISS (Vector Search)  
- Google Gemini (LLM)  
- Streamlit (Frontend)  
- arXiv API, PubMed  

## Project Structure
