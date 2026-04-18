from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.search import fetch_all_papers
from backend.embedder import chunk_papers, build_faiss_index, retrieve_relevant_chunks
from backend.reasoner import analyse_claim

app = FastAPI(title="SciCheck — Scientific Misinformation Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClaimRequest(BaseModel):
    claim: str


class VerificationResult(BaseModel):
    claim: str
    verdict: str
    confidence: int
    reasoning: str
    what_evidence_says: str
    key_distinction: str
    sources: list
    papers_found: int


@app.get("/")
def root():
    return {"message": "SciCheck backend is live. POST to /verify to check a claim."}


@app.get("/health")
def health():
    return {"status": "running", "message": "SciCheck backend is live"}


@app.post("/verify", response_model=VerificationResult)
async def verify_claim(request: ClaimRequest):
    claim = request.claim.strip()

    if len(claim) < 5:
        raise HTTPException(status_code=400, detail="Claim too short.")

    try:
        # Step 1: fetch papers
        papers = fetch_all_papers(claim)
        if not papers:
            raise HTTPException(status_code=404, detail="No papers found for this claim.")

        # Step 2: chunk + embed
        chunks = chunk_papers(papers)
        if not chunks:
            raise HTTPException(status_code=404, detail="Could not extract content from papers.")

        index, _, chunks = build_faiss_index(chunks)

        # Step 3: retrieve relevant chunks
        relevant = retrieve_relevant_chunks(claim, index, chunks, top_k=5)
        if not relevant:
            raise HTTPException(status_code=404, detail="Could not retrieve relevant chunks.")

        # Step 4: LLM reasoning
        result = analyse_claim(claim, relevant)

        # Step 5: deduplicated sources
        seen = set()
        sources = []
        for c in relevant:
            if c["url"] not in seen:
                seen.add(c["url"])
                sources.append({
                    "title": c["title"],
                    "url": c["url"],
                    "source": c["source"]
                })

        return VerificationResult(
            claim=claim,
            verdict=result.get("verdict", "UNVERIFIED"),
            confidence=int(result.get("confidence", 0)),
            reasoning=result.get("reasoning", ""),
            what_evidence_says=result.get("what_evidence_says", ""),
            key_distinction=result.get("key_distinction", ""),
            sources=sources,
            papers_found=len(papers)
        )

    except HTTPException:
        raise
    except Exception as e:
        # Print full traceback to uvicorn terminal
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/test-model")
def test_model():
    try:
        from google import genai
        from dotenv import load_dotenv
        load_dotenv()
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say: model working"
        )
        return {"status": "ok", "response": response.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}