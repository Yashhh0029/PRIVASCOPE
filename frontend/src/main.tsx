import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Handle Google OAuth popup redirect: send token to opener and self-close
if (window.opener && window.location.hash) {
  const hash = window.location.hash.substring(1);
  const params = new URLSearchParams(hash);
  const token = params.get('id_token') || params.get('access_token');
  if (token) {
    try {
      window.opener.postMessage({ type: 'GOOGLE_AUTH_SUCCESS', token }, window.location.origin);
    } catch (e) {
      console.error('Failed to postMessage to opener:', e);
    }
    window.close();
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
