import React from 'react'
import { Link } from 'react-router-dom'
import { formatPrice } from '../utils/api'

export default function RestaurantCard({ restaurant: r }) {
  return (
    <Link to={`/restaurant/${r.slug}`} className="gk-restaurant-card">
      <div className="gk-rest-cover">
        {r.cover_image
          ? <img src={r.cover_image} alt={r.name} />
          : <div style={{ width: '100%', height: '100%', background: 'linear-gradient(135deg, #1a1a1a, #2d2d2d)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><i className="bi bi-shop" style={{ fontSize: '3rem', color: 'var(--primary)', opacity: 0.5 }}></i></div>
        }
        <div className="gk-rest-logo">
          {r.logo ? <img src={r.logo} alt="" /> : <div style={{ width: '100%', height: '100%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: '1.2rem', color: 'var(--dark)' }}>{r.name[0]}</div>}
        </div>
        <div className="gk-rest-badges">
          {r.is_featured && <span className="gk-rest-badge gk-rest-badge-featured">Featured</span>}
          {r.is_free_delivery && <span className="gk-rest-badge gk-rest-badge-free">Free delivery</span>}
          {!r.is_open && <span className="gk-rest-badge gk-rest-badge-closed">Closed</span>}
        </div>
      </div>
      <div className="gk-rest-info">
        <div className="gk-rest-name">{r.name}</div>
        <div className="gk-rest-cat">{r.category_name}</div>
        <div className="gk-rest-meta">
          <span className="rating"><i className="bi bi-star-fill"></i> {r.rating || '—'}</span>
          <span><i className="bi bi-clock"></i> {r.estimated_delivery_time} min</span>
          {r.zone_name && <span><i className="bi bi-geo-alt"></i> {r.zone_name}</span>}
        </div>
      </div>
      <div className="gk-rest-footer">
        <span className={`delivery-fee ${r.is_free_delivery ? 'free' : ''}`}>
          {r.is_free_delivery ? 'Free delivery' : `Delivery: ${formatPrice(r.delivery_fee)}`}
        </span>
        {r.minimum_order > 0 && <span className="min-order">Min: {formatPrice(r.minimum_order)}</span>}
      </div>
    </Link>
  )
}