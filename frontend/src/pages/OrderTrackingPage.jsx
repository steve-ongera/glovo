import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api, { formatPrice } from '../utils/api'

const STEPS = [
  { key: 'pending', label: 'Order Placed', icon: 'bi-receipt', desc: 'Your order has been received' },
  { key: 'confirmed', label: 'Confirmed', icon: 'bi-check-circle', desc: 'Restaurant confirmed your order' },
  { key: 'preparing', label: 'Preparing', icon: 'bi-fire', desc: 'Your food is being prepared' },
  { key: 'on_the_way', label: 'On the Way', icon: 'bi-bicycle', desc: 'Rider is heading to you' },
  { key: 'delivered', label: 'Delivered', icon: 'bi-check2-all', desc: 'Enjoy your meal!' },
]

const ORDER_INDEX = { pending: 0, confirmed: 1, preparing: 2, ready: 2, on_the_way: 3, delivered: 4 }

export default function OrderTrackingPage() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/orders/${id}/`).then(res => {
      setOrder(res.data)
      document.title = `Order #${res.data.order_number} | GlovoKE`
    }).finally(() => setLoading(false))

    // Poll every 30s for live updates
    const interval = setInterval(() => {
      api.get(`/orders/${id}/`).then(res => setOrder(res.data)).catch(() => {})
    }, 30000)
    return () => clearInterval(interval)
  }, [id])

  if (loading) return <div className="gk-spinner" style={{ minHeight: '60vh' }}></div>
  if (!order) return <div className="gk-empty container-gk"><h4>Order not found</h4></div>

  const currentIndex = ORDER_INDEX[order.status] ?? 0

  return (
    <div className="container-gk" style={{ padding: '1.5rem', maxWidth: 640 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <Link to="/orders" style={{ color: 'var(--text-muted)' }}><i className="bi bi-arrow-left"></i></Link>
        <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.3rem' }}>Order #{order.order_number}</h1>
      </div>

      {/* ETA card */}
      {order.status !== 'delivered' && order.status !== 'cancelled' && (
        <div style={{ background: 'var(--dark)', borderRadius: 'var(--radius-lg)', padding: '1.5rem', marginBottom: '1rem', textAlign: 'center', color: '#fff' }}>
          <div style={{ color: 'var(--primary)', fontWeight: 800, fontSize: '0.82rem', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Estimated Delivery</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 900, fontFamily: 'var(--font-display)' }}>{order.estimated_delivery_time} min</div>
          <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.82rem', marginTop: 4 }}>From {order.restaurant_name}</div>
        </div>
      )}

      {/* Tracker */}
      <div className="gk-tracker">
        <div className="gk-tracker-steps">
          {STEPS.map((step, i) => {
            const done = i < currentIndex
            const active = i === currentIndex
            return (
              <div key={step.key} className={`gk-tracker-step ${done ? 'done' : ''} ${active ? 'active' : ''}`}>
                <div className="gk-tracker-dot">
                  {done ? <i className="bi bi-check-lg"></i> : <i className={`bi ${step.icon}`}></i>}
                </div>
                <div className="gk-tracker-info">
                  <h6 style={{ color: active ? 'var(--dark)' : done ? 'var(--text-muted)' : 'var(--text-light)' }}>{step.label}</h6>
                  {(done || active) && <p>{step.desc}</p>}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Items */}
      <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', marginBottom: '1rem' }}>
        <h5 style={{ fontWeight: 800, marginBottom: '1rem', fontSize: '0.95rem' }}>Items</h5>
        {order.items.map(item => (
          <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
            <span>{item.item_name} × {item.quantity}</span>
            <span style={{ fontWeight: 700 }}>{formatPrice(item.subtotal)}</span>
          </div>
        ))}
        <div style={{ borderTop: '1px solid var(--border)', marginTop: '0.75rem', paddingTop: '0.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: 4 }}>
            <span>Subtotal</span><span>{formatPrice(order.subtotal)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: 4 }}>
            <span>Delivery</span><span>{formatPrice(order.delivery_fee)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: '1rem' }}>
            <span>Total</span><span style={{ color: 'var(--primary)' }}>{formatPrice(order.total)}</span>
          </div>
        </div>
      </div>

      {/* Delivery address */}
      <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem' }}>
        <h5 style={{ fontWeight: 800, marginBottom: '0.75rem', fontSize: '0.95rem' }}>Delivery Address</h5>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          <div><i className="bi bi-geo-alt" style={{ color: 'var(--primary)' }}></i> {order.delivery_street}, {order.delivery_town}</div>
          <div style={{ marginTop: 4 }}><i className="bi bi-person" style={{ color: 'var(--primary)' }}></i> {order.customer_name} · {order.customer_phone}</div>
        </div>
      </div>
    </div>
  )
}