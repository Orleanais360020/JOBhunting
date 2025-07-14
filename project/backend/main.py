import os
import json
import requests
from difflib import SequenceMatcher
import fitz
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanyRequest(BaseModel):
    company_name: str

class ConditionRequest(BaseModel):
    industry_code: Optional[str] = None
    prefecture: Optional[str] = None

def fetch_edinet_pdf(company_name: str) -> bytes:
    """Search EDINET for the latest document that roughly matches the company
    name and return the PDF bytes."""

    search_url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
    params = {"type": 2, "keyword": company_name, "date": "2024-01-01"}
    resp = requests.get(search_url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to query EDINET")
    data = resp.json()
    results = data.get("results") or []

    if not results and len(company_name) > 2:
        params["keyword"] = company_name[: len(company_name) // 2]
        resp = requests.get(search_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results") or []

    if not results:
        raise HTTPException(status_code=404, detail="IR document not found")

    best = None
    best_score = 0.0
    for r in results:
        name = r.get("filerName", "")
        score = SequenceMatcher(None, company_name, name).ratio()
        if score > best_score:
            best = r
            best_score = score

    if not best:
        raise HTTPException(status_code=404, detail="IR document not found")

    doc_id = best["docID"]
    pdf_url = (
        f"https://disclosure.edinet-fsa.go.jp/api/v1/documents/{doc_id}?type=1"
    )
    pdf_resp = requests.get(pdf_url)
    pdf_resp.raise_for_status()
    return pdf_resp.content


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def analyze_ir(text: str) -> dict:
    prompt = (
        "以下のIR情報を読んで、会社の強み、課題、志望動機例を"
        "JSON形式で日本語で出力してください。"
    )
    user_content = text[:4000]
    messages = [
        {"role": "system", "content": "あなたは優秀なキャリアアドバイザーです"},
        {"role": "user", "content": prompt + "\n" + user_content},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    content = response.choices[0].message.content
    return json.loads(content)


CORPORATIONS_CACHE: List[dict] = []


def fetch_corporations() -> List[dict]:
    """Retrieve the EDINET corporate list and cache it."""
    global CORPORATIONS_CACHE
    if CORPORATIONS_CACHE:
        return CORPORATIONS_CACHE
    url = "https://disclosure.edinet-fsa.go.jp/api/v1/corporations.json"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch corporations")
    data = resp.json()
    CORPORATIONS_CACHE = data.get("results", [])
    return CORPORATIONS_CACHE



def analyze_company(name: str) -> dict:
    try:
        pdf_bytes = fetch_edinet_pdf(name)
        text = extract_text_from_pdf(pdf_bytes)
        analysis = analyze_ir(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to analyze IR") from e
    analysis["company"] = name
    return analysis


@app.post("/search_company")
async def search_company(req: CompanyRequest):
    """Analyze a single company's IR data."""
    return analyze_company(req.company_name)


@app.post("/search_by_condition")
async def search_by_condition(cond: ConditionRequest):
    """Return analyses for companies that match the given conditions."""
    companies = fetch_corporations()

    matched: List[dict] = []
    for c in companies:
        if cond.industry_code and cond.industry_code != c.get("industryCode"):
            continue
        if cond.prefecture and cond.prefecture not in c.get("prefectureName", ""):
            continue
        matched.append(c)

    if not matched:
        raise HTTPException(status_code=404, detail="No companies found")

    results = []
    for c in matched[:5]:
        name = c.get("filerName")
        try:
            analysis = analyze_company(name)
            analysis["edinetCode"] = c.get("edinetCode")
            results.append(analysis)
        except HTTPException:
            continue

    if not results:
        raise HTTPException(status_code=500, detail="Failed to analyze IR")

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
