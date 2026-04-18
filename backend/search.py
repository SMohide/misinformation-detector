import requests
import xml.etree.ElementTree as ET


def search_arxiv(query: str, max_results: int = 5) -> list:
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        root = ET.fromstring(response.content)
        papers = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            link = entry.find("atom:id", ns)
            if title is not None and summary is not None:
                papers.append({
                    "title": title.text.strip(),
                    "abstract": summary.text.strip(),
                    "url": link.text.strip() if link is not None else "",
                    "source": "arXiv"
                })
        print(f"arXiv returned {len(papers)} papers")
        return papers
    except Exception as e:
        print(f"arXiv search error: {e}")
        return []


def search_pubmed(query: str, max_results: int = 4) -> list:
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        ids = requests.get(search_url, params=search_params, timeout=15).json()
        id_list = ids.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            print("PubMed returned 0 IDs")
            return []

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "rettype": "abstract",
            "retmode": "text"
        }
        abstracts_text = requests.get(fetch_url, params=fetch_params, timeout=15).text
        print(f"PubMed returned {len(id_list)} papers")

        return [{
            "title": f"PubMed results for: {query}",
            "abstract": abstracts_text[:3000],
            "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={query.replace(' ', '+')}",
            "source": "PubMed"
        }]
    except Exception as e:
        print(f"PubMed search error: {e}")
        return []


def fetch_all_papers(claim: str) -> list:
    arxiv_results = search_arxiv(claim, max_results=5)
    pubmed_results = search_pubmed(claim, max_results=4)
    all_papers = arxiv_results + pubmed_results
    print(f"Total papers found: {len(all_papers)}")
    return all_papers