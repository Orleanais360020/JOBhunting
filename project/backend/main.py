import os
import json
import requests
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
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    culture: Optional[str] = None


def fetch_edinet_pdf(company_name: str) -> bytes:
    """
    EDINET で会社名をキーワードに直近のドキュメントを検索し
    該当 PDF のバイト列を返します。
    """
    search_url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
    params = {
        "type": 2,                # 文書検索
        "keyword": company_name,
        "date": "2024-01-01",     # 検索開始日
    }
    resp = requests.get(search_url, params=params, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to query EDINET")

    data = resp.json()
    results = data.get("results")
    if not results:
        raise HTTPException(status_code=404, detail="IR document not found")

    doc_id = results[0]["docID"]
    pdf_url = f"https://disclosure.edinet-fsa.go.jp/api/v1/documents/{doc_id}?type=1"

    pdf_resp = requests.get(pdf_url, timeout=30)
    pdf_resp.raise_for_status()
    return pdf_resp.content


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """PDF からテキストを抽出します。"""
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def analyze_ir(text: str) -> dict:
    """
    IR 情報を GPT に要約させ、強み・課題・志望動機例を含む
    JSON を返します。
    """
    prompt = (
        "以下のIR情報を読んで、会社の強み、課題、志望動機例を"
        "JSON形式で日本語で出力してください。"
    )
    user_content = text[:4000]  # 入力長制限
    messages = [
        {"role": "system", "content": "あなたは優秀なキャリアアドバイザーです"},
        {"role": "user", "content": prompt + "\n" + user_content},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search_company")
async def search_company(req: CompanyRequest):
    """単一企業を分析して返します。"""
    pdf_bytes = fetch_edinet_pdf(req.company_name)
    text = extract_text_from_pdf(pdf_bytes)
    analysis = analyze_ir(text)
    analysis["company"] = req.company_name
    return analysis


@app.post("/search_by_condition")
async def search_by_condition(cond: ConditionRequest):
    """
    条件に合致する企業を companies.json から抽出し、
    それぞれ IR 解析結果を返します。
    """
    companies_path = os.path.join(os.path.dirname(__file__), "companies.json")
    with open(companies_path, "r", encoding="utf-8") as f:
        companies = json.load(f)

    matched: List[str] = []
    for c in companies:
        if cond.industry and cond.industry not in c["industry"]:
            continue
        if cond.location and cond.location not in c["location"]:
            continue
        if cond.salary_min and c["salary"] < cond.salary_min:
            continue
        if cond.culture and cond.culture not in c["culture"]:
            continue
        matched.append(c["name"])

    if not matched:
        raise HTTPException(status_code=404, detail="No companies found")

    results = []
    for name in matched:
        try:
            pdf_bytes = fetch_edinet_pdf(name)
            text = extract_text_from_pdf(pdf_bytes)
            analysis = analyze_ir(text)
            analysis["company"] = name
            results.append(analysis)
        except HTTPException:
            # 個別企業の取得失敗はスキップし、他を続行
            continue

    if not results:
        raise HTTPException(status_code=500, detail="Failed to analyze IR")

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
