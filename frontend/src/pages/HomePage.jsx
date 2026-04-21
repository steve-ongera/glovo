import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../utils/api'
import RestaurantCard from '../components/RestaurantCard'

export default function HomePage() {
  const [categories, setCategories] = useState([])
  const [restaurants, setRestaurants] = useState([])
  const [featured, setFeatured] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    document.title = 'GlovoKE — Food & More Delivered'
    Promise.all([
      api.get('/categories/'),
      api.get('/restaurants/'),
      api.get('/restaurants/?featured=true'),
    ]).then(([cats, rests, feat]) => {
      setCategories(cats.data.results || cats.data)
      setRestaurants(rests.data.results || rests.data)
      setFeatured(feat.data.results || feat.data)
    }).finally(() => setLoading(false))
  }, [])

  const filtered = activeCategory
    ? restaurants.filter(r => r.category_name?.toLowerCase() === activeCategory.toLowerCase())
    : restaurants

  const handleSearch = (e) => {
    e.preventDefault()
    if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <>
      {/* Hero */}
      <div className="gk-hero">
        <div className="gk-hero-inner">
          <h1>Order food, <span>delivered fast</span><br />anywhere in Kenya</h1>
          <p>Restaurants, groceries, and more — delivered to your door.</p>
          <form className="gk-hero-search" onSubmit={handleSearch}>
            <i className="bi bi-search" style={{ color: 'var(--text-muted)', fontSize: '1rem' }}></i>
            <input placeholder="Search restaurants or food..." value={q} onChange={e => setQ(e.target.value)} />
            <button type="submit"><i className="bi bi-arrow-right"></i> Find</button>
          </form>
        </div>
      </div>

      {/* Category strip */}
      <div className="gk-catstrip">
        <div className="gk-catstrip-inner">
          <button
            className={`gk-cat-pill ${!activeCategory ? 'active' : ''}`}
            onClick={() => setActiveCategory(null)}>
            <i className="bi bi-grid"></i> All
          </button>
          {categories.map(cat => (
            <button key={cat.id}
              className={`gk-cat-pill ${activeCategory === cat.name ? 'active' : ''}`}
              onClick={() => setActiveCategory(activeCategory === cat.name ? null : cat.name)}>
              {cat.icon && <i className={`bi ${cat.icon}`}></i>}
              {cat.name}
              <span style={{ fontSize: '0.7rem', color: 'var(--text-light)', marginLeft: 2 }}>({cat.restaurant_count})</span>
            </button>
          ))}
        </div>
      </div>

      <div className="container-gk">
        {/* Featured */}
        {!activeCategory && featured.length > 0 && (
          <section className="gk-section">
            <div className="gk-section-header">
              <h2 className="gk-section-title">Featured</h2>
              <Link to="/search" className="gk-section-link">See all <i className="bi bi-arrow-right"></i></Link>
            </div>
            <div className="gk-restaurants-grid">
              {featured.slice(0, 4).map(r => <RestaurantCard key={r.id} restaurant={r} />)}
            </div>
          </section>
        )}

        {/* Promo */}
        {!activeCategory && (
          <div className="gk-promo" style={{ marginBottom: '2rem' }}>
            <div>
              <h3>Get 20% off your first order</h3>
              <p>Use code below at checkout</p>
            </div>
            <div className="gk-promo-code">FIRST20</div>
          </div>
        )}

        {/* All restaurants */}
        <section className="gk-section">
          <div className="gk-section-header">
            <h2 className="gk-section-title">
              {activeCategory ? activeCategory : 'All Restaurants'}
              <span style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-muted)', marginLeft: 8 }}>({filtered.length})</span>
            </h2>
          </div>
          {loading ? (
            <div className="gk-spinner" style={{ minHeight: '40vh' }}></div>
          ) : filtered.length === 0 ? (
            <div className="gk-empty">
              <div className="gk-empty-icon"><i className="bi bi-shop"></i></div>
              <h4>No restaurants found</h4>
              <p>Try a different category or check back later</p>
            </div>
          ) : (
            <div className="gk-restaurants-grid">
              {filtered.map(r => <RestaurantCard key={r.id} restaurant={r} />)}
            </div>
          )}
        </section>
      </div>
    </>
  )
}