import os
import json
import requests
import fitz
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    industry: str
    location: str
    salary_min: int
    culture: str

def fetch_edinet_pdf(company_name: str) -> bytes:
    search_url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
    params = {"type": 2, "keyword": company_name, "date": "2023-01-01"}
    resp = requests.get(search_url, params=params)
    data = resp.json()
    results = data.get("results")
    if not results:
        raise HTTPException(status_code=404, detail="IR document not found")
    doc_id = results[0]["docID"]
    pdf_url = f"https://disclosure.edinet-fsa.go.jp/api/v1/documents/{doc_id}?type=1"
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
        "以下のIR情報を読んで、会社の強み、課題、志望動機例を" \
        "JSON形式で日本語で出力してください。"\
    )
    user_content = text[:4000]
    messages = [
        {"role": "system", "content": "あなたは優秀なキャリアアドバイザーです"},
        {"role": "user", "content": prompt + "\n" + user_content},
    ]
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_company")
async def search_company(req: CompanyRequest):
    pdf_bytes = fetch_edinet_pdf(req.company_name)
    text = extract_text_from_pdf(pdf_bytes)
    analysis = analyze_ir(text)
    return analysis

@app.post("/search_by_condition")
async def search_by_condition(cond: ConditionRequest):
    # 簡易的に industry キーワードで検索
    pdf_bytes = fetch_edinet_pdf(cond.industry)
    text = extract_text_from_pdf(pdf_bytes)
    analysis = analyze_ir(text)
    analysis["searched_industry"] = cond.industry
    analysis["location"] = cond.location
    analysis["salary_min"] = cond.salary_min
    analysis["culture"] = cond.culture
    return analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
