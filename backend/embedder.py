from sentence_transformers import SentenceTransformer  # type: ignore
import faiss  # type: ignore
import numpy as np  # type: ignore

# Load once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_papers(papers: list, chunk_size: int = 300) -> list:
    chunks = []
    for paper in papers:
        text = f"{paper['title']}. {paper['abstract']}"
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append({
                "text": chunk,
                "source": paper["source"],
                "url": paper["url"],
                "title": paper["title"]
            })
    return chunks


def build_faiss_index(chunks: list):
    if not chunks:
        return None, None, chunks

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)
    embeddings = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    return index, embeddings, chunks


def retrieve_relevant_chunks(claim: str, index, chunks: list, top_k: int = 5) -> list:
    if index is None or not chunks:
        return []

    claim_embedding = model.encode([claim], convert_to_numpy=True)
    claim_embedding = np.array(claim_embedding, dtype="float32")
    faiss.normalize_L2(claim_embedding)

    k = min(top_k, len(chunks))
    scores, indices = index.search(claim_embedding, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if 0 <= idx < len(chunks):
            results.append({
                **chunks[idx],
                "similarity_score": float(score)
            })
    return results