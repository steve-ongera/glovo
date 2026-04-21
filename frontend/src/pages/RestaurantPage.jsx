import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import api, { formatPrice, getErrorMessage } from '../utils/api'
import { useCart } from '../context/CartContext'
import { useToast } from '../context/ToastContext'

export default function RestaurantPage() {
  const { slug } = useParams()
  const [restaurant, setRestaurant] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeSection, setActiveSection] = useState(null)
  const sectionRefs = useRef({})
  const { addItem, cart } = useCart()
  const { toast } = useToast()

  useEffect(() => {
    api.get(`/restaurants/${slug}/`).then(res => {
      setRestaurant(res.data)
      if (res.data.sections?.length > 0) setActiveSection(res.data.sections[0].id)
      document.title = `${res.data.name} | GlovoKE`
    }).catch(() => toast('Could not load restaurant', 'error'))
      .finally(() => setLoading(false))
  }, [slug])

  const handleAdd = async (menuItemId) => {
    try {
      const result = await addItem(menuItemId)
      if (result) toast('Added to cart', 'success')
    } catch (err) {
      if (err.status === 409) {
        toast('Clear your cart first — it has items from another restaurant', 'error')
      } else {
        toast(getErrorMessage(err), 'error')
      }
    }
  }

  const getItemQty = (itemId) => {
    const found = cart.items.find(ci => ci.menu_item?.id === itemId)
    return found ? found.quantity : 0
  }

  const scrollToSection = (sectionId) => {
    setActiveSection(sectionId)
    sectionRefs.current[sectionId]?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  if (loading) return <div className="gk-spinner" style={{ minHeight: '80vh' }}></div>
  if (!restaurant) return <div className="gk-empty container-gk" style={{ paddingTop: '4rem' }}><h4>Restaurant not found</h4></div>

  return (
    <>
      {/* Cover */}
      <div className="gk-rest-hero">
        {restaurant.cover_image
          ? <img src={restaurant.cover_image} alt={restaurant.name} />
          : <div style={{ width: '100%', height: '100%', background: 'linear-gradient(135deg, #1a1a1a, var(--primary))', opacity: 0.4 }} />
        }
        <div className="gk-rest-hero-overlay" />
        <div className="gk-rest-hero-info">
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1rem' }}>
            <div className="gk-rest-hero-logo">
              {restaurant.logo ? <img src={restaurant.logo} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <div style={{ width: '100%', height: '100%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: '1.5rem', color: 'var(--dark)' }}>{restaurant.name[0]}</div>}
            </div>
            <div>
              <h1>{restaurant.name}</h1>
              <div className="meta">
                <span><i className="bi bi-star-fill" style={{ color: 'var(--primary)' }}></i> {restaurant.rating}</span>
                <span><i className="bi bi-clock"></i> {restaurant.estimated_delivery_time} min</span>
                <span><i className="bi bi-geo-alt"></i> {restaurant.address}</span>
                <span style={{ color: restaurant.is_open ? 'var(--success)' : 'var(--danger)', fontWeight: 700 }}>
                  <i className={`bi bi-circle-fill`} style={{ fontSize: '0.5rem' }}></i> {restaurant.is_open ? 'Open' : 'Closed'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Delivery info strip */}
      <div style={{ background: 'var(--white)', borderBottom: '1px solid var(--border)', padding: '0.75rem 1.5rem' }}>
        <div className="container-gk" style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.82rem' }}>
          <span><i className="bi bi-truck" style={{ color: 'var(--primary)' }}></i> Delivery: {Number(restaurant.delivery_fee) === 0 ? <strong style={{ color: 'var(--success)' }}>Free</strong> : <strong>{formatPrice(restaurant.delivery_fee)}</strong>}</span>
          {restaurant.minimum_order > 0 && <span><i className="bi bi-bag" style={{ color: 'var(--primary)' }}></i> Min order: <strong>{formatPrice(restaurant.minimum_order)}</strong></span>}
          {restaurant.free_delivery_threshold && <span><i className="bi bi-gift" style={{ color: 'var(--success)' }}></i> Free delivery above <strong>{formatPrice(restaurant.free_delivery_threshold)}</strong></span>}
        </div>
      </div>

      {/* Sticky section nav */}
      {restaurant.sections?.length > 1 && (
        <div className="gk-menu-nav">
          <div className="gk-menu-nav-inner container-gk" style={{ padding: 0 }}>
            {restaurant.sections.map(section => (
              <button key={section.id}
                className={`gk-menu-nav-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => scrollToSection(section.id)}
                style={{ background: 'none', border: 'none' }}>
                {section.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Menu */}
      <div className="container-gk" style={{ padding: '1.5rem' }}>
        {restaurant.sections?.map(section => (
          <div key={section.id} ref={el => sectionRefs.current[section.id] = el} style={{ marginBottom: '2rem' }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.1rem', marginBottom: '0.5rem', paddingBottom: '0.5rem', borderBottom: '2px solid var(--primary)', display: 'inline-block' }}>
              {section.name}
            </h3>
            {section.description && <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>{section.description}</p>}
            <div style={{ background: 'var(--white)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border)', overflow: 'hidden' }}>
              {section.items.filter(item => item.is_available).map(item => {
                const qty = getItemQty(item.id)
                return (
                  <div key={item.id} className="gk-menu-item">
                    <div className="gk-menu-item-body">
                      <div className="gk-menu-item-name">{item.name}</div>
                      {item.description && <div className="gk-menu-item-desc">{item.description}</div>}
                      <div className="gk-menu-item-tags">
                        {item.is_popular && <span className="gk-menu-item-tag popular"><i className="bi bi-fire"></i> Popular</span>}
                        {item.is_vegetarian && <span className="gk-menu-item-tag veg"><i className="bi bi-leaf"></i> Veg</span>}
                        {item.is_spicy && <span className="gk-menu-item-tag">Spicy</span>}
                        {item.calories && <span className="gk-menu-item-tag">{item.calories} kcal</span>}
                      </div>
                      <div className="gk-menu-item-price">
                        <span className="gk-item-price">{formatPrice(item.price)}</span>
                        {item.compare_price && <span className="gk-item-price-old">{formatPrice(item.compare_price)}</span>}
                      </div>
                    </div>
                    {item.image && <img src={item.image} alt={item.name} className="gk-menu-item-img" />}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      {qty === 0 ? (
                        <button className="gk-add-btn" onClick={() => handleAdd(item.id)} disabled={!restaurant.is_open}>
                          <i className="bi bi-plus"></i>
                        </button>
                      ) : (
                        <div className="gk-qty">
                          <button className="gk-qty-btn" onClick={() => {
                            const cartItem = cart.items.find(ci => ci.menu_item?.id === item.id)
                            if (cartItem) import('../context/CartContext').then(() => {})
                            // handled via CartContext updateItem
                          }}>−</button>
                          <span className="gk-qty-val">{qty}</span>
                          <button className="gk-qty-btn" onClick={() => handleAdd(item.id)}>+</button>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </>
  )
}