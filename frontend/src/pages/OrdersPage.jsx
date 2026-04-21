import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api, { formatPrice } from '../utils/api'

const STATUS = {
  pending: { color: '#f59e0b', icon: 'bi-clock', label: 'Pending' },
  confirmed: { color: '#3b82f6', icon: 'bi-check-circle', label: 'Confirmed' },
  preparing: { color: '#a855f7', icon: 'bi-fire', label: 'Preparing' },
  ready: { color: '#22c55e', icon: 'bi-bag-check', label: 'Ready' },
  on_the_way: { color: '#FFC244', icon: 'bi-bicycle', label: 'On the way' },
  delivered: { color: '#22c55e', icon: 'bi-check2-all', label: 'Delivered' },
  cancelled: { color: '#ef4444', icon: 'bi-x-circle', label: 'Cancelled' },
}

export default function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'My Orders | GlovoKE'
    api.get('/orders/').then(res => setOrders(res.data.results || res.data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="gk-spinner" style={{ minHeight: '60vh' }}></div>

  return (
    <div className="container-gk" style={{ padding: '1.5rem' }}>
      <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.5rem', marginBottom: '1.5rem' }}>My Orders</h1>

      {orders.length === 0 ? (
        <div className="gk-empty">
          <div className="gk-empty-icon"><i className="bi bi-receipt"></i></div>
          <h4>No orders yet</h4>
          <p>Your order history will appear here</p>
          <Link to="/" className="btn-gk btn-gk-primary">Order Now</Link>
        </div>
      ) : (
        orders.map(order => {
          const st = STATUS[order.status] || STATUS.pending
          return (
            <Link to={`/orders/${order.id}`} key={order.id} style={{ display: 'block', marginBottom: '1rem', textDecoration: 'none' }}>
              <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', transition: 'var(--transition)' }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--primary)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <div>
                    <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>#{order.order_number}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{order.restaurant_name}</div>
                  </div>
                  <span style={{ background: `${st.color}18`, color: st.color, padding: '4px 12px', borderRadius: 'var(--radius-pill)', fontSize: '0.78rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 4 }}>
                    <i className={`bi ${st.icon}`}></i> {st.label}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  <span>{new Date(order.created_at).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                  <span style={{ fontWeight: 800, color: 'var(--dark)', fontSize: '0.95rem' }}>{formatPrice(order.total)}</span>
                </div>
              </div>
            </Link>
          )
        })
      )}
    </div>
  )
}