import React, { useState } from 'react'

function App() {
  const [companyName, setCompanyName] = useState('')
  const [result, setResult] = useState(null)
  const [condition, setCondition] = useState({
    industry: '',
    location: '',
    salary_min: '',
    culture: ''
  })

  const searchCompany = async () => {
    const res = await fetch('http://localhost:8000/search_company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_name: companyName })
    })
    const data = await res.json()
    setResult(data)
  }

  const searchByCondition = async () => {
    const res = await fetch('http://localhost:8000/search_by_condition', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        industry: condition.industry,
        location: condition.location,
        salary_min: Number(condition.salary_min),
        culture: condition.culture
      })
    })
    const data = await res.json()
    setResult(data)
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h1>就活支援アプリ</h1>
      <div>
        <h2>企業名で検索</h2>
        <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
        <button onClick={searchCompany}>検索</button>
      </div>
      <div>
        <h2>条件で検索</h2>
        <input placeholder="業界" value={condition.industry} onChange={(e) => setCondition({ ...condition, industry: e.target.value })} />
        <input placeholder="勤務地" value={condition.location} onChange={(e) => setCondition({ ...condition, location: e.target.value })} />
        <input placeholder="最低年収" value={condition.salary_min} onChange={(e) => setCondition({ ...condition, salary_min: e.target.value })} />
        <input placeholder="社風" value={condition.culture} onChange={(e) => setCondition({ ...condition, culture: e.target.value })} />
        <button onClick={searchByCondition}>検索</button>
      </div>
      {result && (
        <div>
          <h2>強み</h2>
          <pre>{JSON.stringify(result.strengths, null, 2)}</pre>
          <h2>課題</h2>
          <pre>{JSON.stringify(result.challenges, null, 2)}</pre>
          <h2>志望動機例</h2>
          <pre>{result.motivation}</pre>
        </div>
      )}
    </div>
  )
}

export default App
