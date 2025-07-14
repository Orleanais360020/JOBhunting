import React, { useState } from 'react'

function App() {
  const [companyName, setCompanyName] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [condition, setCondition] = useState({
    industry: '',
    location: '',
    salary_min: '',
    culture: ''
  })

  const searchCompany = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://localhost:8000/search_company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName })
      })
      if (!res.ok) throw new Error('検索に失敗しました')
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const searchByCondition = async () => {
    setLoading(true)
    setError('')
    try {
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
      if (!res.ok) throw new Error('検索に失敗しました')
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h1>就活支援アプリ</h1>
      <div style={{ marginBottom: '1rem' }}>
        <h2>企業名で検索</h2>
        <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
        <button onClick={searchCompany}>検索</button>
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <h2>条件で検索</h2>
        <input placeholder="業界" value={condition.industry} onChange={(e) => setCondition({ ...condition, industry: e.target.value })} />
        <input placeholder="勤務地" value={condition.location} onChange={(e) => setCondition({ ...condition, location: e.target.value })} />
        <input placeholder="最低年収" value={condition.salary_min} onChange={(e) => setCondition({ ...condition, salary_min: e.target.value })} />
        <input placeholder="社風" value={condition.culture} onChange={(e) => setCondition({ ...condition, culture: e.target.value })} />
        <button onClick={searchByCondition}>検索</button>
      </div>
      {loading && <p>検索中...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <div>
          <h2>強み</h2>
          {Array.isArray(result.strengths) ? (
            <ul>
              {result.strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          ) : (
            <p>{result.strengths}</p>
          )}
          <h2>課題</h2>
          {Array.isArray(result.challenges) ? (
            <ul>
              {result.challenges.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          ) : (
            <p>{result.challenges}</p>
          )}
          <h2>志望動機例</h2>
          <p>{result.motivation}</p>
        </div>
      )}
    </div>
  )
}

export default App
