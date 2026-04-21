import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import api, { formatPrice, getErrorMessage } from '../utils/api'

const STEPS = ['Address', 'Payment', 'Review']

export default function CheckoutPage() {
  const { cart, clearCart } = useCart()
  const { user } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [counties, setCounties] = useState([])
  const [zones, setZones] = useState([])
  const [loading, setLoading] = useState(false)
  const [couponCode, setCouponCode] = useState('')
  const [couponDiscount, setCouponDiscount] = useState(0)
  const [couponLoading, setCouponLoading] = useState(false)

  const [form, setForm] = useState({
    delivery_street: '',
    delivery_town: '',
    delivery_county_id: null,
    delivery_zone_id: null,
    delivery_instructions: '',
    customer_name: user ? `${user.first_name} ${user.last_name}`.trim() : '',
    customer_email: user?.email || '',
    customer_phone: user?.phone || '',
    payment_method: 'mpesa',
    notes: '',
  })

  useEffect(() => {
    document.title = 'Checkout | GlovoKE'
    api.get('/counties/').then(res => setCounties(res.data.results || res.data))
  }, [])

  useEffect(() => {
    if (form.delivery_county_id) {
      api.get(`/zones/?county_id=${form.delivery_county_id}`).then(res => setZones(res.data.results || res.data))
    } else {
      setZones([])
    }
  }, [form.delivery_county_id])

  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const deliveryFee = () => {
    if (form.delivery_zone_id) {
      const z = zones.find(z => z.id === Number(form.delivery_zone_id))
      return z ? Number(z.delivery_fee) : 0
    }
    return cart.restaurant ? Number(cart.restaurant.delivery_fee) : 0
  }

  const subtotal = Number(cart.total)
  const fee = deliveryFee()
  const total = subtotal + fee - couponDiscount

  const applyCoupon = async () => {
    if (!couponCode.trim()) return
    setCouponLoading(true)
    try {
      const res = await api.post('/cart/validate_coupon/', { code: couponCode })
      setCouponDiscount(res.data.discount)
      toast(`Coupon applied! You save ${formatPrice(res.data.discount)}`, 'success')
    } catch (err) {
      toast(getErrorMessage(err), 'error')
    }
    setCouponLoading(false)
  }

  const validateStep0 = () => {
    if (!form.delivery_street.trim()) { toast('Enter your street address', 'error'); return false }
    if (!form.delivery_town.trim()) { toast('Enter your town/area', 'error'); return false }
    if (!form.delivery_county_id) { toast('Select your county', 'error'); return false }
    if (!form.customer_name.trim() || !form.customer_phone.trim() || !form.customer_email.trim()) {
      toast('Fill in all contact details', 'error'); return false
    }
    return true
  }

  const placeOrder = async () => {
    setLoading(true)
    try {
      const payload = { ...form, coupon_code: couponCode, delivery_county_id: Number(form.delivery_county_id) }
      const res = await api.post('/orders/', payload)
      await clearCart()
      toast('Order placed successfully!', 'success')
      navigate(`/orders/${res.data.id}`)
    } catch (err) {
      toast(getErrorMessage(err), 'error')
    }
    setLoading(false)
  }

  const Summary = () => (
    <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', position: 'sticky', top: 'calc(var(--navbar-height) + 1rem)' }}>
      <h5 style={{ fontWeight: 800, marginBottom: '1rem', fontSize: '0.95rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border)' }}>
        {cart.restaurant?.name}
      </h5>
      {cart.items.map(item => (
        <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.5rem' }}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '60%' }}>{item.menu_item?.name} × {item.quantity}</span>
          <span style={{ fontWeight: 700 }}>{formatPrice(item.subtotal)}</span>
        </div>
      ))}
      <div style={{ borderTop: '1px solid var(--border)', paddingTop: '0.75rem', marginTop: '0.5rem' }}>
        {[['Subtotal', formatPrice(subtotal)], ['Delivery', fee === 0 ? 'Free' : formatPrice(fee)]].map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: 4 }}>
            <span style={{ color: 'var(--text-muted)' }}>{k}</span><span>{v}</span>
          </div>
        ))}
        {couponDiscount > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--success)', marginBottom: 4 }}>
            <span>Discount</span><span>− {formatPrice(couponDiscount)}</span>
          </div>
        )}
        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: '1rem', borderTop: '1px solid var(--border)', paddingTop: '0.75rem', marginTop: 4 }}>
          <span>Total</span><span style={{ color: 'var(--primary)' }}>{formatPrice(total)}</span>
        </div>
      </div>
      <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
        <label className="gk-label">Coupon Code</label>
        <div style={{ display: 'flex', gap: 6 }}>
          <input className="gk-input" placeholder="Enter code" value={couponCode} onChange={e => setCouponCode(e.target.value)} style={{ flex: 1, fontSize: '0.82rem' }} />
          <button className="btn-gk btn-gk-outline" onClick={applyCoupon} disabled={couponLoading} style={{ padding: '8px 12px', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
            Apply
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="container-gk" style={{ padding: '1.5rem' }}>
      <h1 style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.5rem', marginBottom: '1.5rem' }}>Checkout</h1>

      {/* Steps */}
      <div className="gk-step-indicator" style={{ marginBottom: '2rem' }}>
        {STEPS.map((s, i) => (
          <React.Fragment key={s}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
              <div className={`gk-step-dot ${i < step ? 'done' : ''} ${i === step ? 'active' : ''}`}>
                {i < step ? <i className="bi bi-check-lg"></i> : i + 1}
              </div>
              <span className={`gk-step-label ${i === step ? 'active' : ''}`}>{s}</span>
            </div>
            {i < STEPS.length - 1 && <div className={`gk-step-line ${i < step ? 'done' : ''}`}></div>}
          </React.Fragment>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'start' }}>
        <div>
          {/* Step 0: Address */}
          {step === 0 && (
            <div>
              <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', marginBottom: '1rem' }}>
                <h5 style={{ fontWeight: 800, marginBottom: '1rem' }}>Contact Details</h5>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label className="gk-label">Full Name</label>
                    <input className="gk-input" value={form.customer_name} onChange={set('customer_name')} placeholder="Full name" />
                  </div>
                  <div>
                    <label className="gk-label">Phone</label>
                    <input className="gk-input" value={form.customer_phone} onChange={set('customer_phone')} placeholder="+254 7XX XXX XXX" />
                  </div>
                </div>
                <div>
                  <label className="gk-label">Email</label>
                  <input className="gk-input" type="email" value={form.customer_email} onChange={set('customer_email')} placeholder="email@example.com" />
                </div>
              </div>

              <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', marginBottom: '1rem' }}>
                <h5 style={{ fontWeight: 800, marginBottom: '1rem' }}>Delivery Address</h5>
                <div style={{ marginBottom: '1rem' }}>
                  <label className="gk-label">Street / Building</label>
                  <input className="gk-input" value={form.delivery_street} onChange={set('delivery_street')} placeholder="e.g. Kenyatta Ave, Nairobi Tower 3rd Floor" />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <label className="gk-label">Town / Area</label>
                    <input className="gk-input" value={form.delivery_town} onChange={set('delivery_town')} placeholder="e.g. Westlands" />
                  </div>
                  <div>
                    <label className="gk-label">County</label>
                    <select className="gk-input" value={form.delivery_county_id || ''} onChange={e => setForm(p => ({ ...p, delivery_county_id: e.target.value, delivery_zone_id: null }))}>
                      <option value="">Select county</option>
                      {counties.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                </div>
                {zones.length > 0 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <label className="gk-label">Delivery Zone ({zones.length} available)</label>
                    <select className="gk-input" value={form.delivery_zone_id || ''} onChange={e => setForm(p => ({ ...p, delivery_zone_id: e.target.value }))}>
                      <option value="">Select zone (optional)</option>
                      {zones.map(z => <option key={z.id} value={z.id}>{z.name} — {formatPrice(z.delivery_fee)} · ~{z.estimated_minutes} min</option>)}
                    </select>
                  </div>
                )}
                <div>
                  <label className="gk-label">Delivery Instructions (optional)</label>
                  <textarea className="gk-input" rows={2} value={form.delivery_instructions} onChange={set('delivery_instructions')} placeholder="e.g. Call when you arrive, gate code is 1234"></textarea>
                </div>
              </div>

              <button className="btn-gk btn-gk-primary btn-gk-lg" onClick={() => { if (validateStep0()) setStep(1) }}>
                Continue to Payment <i className="bi bi-arrow-right"></i>
              </button>
            </div>
          )}

          {/* Step 1: Payment */}
          {step === 1 && (
            <div>
              <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem' }}>
                <h5 style={{ fontWeight: 800, marginBottom: '1rem' }}>Payment Method</h5>
                {[
                  { value: 'mpesa', label: 'M-Pesa', icon: 'bi-phone', desc: 'Pay via M-Pesa Paybill or Till' },
                  { value: 'card', label: 'Credit / Debit Card', icon: 'bi-credit-card', desc: 'Visa, Mastercard' },
                  { value: 'cod', label: 'Cash on Delivery', icon: 'bi-cash-stack', desc: 'Pay when your order arrives' },
                ].map(opt => (
                  <div key={opt.value} onClick={() => setForm(p => ({ ...p, payment_method: opt.value }))}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem',
                      marginBottom: '0.75rem', cursor: 'pointer', borderRadius: 'var(--radius)',
                      border: `2px solid ${form.payment_method === opt.value ? 'var(--primary)' : 'var(--border)'}`,
                      background: form.payment_method === opt.value ? 'var(--primary-xlight)' : 'var(--white)',
                      transition: 'var(--transition)',
                    }}>
                    <i className={`bi ${opt.icon}`} style={{ fontSize: '1.4rem', color: form.payment_method === opt.value ? 'var(--primary-dark)' : 'var(--text-muted)', flexShrink: 0 }}></i>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 700 }}>{opt.label}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{opt.desc}</div>
                    </div>
                    <div style={{ width: 20, height: 20, borderRadius: '50%', border: `2px solid ${form.payment_method === opt.value ? 'var(--primary)' : 'var(--border)'}`, background: form.payment_method === opt.value ? 'var(--primary)' : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      {form.payment_method === opt.value && <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--dark)' }}></div>}
                    </div>
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button className="btn-gk btn-gk-outline" onClick={() => setStep(0)}><i className="bi bi-arrow-left"></i> Back</button>
                <button className="btn-gk btn-gk-primary btn-gk-lg" onClick={() => setStep(2)}>Review Order <i className="bi bi-arrow-right"></i></button>
              </div>
            </div>
          )}

          {/* Step 2: Review */}
          {step === 2 && (
            <div>
              <div style={{ background: 'var(--white)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '1.25rem', marginBottom: '1rem' }}>
                <h5 style={{ fontWeight: 800, marginBottom: '1rem' }}>Confirm Details</h5>
                <table style={{ width: '100%', fontSize: '0.875rem' }}>
                  <tbody>
                    {[
                      ['Name', form.customer_name],
                      ['Phone', form.customer_phone],
                      ['Address', `${form.delivery_street}, ${form.delivery_town}`],
                      ['Payment', form.payment_method.toUpperCase()],
                      ['Delivery fee', fee === 0 ? 'Free' : formatPrice(fee)],
                    ].map(([k, v]) => (
                      <tr key={k}>
                        <td style={{ padding: '6px 0', color: 'var(--text-muted)', width: '35%' }}>{k}</td>
                        <td style={{ padding: '6px 0', fontWeight: 600 }}>{v}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button className="btn-gk btn-gk-outline" onClick={() => setStep(1)}><i className="bi bi-arrow-left"></i> Back</button>
                <button className="btn-gk btn-gk-primary btn-gk-lg" style={{ flex: 1, justifyContent: 'center' }} onClick={placeOrder} disabled={loading}>
                  {loading ? <><i className="bi bi-hourglass-split"></i> Placing Order...</> : <><i className="bi bi-check-circle"></i> Place Order — {formatPrice(total)}</>}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Summary sidebar */}
        <div>
          <Summary />
        </div>
      </div>
    </div>
  )
}