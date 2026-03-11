import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { ShoppingCart, Plus, Minus } from 'lucide-react';

interface Product {
  id: number;
  sku: string;
  name: string;
  price: string;
  quantity: number;
}

interface CartItem extends Product {
  cartQuantity: number;
}

export const Dashboard: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkoutStatus, setCheckoutStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await apiClient.get('/inventory/');
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product: Product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item =>
          item.id === product.id
            ? { ...item, cartQuantity: Math.min(item.cartQuantity + 1, product.quantity) }
            : item
        );
      }
      return [...prev, { ...product, cartQuantity: 1 }];
    });
  };

  const updateCartQuantity = (id: number, delta: number) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQuantity = Math.max(0, Math.min(item.cartQuantity + delta, item.quantity));
        return { ...item, cartQuantity: newQuantity };
      }
      return item;
    }).filter(item => item.cartQuantity > 0));
  };

  const cartTotal = cart.reduce((total, item) => total + (parseFloat(item.price) * item.cartQuantity), 0);

  const handleCheckout = async () => {
    if (cart.length === 0) return;

    setCheckoutStatus('loading');
    try {
      await apiClient.post('/orders/', {
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.cartQuantity
        }))
      });
      setCart([]);
      setCheckoutStatus('success');
      fetchProducts(); // Refresh inventory
      setTimeout(() => setCheckoutStatus('idle'), 3000);
    } catch (error) {
      console.error('Checkout failed', error);
      setCheckoutStatus('error');
      setTimeout(() => setCheckoutStatus('idle'), 3000);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Products Grid */}
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Products</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map(product => (
              <div key={product.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{product.name}</h3>
                      <p className="text-sm text-gray-500">SKU: {product.sku}</p>
                    </div>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ${parseFloat(product.price).toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      {product.quantity} in stock
                    </span>
                    <button
                      onClick={() => addToCart(product)}
                      disabled={product.quantity === 0}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cart Sidebar */}
        <div className="w-full lg:w-96">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 sticky top-6">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900 flex items-center">
                <ShoppingCart className="h-5 w-5 mr-2 text-gray-500" />
                Your Cart
              </h2>
              <span className="bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                {cart.reduce((acc, item) => acc + item.cartQuantity, 0)} items
              </span>
            </div>

            <div className="p-6">
              {cart.length === 0 ? (
                <p className="text-gray-500 text-center py-4">Your cart is empty</p>
              ) : (
                <ul className="space-y-4">
                  {cart.map(item => (
                    <li key={item.id} className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-gray-900">{item.name}</h4>
                        <p className="text-sm text-gray-500">${parseFloat(item.price).toFixed(2)}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => updateCartQuantity(item.id, -1)}
                          className="p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
                        >
                          <Minus className="h-4 w-4" />
                        </button>
                        <span className="text-sm font-medium text-gray-900 w-4 text-center">
                          {item.cartQuantity}
                        </span>
                        <button
                          onClick={() => updateCartQuantity(item.id, 1)}
                          disabled={item.cartQuantity >= item.quantity}
                          className="p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 disabled:opacity-50"
                        >
                          <Plus className="h-4 w-4" />
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-lg">
              <div className="flex justify-between text-base font-medium text-gray-900 mb-4">
                <p>Total</p>
                <p>${cartTotal.toFixed(2)}</p>
              </div>
              <button
                onClick={handleCheckout}
                disabled={cart.length === 0 || checkoutStatus === 'loading'}
                className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {checkoutStatus === 'loading' ? 'Processing...' : 'Checkout'}
              </button>

              {checkoutStatus === 'success' && (
                <p className="mt-2 text-sm text-green-600 text-center">Order placed successfully!</p>
              )}
              {checkoutStatus === 'error' && (
                <p className="mt-2 text-sm text-red-600 text-center">Failed to place order.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
