import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.0-flash"


def analyse_claim(claim: str, relevant_chunks: list) -> dict:
    if not relevant_chunks:
        return {
            "verdict": "UNVERIFIED",
            "confidence": 0,
            "reasoning": "No relevant research chunks were retrieved.",
            "what_evidence_says": "",
            "key_distinction": ""
        }

    context = "\n\n".join([
        f"[{i+1}] Title: {c['title']}\nSource: {c['source']}\nExcerpt: {c['text']}"
        for i, c in enumerate(relevant_chunks)
    ])

    prompt = f"""You are a scientific fact-checker. Analyse the following claim against the provided research paper excerpts.

CLAIM: {claim}

RESEARCH EVIDENCE:
{context}

Respond ONLY with a valid JSON object (no markdown, no code fences) with these exact keys:
{{
  "verdict": "SUPPORTED" | "REFUTED" | "PARTIALLY SUPPORTED" | "UNVERIFIED",
  "confidence": <integer 0-100>,
  "reasoning": "<2-4 sentences explaining your verdict>",
  "what_evidence_says": "<1-3 sentences summarising what the papers actually say>",
  "key_distinction": "<1-2 sentences on the most important nuance or caveat>"
}}"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
            )
        )

        raw = response.text.strip()

        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}\nRaw response: {raw}")
        return {
            "verdict": "UNVERIFIED",
            "confidence": 0,
            "reasoning": "Could not parse model response.",
            "what_evidence_says": raw[:300] if 'raw' in dir() else "",
            "key_distinction": ""
        }
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {
            "verdict": "UNVERIFIED",
            "confidence": 0,
            "reasoning": f"Model error: {str(e)}",
            "what_evidence_says": "",
            "key_distinction": ""
        }