import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import api from '../utils/api'
import { useToast } from '../context/ToastContext'

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ first_name: user?.first_name || '', last_name: user?.last_name || '', phone: user?.phone || '' })
  const [saving, setSaving] = useState(false)

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.patch('/auth/profile/', form)
      toast('Profile updated', 'success')
    } catch {
      toast('Failed to update profile', 'error')
    }
    setSaving(false)
  }

  const handleLogout = () => { logout(); navigate('/') }

  return (
    <div className="container-gk" style={{ padding: '1.5rem', maxWidth: 600 }}>
      <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.5rem', marginBottom: '1.5rem' }}>Profile</h1>

      {/* Avatar */}
      <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.5rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ width: 60, height: 60, borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: '1.5rem', color: 'var(--dark)', flexShrink: 0 }}>
          {user?.first_name?.[0]}
        </div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '1rem' }}>{user?.first_name} {user?.last_name}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>{user?.email}</div>
        </div>
      </div>

      {/* Edit form */}
      <form onSubmit={handleSave} style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', marginBottom: '1rem' }}>
        <h5 style={{ fontWeight: 800, marginBottom: '1rem' }}>Edit Profile</h5>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label className="gk-label">First Name</label>
            <input className="gk-input" value={form.first_name} onChange={e => setForm(p => ({ ...p, first_name: e.target.value }))} />
          </div>
          <div>
            <label className="gk-label">Last Name</label>
            <input className="gk-input" value={form.last_name} onChange={e => setForm(p => ({ ...p, last_name: e.target.value }))} />
          </div>
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label className="gk-label">Phone</label>
          <input className="gk-input" value={form.phone} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))} placeholder="+254 7XX XXX XXX" />
        </div>
        <button type="submit" className="btn-gk btn-gk-primary" disabled={saving}>
          {saving ? 'Saving...' : <><i className="bi bi-check-circle"></i> Save Changes</>}
        </button>
      </form>

      {/* Quick links */}
      <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden', marginBottom: '1rem' }}>
        {[
          { to: '/orders', icon: 'bi-receipt', label: 'My Orders' },
        ].map(item => (
          <Link key={item.to} to={item.to} style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)', color: 'var(--text)', fontWeight: 600, fontSize: '0.875rem' }}>
            <i className={`bi ${item.icon}`} style={{ color: 'var(--primary)', fontSize: '1.1rem' }}></i>
            {item.label}
            <i className="bi bi-chevron-right" style={{ marginLeft: 'auto', color: 'var(--text-muted)' }}></i>
          </Link>
        ))}
        <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', padding: '1rem 1.25rem', width: '100%', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--danger)', fontWeight: 600, fontSize: '0.875rem' }}>
          <i className="bi bi-box-arrow-right" style={{ fontSize: '1.1rem' }}></i> Logout
        </button>
      </div>
    </div>
  )
}