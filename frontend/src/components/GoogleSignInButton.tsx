import React, { useEffect, useRef, useState } from 'react';
import { AlertCircle, Info, Loader2 } from 'lucide-react';

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
  const containerRef = useRef<HTMLDivElement>(null);
  const tokenClientRef = useRef<any>(null);
  const [isGisReady, setIsGisReady] = useState<boolean>(false);
  const [gisError, setGisError] = useState<string | null>(null);
  const [showOriginHelp, setShowOriginHelp] = useState<boolean>(false);
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  const isConfigured = Boolean(
    clientId && clientId !== 'your-google-client-id-here.apps.googleusercontent.com'
  );

  useEffect(() => {
    if (!isConfigured) return;

    let attempts = 0;
    const maxAttempts = 50; // 50 * 150ms = 7.5 seconds

    const initGis = () => {
      if (window.google?.accounts && containerRef.current) {
        try {
          // 1. Initialize Google Identity Services ID client
          window.google.accounts.id.initialize({
            client_id: clientId,
            callback: (response: any) => {
              if (response?.credential) {
                onSuccess(response.credential);
              } else {
                onError('No identity credential returned by Google.');
              }
            },
            auto_select: false,
            cancel_on_tap_outside: true,
          });

          // 2. Clear previous child nodes and render official GIS button
          containerRef.current.innerHTML = '';
          const containerWidth = containerRef.current.offsetWidth || 380;
          const buttonWidth = Math.max(280, Math.min(containerWidth, 400));

          window.google.accounts.id.renderButton(containerRef.current, {
            theme: 'outline',
            size: 'large',
            type: 'standard',
            text: 'continue_with',
            shape: 'rectangular',
            logo_alignment: 'left',
            width: buttonWidth,
          });

          // 3. Initialize OAuth2 Token Client with prompt: 'select_account'
          // This forces Google to fetch and display all accounts on the device
          if (window.google.accounts.oauth2) {
            tokenClientRef.current = window.google.accounts.oauth2.initTokenClient({
              client_id: clientId,
              scope: 'openid email profile',
              prompt: 'select_account',
              callback: (tokenResponse: any) => {
                if (tokenResponse?.access_token) {
                  onSuccess(tokenResponse.access_token);
                } else if (tokenResponse?.error) {
                  onError(`Google authorization failed: ${tokenResponse.error}`);
                }
              },
              error_callback: (err: any) => {
                console.error('Google OAuth error:', err);
                setShowOriginHelp(true);
              }
            });
          }

          setIsGisReady(true);
          return true;
        } catch (err: any) {
          console.error('Failed to initialize Google Identity Services:', err);
          setGisError('Could not initialize Google authentication.');
        }
      }
      return false;
    };

    if (initGis()) return;

    const interval = setInterval(() => {
      attempts++;
      if (initGis() || attempts >= maxAttempts) {
        clearInterval(interval);
        if (attempts >= maxAttempts && !window.google?.accounts) {
          setGisError('Google Identity library took too long to load or was blocked.');
        }
      }
    }, 150);

    return () => clearInterval(interval);
  }, [clientId, isConfigured, onSuccess, onError]);

  const handleManualClick = () => {
    if (!isConfigured) {
      setShowOriginHelp(true);
      return;
    }

    // Force Google Account Chooser showing all accounts on the user's device
    if (tokenClientRef.current) {
      tokenClientRef.current.requestAccessToken({ prompt: 'select_account' });
    } else if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt((notification: any) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          setShowOriginHelp(true);
        }
      });
    } else {
      setShowOriginHelp(true);
    }
  };

  return (
    <div className="w-full space-y-2">
      {/* Official Google Sign-In button container */}
      <div
        ref={containerRef}
        id="google-official-btn-container"
        className={`w-full flex justify-center min-h-[44px] transition-opacity duration-200 ${
          isGisReady ? 'opacity-100' : 'opacity-0 h-0 overflow-hidden'
        }`}
      />

      {/* Fallback button shown while GIS is initializing or if custom click is triggered */}
      {!isGisReady && (
        <button
          type="button"
          onClick={handleManualClick}
          className="w-full py-2.5 px-4 rounded-xl bg-slate-900 border border-slate-700 hover:border-slate-600 hover:bg-slate-800 text-slate-200 text-xs font-medium flex items-center justify-center gap-3 transition-colors shadow-sm"
        >
          {/* Official Google SVG */}
          <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
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
          {isConfigured && !gisError && (
            <Loader2 className="w-3.5 h-3.5 text-slate-400 animate-spin ml-auto" />
          )}
          {!isConfigured && (
            <span className="ml-auto text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
              SETUP REQD
            </span>
          )}
        </button>
      )}

      {/* Helpful guidance if Google OAuth origin needs to be configured in Cloud Console */}
      {showOriginHelp && (
        <div className="p-3 rounded-xl bg-slate-900/90 border border-cyan-500/30 text-[11px] text-slate-300 space-y-2 animate-fadeIn shadow-lg">
          <div className="flex items-center gap-1.5 font-semibold text-cyan-400">
            <Info className="w-4 h-4 shrink-0" />
            <span>Google Cloud Console Origin Setup</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Ensure your Google OAuth 2.0 Client ID has the current URL added under <strong className="text-slate-200">Authorized JavaScript origins</strong>:
          </p>
          <div className="bg-slate-950 p-2 rounded-lg font-mono text-[11px] text-cyan-300 border border-slate-800 break-all select-all">
            {window.location.origin}
          </div>
          <p className="text-[10px] text-slate-500">
            Google Cloud Console &rarr; APIs &amp; Services &rarr; Credentials &rarr; Edit OAuth 2.0 Client ID &rarr; Add Authorized JavaScript Origin.
          </p>
          <div className="flex justify-end pt-1">
            <button
              type="button"
              onClick={() => setShowOriginHelp(false)}
              className="text-[10px] text-cyan-400 hover:text-cyan-300 uppercase tracking-wider font-mono"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {gisError && (
        <div className="flex items-center gap-1.5 text-[11px] text-amber-400 px-1">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{gisError}</span>
        </div>
      )}
    </div>
  );
};

