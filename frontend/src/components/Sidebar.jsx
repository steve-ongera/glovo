import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); onClose(); navigate('/') }

  return (
    <>
      <div className={`gk-sidebar-overlay ${open ? 'open' : ''}`} onClick={onClose} />
      <div className={`gk-sidebar ${open ? 'open' : ''}`}>
        <div className="gk-sidebar-header">
          <span className="gk-logo" style={{ fontSize: '1.3rem' }}>Glovo<span style={{ color: '#fff' }}>KE</span></span>
          <button className="gk-sidebar-close" onClick={onClose}><i className="bi bi-x-lg"></i></button>
        </div>

        {user && (
          <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #2d2d2d' }}>
            <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.75rem', marginBottom: 4 }}>Signed in as</div>
            <div style={{ color: '#fff', fontWeight: 700 }}>{user.first_name} {user.last_name}</div>
            <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.78rem' }}>{user.email}</div>
          </div>
        )}

        <nav className="gk-sidebar-nav">
          {[
            { to: '/', icon: 'bi-house-fill', label: 'Home' },
            { to: '/orders', icon: 'bi-receipt', label: 'My Orders' },
            { to: '/profile', icon: 'bi-person-circle', label: 'Profile' },
          ].map(item => (
            <Link key={item.to} to={item.to} onClick={onClose}>
              <i className={`bi ${item.icon}`}></i> {item.label}
            </Link>
          ))}
          {user ? (
            <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', padding: '0.75rem 1.25rem', fontSize: '0.875rem', fontWeight: 600, color: 'rgba(255,255,255,0.8)', width: '100%', background: 'none', border: 'none', cursor: 'pointer' }}>
              <i className="bi bi-box-arrow-right" style={{ color: 'var(--primary)', width: 20, fontSize: '1.1rem' }}></i> Logout
            </button>
          ) : (
            <Link to="/login" onClick={onClose}><i className="bi bi-person"></i> Login</Link>
          )}
        </nav>
      </div>
    </>
  )
}