import React from 'react'
import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { formatPrice } from '../utils/api'

export default function CartDrawer() {
  const { cart, cartOpen, setCartOpen, updateItem, clearCart } = useCart()

  const deliveryFee = cart.restaurant ? Number(cart.restaurant.delivery_fee) : 0
  const total = Number(cart.total) + deliveryFee
  const minOrder = cart.restaurant ? Number(cart.restaurant.minimum_order) : 0
  const belowMin = Number(cart.total) < minOrder && minOrder > 0

  return (
    <>
      <div className={`gk-cart-overlay ${cartOpen ? 'open' : ''}`} onClick={() => setCartOpen(false)} />
      <div className={`gk-cart-drawer ${cartOpen ? 'open' : ''}`}>
        <div className="gk-cart-header">
          <h4>Your Cart</h4>
          <button className="gk-cart-close" onClick={() => setCartOpen(false)}><i className="bi bi-x-lg"></i></button>
        </div>

        {cart.restaurant && (
          <div className="gk-cart-restaurant">
            <i className="bi bi-shop"></i>
            {cart.restaurant.name}
            <button onClick={clearCart} style={{ marginLeft: 'auto', fontSize: '0.72rem', color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 700 }}>
              Clear
            </button>
          </div>
        )}

        <div className="gk-cart-body">
          {cart.items.length === 0 ? (
            <div className="gk-empty" style={{ padding: '3rem 1rem' }}>
              <div className="gk-empty-icon"><i className="bi bi-bag-x"></i></div>
              <h4>Your cart is empty</h4>
              <p>Add items from a restaurant to get started</p>
            </div>
          ) : (
            cart.items.map(item => (
              <div key={item.id} className="gk-cart-item">
                {item.menu_item?.image
                  ? <img src={item.menu_item.image} alt="" className="gk-cart-item-img" />
                  : <div className="gk-cart-item-img" style={{ background: 'var(--bg2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><i className="bi bi-egg-fried" style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}></i></div>
                }
                <div className="gk-cart-item-info">
                  <div className="gk-cart-item-name">{item.menu_item?.name}</div>
                  <div className="gk-cart-item-price">{formatPrice(item.menu_item?.price)} each</div>
                </div>
                <div className="gk-qty">
                  <button className="gk-qty-btn" onClick={() => updateItem(item.id, item.quantity - 1)}>−</button>
                  <span className="gk-qty-val">{item.quantity}</span>
                  <button className="gk-qty-btn" onClick={() => updateItem(item.id, item.quantity + 1)}>+</button>
                </div>
              </div>
            ))
          )}
        </div>

        {cart.items.length > 0 && (
          <div className="gk-cart-footer">
            <div className="gk-cart-summary-row"><span>Subtotal</span><span>{formatPrice(cart.total)}</span></div>
            <div className="gk-cart-summary-row">
              <span>Delivery</span>
              <span style={{ color: deliveryFee === 0 ? 'var(--success)' : 'inherit' }}>
                {deliveryFee === 0 ? 'Free' : formatPrice(deliveryFee)}
              </span>
            </div>
            <div className="gk-cart-summary-row total"><span>Total</span><span>{formatPrice(total)}</span></div>
            {belowMin && (
              <div className="gk-cart-min-note">
                <i className="bi bi-info-circle"></i> Minimum order is {formatPrice(minOrder)}
              </div>
            )}
            <Link
              to="/checkout"
              onClick={() => setCartOpen(false)}
              className="btn-gk btn-gk-primary btn-gk-full btn-gk-lg"
              style={{ marginTop: '0.75rem', pointerEvents: belowMin ? 'none' : 'auto', opacity: belowMin ? 0.5 : 1 }}>
              <i className="bi bi-arrow-right-circle"></i> Checkout — {formatPrice(total)}
            </Link>
          </div>
        )}
      </div>
    </>
  )
}