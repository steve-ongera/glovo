import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import api, { formatPrice, getErrorMessage } from '../utils/api'

export default function CartPage() {
  const { cart, updateItem, clearCart, loading: cartLoading } = useCart()
  const { user } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()

  const [couponCode, setCouponCode] = useState('')
  const [couponDiscount, setCouponDiscount] = useState(0)
  const [couponLoading, setCouponLoading] = useState(false)
  const [removingId, setRemovingId] = useState(null)
  const [clearConfirm, setClearConfirm] = useState(false)

  const subtotal = Number(cart?.total || 0)
  const deliveryFee = cart?.restaurant ? Number(cart.restaurant.delivery_fee) : 0
  const freeThreshold = cart?.restaurant?.free_delivery_threshold
    ? Number(cart.restaurant.free_delivery_threshold)
    : null
  const effectiveDeliveryFee =
    freeThreshold && subtotal >= freeThreshold ? 0 : deliveryFee
  const total = subtotal + effectiveDeliveryFee - couponDiscount

  const amountToFreeDelivery =
    freeThreshold && effectiveDeliveryFee > 0
      ? freeThreshold - subtotal
      : null

  const isEmpty = !cart?.items || cart.items.length === 0

  /* ── Handlers ── */
  const handleQty = async (itemId, newQty) => {
    try {
      await updateItem(itemId, newQty)
      if (newQty <= 0) toast('Item removed', 'success')
    } catch (err) {
      toast(getErrorMessage(err), 'error')
    }
  }

  const handleRemove = async (itemId) => {
    setRemovingId(itemId)
    try {
      await updateItem(itemId, 0)
      toast('Item removed from cart', 'success')
    } catch (err) {
      toast(getErrorMessage(err), 'error')
    }
    setRemovingId(null)
  }

  const handleClear = async () => {
    try {
      await clearCart()
      setCouponDiscount(0)
      setCouponCode('')
      setClearConfirm(false)
      toast('Cart cleared', 'success')
    } catch (err) {
      toast(getErrorMessage(err), 'error')
    }
  }

  const applyCoupon = async () => {
    if (!couponCode.trim()) return
    setCouponLoading(true)
    try {
      const res = await api.post('/cart/validate_coupon/', { code: couponCode })
      setCouponDiscount(res.data.discount)
      toast(`Coupon applied! You save ${formatPrice(res.data.discount)}`, 'success')
    } catch (err) {
      setCouponDiscount(0)
      toast(getErrorMessage(err), 'error')
    }
    setCouponLoading(false)
  }

  const removeCoupon = () => {
    setCouponDiscount(0)
    setCouponCode('')
    toast('Coupon removed', 'success')
  }

  const handleCheckout = () => {
    if (!user) {
      toast('Please sign in to continue', 'error')
      navigate('/login?next=/checkout')
      return
    }
    navigate('/checkout')
  }

  /* ── Spinner while cart loads ── */
  if (cartLoading) {
    return (
      <div className="container-gk" style={{ padding: '3rem 1.5rem' }}>
        <div className="gk-spinner" />
      </div>
    )
  }

  /* ── Empty cart ── */
  if (isEmpty) {
    return (
      <div className="container-gk" style={{ padding: '3rem 1.5rem' }}>
        <div className="gk-empty">
          <div className="gk-empty-icon">
            <i className="bi bi-cart3" style={{ fontSize: '3.5rem', opacity: 0.25 }} />
          </div>
          <h4>Your cart is empty</h4>
          <p>Looks like you haven't added anything yet. Explore restaurants and find something you love.</p>
          <Link to="/" className="btn-gk btn-gk-primary btn-gk-lg">
            <i className="bi bi-shop" /> Browse Restaurants
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container-gk" style={{ padding: '1.5rem' }}>

      {/* Page header */}
      <div className="gk-section-header" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Link to="/" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 4 }}>
            <i className="bi bi-arrow-left" /> Back
          </Link>
          <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.5rem', margin: 0 }}>
            My Cart
          </h1>
          <span style={{
            background: 'var(--primary)', color: 'var(--dark)',
            fontWeight: 800, fontSize: '0.75rem', borderRadius: 'var(--radius-pill)',
            padding: '2px 10px',
          }}>
            {cart.item_count} {cart.item_count === 1 ? 'item' : 'items'}
          </span>
        </div>
        <button
          className="btn-gk btn-gk-outline"
          style={{ fontSize: '0.8rem', padding: '8px 16px', color: 'var(--danger)', borderColor: 'var(--danger)' }}
          onClick={() => setClearConfirm(true)}
        >
          <i className="bi bi-trash3" /> Clear Cart
        </button>
      </div>

      {/* Free delivery progress bar */}
      {amountToFreeDelivery !== null && amountToFreeDelivery > 0 && (
        <div style={{
          background: 'var(--primary-light)', border: '1px solid var(--primary)',
          borderRadius: 'var(--radius)', padding: '0.875rem 1.25rem',
          marginBottom: '1.25rem', display: 'flex', flexDirection: 'column', gap: 8,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontWeight: 700 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <i className="bi bi-bicycle" style={{ color: 'var(--primary-dark)' }} />
              Add <strong style={{ color: 'var(--primary-dark)' }}>&nbsp;{formatPrice(amountToFreeDelivery)}&nbsp;</strong> more for free delivery!
            </span>
            <span style={{ color: 'var(--text-muted)' }}>{formatPrice(freeThreshold)}</span>
          </div>
          <div style={{ height: 6, background: 'var(--border)', borderRadius: 99, overflow: 'hidden' }}>
            <div style={{
              height: '100%', borderRadius: 99,
              background: 'var(--primary-dark)',
              width: `${Math.min((subtotal / freeThreshold) * 100, 100)}%`,
              transition: 'width 0.4s ease',
            }} />
          </div>
        </div>
      )}
      {freeThreshold && effectiveDeliveryFee === 0 && (
        <div style={{
          background: '#f0fdf4', border: '1px solid var(--success)',
          borderRadius: 'var(--radius)', padding: '0.75rem 1.25rem',
          marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: 8,
          fontSize: '0.82rem', fontWeight: 700, color: 'var(--success)',
        }}>
          <i className="bi bi-check-circle-fill" /> You've unlocked free delivery! 🎉
        </div>
      )}

      {/* Main grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'start' }}>

        {/* ── Left: items + restaurant ── */}
        <div>

          {/* Restaurant info bar */}
          {cart.restaurant && (
            <div style={{
              background: 'var(--white)', border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)', padding: '0.875rem 1.25rem',
              marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.875rem',
            }}>
              {cart.restaurant.logo ? (
                <img
                  src={cart.restaurant.logo}
                  alt={cart.restaurant.name}
                  style={{ width: 44, height: 44, borderRadius: 'var(--radius-sm)', objectFit: 'cover', border: '1px solid var(--border)', flexShrink: 0 }}
                />
              ) : (
                <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-sm)', background: 'var(--primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <i className="bi bi-shop" style={{ color: 'var(--primary-dark)', fontSize: '1.1rem' }} />
                </div>
              )}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>{cart.restaurant.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', gap: 12, marginTop: 2 }}>
                  <span><i className="bi bi-clock" /> {cart.restaurant.estimated_delivery_time} min</span>
                  {cart.restaurant.minimum_order > 0 && (
                    <span><i className="bi bi-bag" /> Min. {formatPrice(cart.restaurant.minimum_order)}</span>
                  )}
                </div>
              </div>
              <Link
                to={`/restaurants/${cart.restaurant.slug}`}
                style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--primary-dark)', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4 }}
              >
                Add more <i className="bi bi-plus-circle" />
              </Link>
            </div>
          )}

          {/* Cart items */}
          <div style={{
            background: 'var(--white)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', overflow: 'hidden',
          }}>
            {cart.items.map((item, idx) => {
              const menuItem = item.menu_item
              const isRemoving = removingId === item.id
              return (
                <div
                  key={item.id}
                  style={{
                    display: 'flex', gap: '1rem', padding: '1rem 1.25rem',
                    borderBottom: idx < cart.items.length - 1 ? '1px solid var(--border)' : 'none',
                    alignItems: 'center',
                    opacity: isRemoving ? 0.4 : 1,
                    transition: 'opacity 0.2s',
                  }}
                >
                  {/* Image */}
                  {menuItem?.image ? (
                    <img
                      src={menuItem.image}
                      alt={menuItem.name}
                      style={{ width: 72, height: 72, borderRadius: 'var(--radius-sm)', objectFit: 'cover', flexShrink: 0, background: 'var(--bg2)' }}
                    />
                  ) : (
                    <div style={{ width: 72, height: 72, borderRadius: 'var(--radius-sm)', background: 'var(--bg2)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <i className="bi bi-image" style={{ fontSize: '1.5rem', color: 'var(--text-light)' }} />
                    </div>
                  )}

                  {/* Info */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: 2 }}>{menuItem?.name || item.item_name}</div>
                    {item.special_instructions && (
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginBottom: 4 }}>
                        "{item.special_instructions}"
                      </div>
                    )}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--dark)' }}>
                        {formatPrice(menuItem?.price || 0)}
                      </span>
                      {menuItem?.compare_price && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textDecoration: 'line-through' }}>
                          {formatPrice(menuItem.compare_price)}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Qty control */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
                    <div className="gk-qty">
                      <button
                        className="gk-qty-btn"
                        onClick={() => handleQty(item.id, item.quantity - 1)}
                        disabled={isRemoving}
                        title="Decrease"
                      >
                        {item.quantity === 1 ? <i className="bi bi-trash3" style={{ fontSize: '0.8rem', color: 'var(--danger)' }} /> : '−'}
                      </button>
                      <span className="gk-qty-val">{item.quantity}</span>
                      <button
                        className="gk-qty-btn"
                        onClick={() => handleQty(item.id, item.quantity + 1)}
                        disabled={isRemoving}
                        title="Increase"
                      >
                        +
                      </button>
                    </div>
                    <div style={{ fontWeight: 800, fontSize: '0.9rem' }}>
                      {formatPrice(item.subtotal)}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Notes for restaurant */}
          <div style={{
            background: 'var(--white)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', padding: '1.25rem', marginTop: '1rem',
          }}>
            <label className="gk-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <i className="bi bi-chat-left-text" style={{ color: 'var(--primary-dark)' }} />
              Notes for restaurant (optional)
            </label>
            <textarea
              className="gk-input"
              rows={2}
              placeholder="e.g. No onions please, extra sauce on the side…"
              style={{ resize: 'none', fontSize: '0.85rem' }}
            />
          </div>
        </div>

        {/* ── Right: order summary ── */}
        <div style={{ position: 'sticky', top: 'calc(var(--navbar-height) + 1rem)' }}>
          <div style={{
            background: 'var(--white)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', overflow: 'hidden',
          }}>
            <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', background: 'var(--dark)' }}>
              <h5 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, color: '#fff', margin: 0, fontSize: '1rem' }}>
                Order Summary
              </h5>
            </div>

            <div style={{ padding: '1.25rem' }}>
              {/* Line items */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: '1rem' }}>
                <SummaryRow label="Subtotal" value={formatPrice(subtotal)} />
                <SummaryRow
                  label="Delivery fee"
                  value={effectiveDeliveryFee === 0
                    ? <span style={{ color: 'var(--success)', fontWeight: 700 }}>Free</span>
                    : formatPrice(effectiveDeliveryFee)}
                />
                {couponDiscount > 0 && (
                  <SummaryRow
                    label={
                      <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        Coupon discount
                        <button onClick={removeCoupon} style={{ color: 'var(--danger)', fontSize: '0.72rem', fontWeight: 700 }}>
                          ✕ Remove
                        </button>
                      </span>
                    }
                    value={<span style={{ color: 'var(--success)' }}>− {formatPrice(couponDiscount)}</span>}
                  />
                )}
              </div>

              {/* Total */}
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                borderTop: '2px solid var(--border)', paddingTop: '0.875rem', marginBottom: '1.25rem',
              }}>
                <span style={{ fontWeight: 800, fontSize: '1rem' }}>Total</span>
                <span style={{ fontWeight: 900, fontSize: '1.2rem', color: 'var(--primary-dark)' }}>
                  {formatPrice(total)}
                </span>
              </div>

              {/* Coupon input */}
              {couponDiscount === 0 && (
                <div style={{ marginBottom: '1.25rem' }}>
                  <label className="gk-label">
                    <i className="bi bi-tag" style={{ marginRight: 4, color: 'var(--primary-dark)' }} />
                    Have a coupon?
                  </label>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <input
                      className="gk-input"
                      placeholder="Enter code"
                      value={couponCode}
                      onChange={e => setCouponCode(e.target.value.toUpperCase())}
                      onKeyDown={e => e.key === 'Enter' && applyCoupon()}
                      style={{ flex: 1, fontSize: '0.82rem', letterSpacing: '0.5px' }}
                    />
                    <button
                      className="btn-gk btn-gk-dark"
                      onClick={applyCoupon}
                      disabled={couponLoading || !couponCode.trim()}
                      style={{ padding: '8px 14px', fontSize: '0.8rem', whiteSpace: 'nowrap' }}
                    >
                      {couponLoading ? <i className="bi bi-hourglass-split" /> : 'Apply'}
                    </button>
                  </div>
                </div>
              )}

              {/* Minimum order warning */}
              {cart.restaurant?.minimum_order > 0 && subtotal < Number(cart.restaurant.minimum_order) && (
                <div className="gk-cart-min-note" style={{ marginBottom: '0.875rem', fontSize: '0.78rem' }}>
                  <i className="bi bi-exclamation-triangle" />
                  &nbsp;Minimum order is {formatPrice(cart.restaurant.minimum_order)}. Add {formatPrice(Number(cart.restaurant.minimum_order) - subtotal)} more.
                </div>
              )}

              {/* Checkout CTA */}
              <button
                className="btn-gk btn-gk-primary btn-gk-full btn-gk-lg"
                onClick={handleCheckout}
                disabled={
                  cart.restaurant?.minimum_order > 0 &&
                  subtotal < Number(cart.restaurant.minimum_order)
                }
                style={{ justifyContent: 'center', fontSize: '1rem' }}
              >
                <i className="bi bi-lock-fill" style={{ fontSize: '0.9rem' }} />
                Checkout — {formatPrice(total)}
              </button>

              {!user && (
                <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  <Link to="/login" style={{ color: 'var(--primary-dark)', fontWeight: 700 }}>Sign in</Link> to save your order history
                </p>
              )}
            </div>
          </div>

          {/* Trust badges */}
          <div style={{
            marginTop: '1rem', display: 'flex', justifyContent: 'center', gap: '1.5rem',
            fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600,
          }}>
            {[
              ['bi-shield-check', 'Secure checkout'],
              ['bi-arrow-counterclockwise', 'Easy returns'],
              ['bi-headset', '24/7 support'],
            ].map(([icon, label]) => (
              <span key={label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <i className={`bi ${icon}`} style={{ color: 'var(--primary-dark)' }} />
                {label}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Clear cart confirm modal */}
      {clearConfirm && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)',
          zIndex: 2000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem',
        }}
          onClick={() => setClearConfirm(false)}
        >
          <div
            style={{
              background: 'var(--white)', borderRadius: 'var(--radius-lg)',
              padding: '2rem', maxWidth: 380, width: '100%', textAlign: 'center',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🗑️</div>
            <h5 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.1rem', marginBottom: '0.5rem' }}>
              Clear your cart?
            </h5>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
              This will remove all {cart.item_count} items from your cart. This action can't be undone.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <button className="btn-gk btn-gk-outline" onClick={() => setClearConfirm(false)}>
                Keep items
              </button>
              <button
                className="btn-gk"
                style={{ background: 'var(--danger)', color: '#fff' }}
                onClick={handleClear}
              >
                <i className="bi bi-trash3" /> Clear cart
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Helper ── */
function SummaryRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
      <span style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ fontWeight: 600 }}>{value}</span>
    </div>
  )
}