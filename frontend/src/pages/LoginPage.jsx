import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { getErrorMessage } from '../utils/api'

export default function LoginPage() {
  const { login } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(form.email, form.password)
      toast('Welcome back!', 'success')
      navigate('/')
    } catch (err) {
      toast(getErrorMessage(err), 'error')
    }
    setLoading(false)
  }

  return (
    <div className="gk-auth-page">
      <div className="gk-auth-card">
        <div className="gk-auth-header">
          <div className="logo">GlovoKE</div>
          <p>Sign in to your account</p>
        </div>
        <div className="gk-auth-body">
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label className="gk-label">Email</label>
              <input className="gk-input" type="email" value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} placeholder="you@example.com" required />
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <label className="gk-label">Password</label>
              <input className="gk-input" type="password" value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} placeholder="••••••••" required />
            </div>
            <button type="submit" className="btn-gk btn-gk-primary btn-gk-full btn-gk-lg" disabled={loading}>
              {loading ? <><i className="bi bi-hourglass-split"></i> Signing in...</> : <><i className="bi bi-box-arrow-in-right"></i> Sign In</>}
            </button>
          </form>
          <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Don't have an account? <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 700 }}>Create one</Link>
          </p>
        </div>
      </div>
    </div>
  )
}