from dataclasses import dataclass
from typing import Optional
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings
from app.core.logger import logger

class GoogleAuthError(Exception):
    """Raised when Google credential verification fails."""
    pass

@dataclass
class GoogleUserInfo:
    sub: str
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False

class GoogleAuthService:
    def verify_credential(self, credential: str, client_id: Optional[str] = None) -> GoogleUserInfo:
        """
        Verifies a Google credential. Supports:
        1. OpenID Connect ID tokens (JWT, starts with 'eyJ...') verified via Google public keys
        2. OAuth2 Access tokens (starts with 'ya29.') verified via Google's tokeninfo/userinfo endpoints
        """
        target_client_id = client_id or settings.GOOGLE_CLIENT_ID

        if not target_client_id:
            raise GoogleAuthError(
                "Google Sign-In is not configured on this server. Set GOOGLE_CLIENT_ID in server environment."
            )

        credential = credential.strip()

        # Handle OAuth2 Access Token flow (from prompt: 'select_account' token client)
        if credential.startswith("ya29."):
            return self._verify_access_token(credential, target_client_id)

        # Handle standard OpenID Connect ID Token flow
        try:
            request = google_requests.Request()
            id_info = id_token.verify_oauth2_token(
                credential,
                request,
                target_client_id
            )

            # Validate issuer
            issuer = id_info.get("iss")
            if issuer not in ("accounts.google.com", "https://accounts.google.com"):
                raise GoogleAuthError(f"Invalid Google token issuer: {issuer}")

            # Extract verified identity
            email = id_info.get("email")
            if not email:
                raise GoogleAuthError("Google token does not contain an email address.")

            email_verified = id_info.get("email_verified", False)
            if not email_verified:
                raise GoogleAuthError("Google account email is not verified.")

            sub = id_info.get("sub")
            if not sub:
                raise GoogleAuthError("Google token does not contain a subject ID (sub).")

            name = id_info.get("name") or email.split("@")[0]
            picture = id_info.get("picture")

            return GoogleUserInfo(
                sub=sub,
                email=email.lower().strip(),
                name=name,
                picture=picture,
                email_verified=email_verified
            )
        except ValueError as e:
            logger.warning(f"Google ID token verification failed: {str(e)}")
            raise GoogleAuthError(f"Invalid or expired Google credential: {str(e)}")
        except Exception as e:
            if isinstance(e, GoogleAuthError):
                raise e
            logger.error(f"Unexpected error during Google ID token verification: {str(e)}")
            raise GoogleAuthError("Unable to verify Google credential at this time.")

    def _verify_access_token(self, access_token: str, target_client_id: str) -> GoogleUserInfo:
        """
        Validates a Google OAuth2 access token against Google tokeninfo and userinfo endpoints.
        Ensures the token was issued to target_client_id and email is verified.
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                # 1. Check token validity and audience/client_id match
                tokeninfo_res = client.get(
                    f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}"
                )
                if tokeninfo_res.status_code != 200:
                    raise GoogleAuthError("Google rejected the access token.")

                tokeninfo = tokeninfo_res.json()
                aud = tokeninfo.get("aud")
                azp = tokeninfo.get("azp")
                
                # Check audience match (aud or azp matches our client ID)
                if target_client_id not in (aud, azp):
                    raise GoogleAuthError("Google token audience mismatch.")

                # 2. Fetch authenticated user profile
                userinfo_res = client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if userinfo_res.status_code != 200:
                    raise GoogleAuthError("Could not retrieve Google profile for access token.")

                userinfo = userinfo_res.json()
                email = userinfo.get("email") or tokeninfo.get("email")
                if not email:
                    raise GoogleAuthError("Google account does not provide an email address.")

                email_verified = userinfo.get("email_verified", tokeninfo.get("email_verified") == "true")
                if not email_verified:
                    raise GoogleAuthError("Google account email is not verified.")

                sub = userinfo.get("sub") or tokeninfo.get("sub")
                if not sub:
                    raise GoogleAuthError("Google account does not provide a user ID.")

                name = userinfo.get("name") or email.split("@")[0]
                picture = userinfo.get("picture")

                return GoogleUserInfo(
                    sub=sub,
                    email=email.lower().strip(),
                    name=name,
                    picture=picture,
                    email_verified=True
                )
        except Exception as e:
            if isinstance(e, GoogleAuthError):
                raise e
            logger.error(f"Error verifying Google access token: {str(e)}")
            raise GoogleAuthError("Failed to authenticate with Google access token.")

google_auth_service = GoogleAuthService()

