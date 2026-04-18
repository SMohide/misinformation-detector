import streamlit as st  # type: ignore
import requests  # type: ignore
import time

st.set_page_config(
    page_title="SciCheck – Scientific Misinformation Detector",
    layout="centered"
)

BACKEND_URL = "http://localhost:8000"

st.title("SciCheck")
st.subheader("Verify scientific claims against real research papers")
st.caption("Powered by RAG + Google Gemini 2.0 Flash | Sources: arXiv + PubMed")

# ── Check backend status ──
def check_backend():
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return health.status_code == 200
    except Exception:
        return False

backend_ok = check_backend()

if backend_ok:
    st.success("✅ Backend connected")
else:
    st.error(
        "❌ Backend not running. Open a **new terminal** and run:\n\n"
        "```\nuvicorn backend.main:app --reload --port 8000\n```"
    )
    st.info("💡 Tip: Keep the uvicorn terminal open while using this app. "
            "Then **refresh this page** once the backend is running.")
    st.stop()  # Don't render the rest of the UI if backend is down

st.divider()

# ── Claim input ──
st.markdown("**Enter a scientific claim to verify:**")
claim = st.text_area(
    label="Claim",
    placeholder="e.g. Law of attraction works with only positive thinking",
    height=100,
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 2])
with col1:
    verify_btn = st.button("Verify Claim", type="primary", use_container_width=True)
with col2:
    st.caption("Takes 10–20 seconds — fetching live research papers")

# ── Verification ──
if verify_btn:
    if not claim.strip():
        st.warning("Please enter a claim to verify.")
    elif len(claim.strip()) < 5:
        st.warning("Claim is too short. Please enter a meaningful scientific statement.")
    else:
        with st.spinner("🔍 Searching arXiv & PubMed, embedding papers, reasoning with Gemini..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/verify",
                    json={"claim": claim.strip()},
                    timeout=120
                )

                if response.status_code == 200:
                    data = response.json()

                    verdict = data.get("verdict", "UNVERIFIED")
                    confidence = data.get("confidence", 0)
                    reasoning = data.get("reasoning", "")
                    what_evidence_says = data.get("what_evidence_says", "")
                    key_distinction = data.get("key_distinction", "")
                    sources = data.get("sources", [])
                    papers_found = data.get("papers_found", 0)

                    # Verdict colour
                    verdict_colours = {
                        "SUPPORTED": "🟢",
                        "PARTIALLY SUPPORTED": "🟡",
                        "REFUTED": "🔴",
                        "UNVERIFIED": "⚪",
                    }
                    icon = verdict_colours.get(verdict, "⚪")

                    st.divider()
                    st.markdown(f"## {icon} Verdict: **{verdict}**")
                    st.progress(confidence / 100)
                    st.caption(f"Confidence: {confidence}%  |  Papers analysed: {papers_found}")

                    st.divider()
                    st.markdown("### 🧠 Reasoning")
                    st.write(reasoning)

                    if what_evidence_says:
                        st.markdown("### 📄 What the Evidence Says")
                        st.write(what_evidence_says)

                    if key_distinction:
                        st.markdown("### ⚠️ Key Distinction")
                        st.info(key_distinction)

                    if sources:
                        st.markdown("### 📚 Sources")
                        for s in sources:
                            st.markdown(f"- [{s['title']}]({s['url']}) *(via {s['source']})*")

                elif response.status_code == 404:
                    st.warning("No research papers found for this claim. Try rephrasing it.")
                elif response.status_code == 400:
                    st.warning("Claim is too short or invalid.")
                else:
                    st.error(f"Backend error {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The backend is taking too long — try a shorter claim.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure uvicorn is running on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")