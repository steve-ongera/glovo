import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useCart } from '../context/CartContext'

export default function BottomNav() {
  const { pathname } = useLocation()
  const { cart, setCartOpen } = useCart()

  return (
    <div className="gk-bottom-nav">
      <div className="gk-bottom-nav-inner">
        <Link to="/" className={`gk-bnav-item ${pathname === '/' ? 'active' : ''}`}>
          <i className="bi bi-house-fill"></i><span>Home</span>
        </Link>
        <Link to="/search" className={`gk-bnav-item ${pathname === '/search' ? 'active' : ''}`}>
          <i className="bi bi-search"></i><span>Search</span>
        </Link>
        <button className="gk-bnav-item" onClick={() => setCartOpen(true)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
          <i className="bi bi-bag-fill"></i>
          <span>Cart</span>
          {cart.item_count > 0 && <span className="badge">{cart.item_count}</span>}
        </button>
        <Link to="/orders" className={`gk-bnav-item ${pathname.startsWith('/orders') ? 'active' : ''}`}>
          <i className="bi bi-receipt"></i><span>Orders</span>
        </Link>
        <Link to="/profile" className={`gk-bnav-item ${pathname === '/profile' ? 'active' : ''}`}>
          <i className="bi bi-person-fill"></i><span>Profile</span>
        </Link>
      </div>
    </div>
  )
}