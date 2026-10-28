import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Loader2 } from 'lucide-react';

interface GoogleSignInButtonProps {
  onSuccess: (credential: string) => void;
  onError: (error: string) => void;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          renderButton: (parent: HTMLElement, options: any) => void;
          prompt: (momentListener?: (notification: any) => void) => void;
        };
        oauth2: {
          initTokenClient: (config: {
            client_id: string;
            scope: string;
            prompt?: string;
            callback: (response: any) => void;
            error_callback?: (error: any) => void;
          }) => {
            requestAccessToken: (overrideConfig?: { prompt?: string }) => void;
          };
        };
      };
    };
  }
}

export const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({ onSuccess, onError }) => {
  const tokenClientRef = useRef<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '28814983984-ktqvgph38b9i48go9c0sgo27ut5u2hgq.apps.googleusercontent.com';

  // Direct OAuth 2.0 Popup: Works everywhere (Brave, Chrome, Firefox, Safari)
  // even when third-party Google Identity scripts are blocked by browser shields
  const launchDirectOAuthPopup = useCallback(() => {
    setLoading(true);
    try {
      const redirectUri = `${window.location.origin}/login`;
      const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
      authUrl.searchParams.set('client_id', clientId);
      authUrl.searchParams.set('redirect_uri', redirectUri);
      authUrl.searchParams.set('response_type', 'token id_token');
      authUrl.searchParams.set('scope', 'openid email profile');
      authUrl.searchParams.set('prompt', 'select_account'); // Shows all Google accounts on device
      authUrl.searchParams.set('nonce', Math.random().toString(36).substring(2));

      const width = 500;
      const height = 620;
      const left = Math.max(0, window.screenX + (window.outerWidth - width) / 2);
      const top = Math.max(0, window.screenY + (window.outerHeight - height) / 2);

      const popup = window.open(
        authUrl.toString(),
        'GoogleSignInPopup',
        `width=${width},height=${height},left=${left},top=${top},status=no,toolbar=no,menubar=no`
      );

      if (!popup) {
        // If browser blocks popups, fallback to top-level redirect
        window.location.href = authUrl.toString();
        return;
      }

      // Check if popup was closed by user
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          setLoading(false);
        }
      }, 1000);
    } catch (err: any) {
      setLoading(false);
      onError(err?.message || 'Failed to initiate Google authentication.');
    }
  }, [clientId, onError]);

  // Initialize Google Identity Services (GIS) if available in the browser
  useEffect(() => {
    if (!clientId) return;

    const setupGis = () => {
      if (window.google?.accounts?.oauth2) {
        try {
          tokenClientRef.current = window.google.accounts.oauth2.initTokenClient({
            client_id: clientId,
            scope: 'openid email profile',
            prompt: 'select_account', // Fetch and display all accounts on device
            callback: (tokenResponse: any) => {
              setLoading(false);
              if (tokenResponse?.access_token) {
                onSuccess(tokenResponse.access_token);
              } else if (tokenResponse?.error) {
                onError(`Google authorization failed: ${tokenResponse.error}`);
              }
            },
            error_callback: () => {
              setLoading(false);
            }
          });
          return true;
        } catch {
          return false;
        }
      }
      return false;
    };

    if (setupGis()) return;

    const interval = setInterval(() => {
      if (setupGis()) {
        clearInterval(interval);
      }
    }, 200);

    return () => clearInterval(interval);
  }, [clientId, onSuccess, onError]);

  // Listen for OAuth token posted from popup or URL hash redirect
  useEffect(() => {
    // 1. PostMessage from popup
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      if (event.data?.type === 'GOOGLE_AUTH_SUCCESS' && event.data.token) {
        setLoading(false);
        onSuccess(event.data.token);
      }
    };
    window.addEventListener('message', handleMessage);

    // 2. Direct URL Hash redirect callback (if full-page redirect was used)
    if (window.location.hash && (window.location.hash.includes('access_token') || window.location.hash.includes('id_token'))) {
      const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ''));
      const token = hashParams.get('id_token') || hashParams.get('access_token');
      if (token) {
        // Clean up hash from browser URL without reloading
        window.history.replaceState(null, '', window.location.pathname);
        onSuccess(token);
      }
    }

    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [onSuccess]);

  const handleClick = () => {
    setLoading(true);
    // If GIS tokenClient is ready, use it with select_account prompt
    if (tokenClientRef.current) {
      try {
        tokenClientRef.current.requestAccessToken({ prompt: 'select_account' });
        return;
      } catch {
        // Fall back to direct OAuth popup
      }
    }
    // Universal fallback: Direct Google OAuth popup (Works in Brave Shields, Firefox, Safari)
    launchDirectOAuthPopup();
  };

  return (
    <div className="w-full">
      <button
        type="button"
        onClick={handleClick}
        disabled={loading}
        className="w-full py-2.5 px-4 rounded-xl bg-slate-900 border border-slate-700 hover:border-slate-500 hover:bg-slate-800 text-slate-200 text-xs font-medium flex items-center justify-center gap-3 transition-all shadow-sm hover:shadow active:scale-[0.99] disabled:opacity-70 disabled:cursor-not-allowed group cursor-pointer"
      >
        {/* Official Google 4-Color SVG Icon */}
        <svg className="w-4 h-4 shrink-0 transition-transform group-hover:scale-110" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
          />
        </svg>

        <span>Continue with Google</span>

        {loading && (
          <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin ml-auto" />
        )}
      </button>
    </div>
  );
};
