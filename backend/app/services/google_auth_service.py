from dataclasses import dataclass
from typing import Optional
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings
from app.core.logger import logger

class GoogleAuthError(Exception):
    """Raised when Google ID token verification fails."""
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
        Cryptographically verifies a Google OpenID Connect ID token using Google public keys.
        Validates signature, audience (client ID), issuer, and expiration.
        """
        target_client_id = client_id or settings.GOOGLE_CLIENT_ID

        if not target_client_id:
            raise GoogleAuthError(
                "Google Sign-In is not configured on this server. Set GOOGLE_CLIENT_ID in server environment."
            )

        try:
            request = google_requests.Request()
            # verify_oauth2_token fetches Google's public certificates, checks signature & audience & expiration
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
            logger.warning(f"Google token verification failed: {str(e)}")
            raise GoogleAuthError(f"Invalid or expired Google credential: {str(e)}")
        except Exception as e:
            if isinstance(e, GoogleAuthError):
                raise e
            logger.error(f"Unexpected error during Google verification: {str(e)}")
            raise GoogleAuthError("Unable to verify Google credential at this time.")

google_auth_service = GoogleAuthService()
