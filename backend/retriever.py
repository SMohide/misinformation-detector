# Re-export from embedder so any import of retriever still works
from backend.embedder import chunk_papers, build_faiss_index, retrieve_relevant_chunks

__all__ = ["chunk_papers", "build_faiss_index", "retrieve_relevant_chunks"]