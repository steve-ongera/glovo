import React, { createContext, useContext, useState, useCallback } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const toast = useCallback((message, type = 'default', duration = 3000) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), duration)
  }, [])

  const icons = { error: 'bi-x-circle-fill', success: 'bi-check-circle-fill', default: 'bi-info-circle-fill' }

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="gk-toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`gk-toast ${t.type}`}>
            <i className={`bi ${icons[t.type] || icons.default}`}></i>
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)