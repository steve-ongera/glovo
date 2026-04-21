import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function Navbar({ onMenuOpen }) {
  const { user } = useAuth()
  const { cart, setCartOpen } = useCart()
  const navigate = useNavigate()
  const [q, setQ] = useState('')

  const handleSearch = (e) => {
    e.preventDefault()
    if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <nav className="gk-navbar">
      <div className="inner">
        <button className="gk-hamburger" onClick={onMenuOpen} aria-label="Menu">
          <span /><span /><span />
        </button>

        <Link to="/" className="gk-logo">Glovo<span>KE</span></Link>

        <div className="gk-search">
          <form onSubmit={handleSearch}>
            <input placeholder="Search restaurants..." value={q} onChange={e => setQ(e.target.value)} />
            <button type="submit" className="gk-search-btn"><i className="bi bi-search"></i></button>
          </form>
        </div>

        <div className="gk-nav-actions">
          <Link to="/" className="gk-nav-btn"><i className="bi bi-house-fill"></i><span>Home</span></Link>
          {user ? (
            <Link to="/profile" className="gk-nav-btn"><i className="bi bi-person-circle"></i><span>{user.first_name}</span></Link>
          ) : (
            <Link to="/login" className="gk-nav-btn"><i className="bi bi-person"></i><span>Login</span></Link>
          )}
          <Link to="/orders" className="gk-nav-btn"><i className="bi bi-receipt"></i><span>Orders</span></Link>
          <button className="gk-nav-btn" onClick={() => setCartOpen(true)} style={{ background: 'none', border: 'none' }}>
            <i className="bi bi-bag-fill"></i>
            <span>Cart</span>
            {cart.item_count > 0 && <span className="badge">{cart.item_count > 99 ? '99+' : cart.item_count}</span>}
          </button>
        </div>
      </div>
    </nav>
  )
}