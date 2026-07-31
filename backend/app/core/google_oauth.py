"""Google OAuth ID token verification utilities."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from google.auth.transport import requests as google_requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleOAuthError(Exception):
    """Google OAuth verification failed."""


def verify_google_id_token(token: str) -> dict[str, Any]:
    """
    Verify a Google ID token using Google's public keys.
    
    Args:
        token: The Google ID token to verify
        
    Returns:
        The decoded token payload containing user information
        
    Raises:
        GoogleOAuthError: If token verification fails
    """
    try:
        # Verify the token using Google's public keys
        # The audience should match your Google OAuth client ID
        google_client_id = settings.google_oauth_client_id
        
        logger.debug(f"GOOGLE_OAUTH_CLIENT_ID from settings: {google_client_id}")
        
        if not google_client_id:
            logger.error("GOOGLE_OAUTH_CLIENT_ID not configured")
            raise GoogleOAuthError("GOOGLE_OAUTH_CLIENT_ID not configured")
        
        # Create a request object for verification
        request = google_requests.Request()
        
        # Verify the token
        id_info = id_token.verify_oauth2_token(
            token,
            request,
            google_client_id,
        )
        
        # Log token details for debugging
        logger.debug(f"Token audience (aud): {id_info.get('aud')}")
        logger.debug(f"Expected audience: {google_client_id}")
        logger.debug(f"Token issuer (iss): {id_info.get('iss')}")
        
        # Check if the issuer is Google
        if id_info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.error(f"Wrong issuer: {id_info.get('iss')}")
            raise GoogleOAuthError("Wrong issuer")
        
        # Check if the audience matches our client ID
        if id_info.get("aud") != google_client_id:
            logger.error(f"Audience mismatch. Token aud: {id_info.get('aud')}, Expected: {google_client_id}")
            raise GoogleOAuthError("Wrong audience")
        
        # Check if the token is not expired
        if id_info.get("exp") < 0:
            logger.error("Token expired")
            raise GoogleOAuthError("Token expired")
        
        return id_info
        
    except Exception as exc:
        logger.error(f"Failed to verify Google ID token: {exc}")
        raise GoogleOAuthError(f"Failed to verify Google ID token: {exc}") from exc


def get_google_user_info(token: str) -> dict[str, Any]:
    """
    Get user information from a Google ID token.
    
    Args:
        token: The Google ID token
        
    Returns:
        Dictionary containing user information:
        - google_id: The user's Google ID (sub)
        - email: The user's email
        - full_name: The user's full name
        - google_avatar_url: The user's profile picture URL
    """
    id_info = verify_google_id_token(token)
    
    return {
        "google_id": id_info.get("sub"),
        "email": id_info.get("email"),
        "full_name": id_info.get("name"),
        "google_avatar_url": id_info.get("picture"),
        "email_verified": id_info.get("email_verified", False),
    }
