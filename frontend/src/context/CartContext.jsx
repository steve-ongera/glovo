import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../utils/api'

const CartContext = createContext(null)

const EMPTY_CART = { id: null, restaurant: null, items: [], total: 0, item_count: 0 }

export function CartProvider({ children }) {
  const [cart, setCart] = useState(EMPTY_CART)
  const [cartOpen, setCartOpen] = useState(false)

  useEffect(() => {
    api.get('/cart/').then(res => setCart(res.data)).catch(() => {})
  }, [])

  const refreshCart = async () => {
    const res = await api.get('/cart/')
    setCart(res.data)
    return res.data
  }

  const addItem = async (menuItemId, quantity = 1, instructions = '') => {
    const res = await api.post('/cart/add/', { menu_item_id: menuItemId, quantity, special_instructions: instructions })
    setCart(res.data)
    setCartOpen(true)
    return res.data
  }

  const updateItem = async (itemId, quantity) => {
    const res = await api.post('/cart/update_item/', { item_id: itemId, quantity })
    setCart(res.data)
    return res.data
  }

  const clearCart = async () => {
    const res = await api.post('/cart/clear/')
    setCart(res.data)
  }

  return (
    <CartContext.Provider value={{ cart, cartOpen, setCartOpen, addItem, updateItem, clearCart, refreshCart }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => useContext(CartContext)