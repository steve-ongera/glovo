import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../utils/api'
import RestaurantCard from '../components/RestaurantCard'

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const q = searchParams.get('q') || ''

  useEffect(() => {
    document.title = q ? `"${q}" | GlovoKE` : 'Search | GlovoKE'
    if (!q.trim()) { setResults([]); return }
    setLoading(true)
    api.get(`/restaurants/?search=${encodeURIComponent(q)}`)
      .then(res => setResults(res.data.results || res.data))
      .finally(() => setLoading(false))
  }, [q])

  return (
    <div className="container-gk" style={{ padding: '1.5rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ position: 'relative', maxWidth: 480 }}>
          <input className="gk-input" placeholder="Search restaurants..."
            defaultValue={q}
            onChange={e => setSearchParams({ q: e.target.value })}
            style={{ paddingLeft: '2.5rem', fontSize: '1rem' }} />
          <i className="bi bi-search" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}></i>
        </div>
      </div>

      {loading ? (
        <div className="gk-spinner"></div>
      ) : results.length === 0 && q ? (
        <div className="gk-empty">
          <div className="gk-empty-icon"><i className="bi bi-search"></i></div>
          <h4>No results for "{q}"</h4>
          <p>Try different keywords</p>
        </div>
      ) : (
        <>
          {q && <p style={{ marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>{results.length} result{results.length !== 1 ? 's' : ''} for "{q}"</p>}
          <div className="gk-restaurants-grid">
            {results.map(r => <RestaurantCard key={r.id} restaurant={r} />)}
          </div>
        </>
      )}
    </div>
  )
}