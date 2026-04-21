import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { getErrorMessage } from '../utils/api'

export default function RegisterPage() {
  const { register } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', password: '', password2: '' })
  const [loading, setLoading] = useState(false)
  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.password2) { toast('Passwords do not match', 'error'); return }
    setLoading(true)
    try {
      await register(form)
      toast('Account created!', 'success')
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
          <p>Create your account</p>
        </div>
        <div className="gk-auth-body">
          <form onSubmit={handleSubmit}>
            <div className="row g-3" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label className="gk-label">First Name</label>
                <input className="gk-input" value={form.first_name} onChange={set('first_name')} placeholder="Jane" required />
              </div>
              <div>
                <label className="gk-label">Last Name</label>
                <input className="gk-input" value={form.last_name} onChange={set('last_name')} placeholder="Doe" required />
              </div>
            </div>
            {[
              { k: 'email', label: 'Email', type: 'email', ph: 'you@example.com' },
              { k: 'phone', label: 'Phone', type: 'tel', ph: '+254 7XX XXX XXX' },
              { k: 'password', label: 'Password', type: 'password', ph: '••••••••' },
              { k: 'password2', label: 'Confirm Password', type: 'password', ph: '••••••••' },
            ].map(({ k, label, type, ph }) => (
              <div key={k} style={{ marginBottom: '1rem' }}>
                <label className="gk-label">{label}</label>
                <input className="gk-input" type={type} value={form[k]} onChange={set(k)} placeholder={ph} required={k !== 'phone'} />
              </div>
            ))}
            <button type="submit" className="btn-gk btn-gk-primary btn-gk-full btn-gk-lg" disabled={loading}>
              {loading ? <><i className="bi bi-hourglass-split"></i> Creating account...</> : <><i className="bi bi-person-plus"></i> Create Account</>}
            </button>
          </form>
          <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Already have an account? <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 700 }}>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}