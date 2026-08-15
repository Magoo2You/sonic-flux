"""
TIDAL OAuth 2.1 Authorization Code Flow Client with PKCE
==========================================================
This module implements the complete authorization code flow for user-scoped
access to TIDAL API endpoints (tracks, search, playlists, etc.)

FLOW OVERVIEW:
1. User clicks "Login" button in Sonic Flux
2. Redirected to https://listen.tidal.com/oauth/authorize
3. User authorizes and enters credentials
4. Redirect back to Sonic Flux with auth code
5. Exchange auth code for access + refresh tokens
6. Use tokens for API calls

SECURITY: Uses PKCE (Proof Key for Code Exchange) per OAuth 2.1 spec
"""

import sys
import os
import json
import base64
import requests


class TidalOAuthFlowError(Exception):
    """Base exception for TidalOAuthFlow errors."""
    pass


class AuthorizationPendingError(TidalOAuthFlowError):
    """User has not yet authorized the application."""
    pass


class CodeExchangeFailedError(TidalOAuthFlowError):
    """Failed to exchange authorization code for tokens."""
    pass


class TokenRefreshFailedError(TidalOAuthFlowError):
    """Failed to refresh access token."""
    pass


class TidalApi:
    """
    TIDAL OAuth 2.1 Authorization Code Flow Client
    
    Implements complete user-scoped access to TIDAL API endpoints
    including tracks, search, albums, artists, and playlists.
    
    Authentication requires user interaction via browser redirect.
    """
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the TidalOAuthFlowClient.
        
        Args:
            client_id: Your TIDAL API Client ID
            client_secret: Your TIDAL API Client Secret (not used in PKCE flow)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        
        # TIDAL OAuth endpoints
        self.AUTHORIZATION_URL = "https://listen.tidal.com/oauth/authorize"
        self.TOKEN_ENDPOINT = "https://openapi.tidal.com/v1/auth/token"
        self.REFRESH_ENDPOINT = "https://openapi.tidal.com/v1/auth/refresh"
        
        # Default token store path
        self.DEFAULT_TOKEN_STORE_PATH = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "data", "tidal_token_store.json"
        ).replace("\\\\", "\\")
    
    def generate_code_verifier(self, length: int = 43) -> str:
        """
        Generate a code verifier (random string for PKCE).
        
        Args:
            length: Length of the random string (default 43 chars)
            
        Returns:
            Base64URL encoded random string
        """
        # Generate random bytes
        import secrets
        return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8')[:length]
    
    def generate_code_challenge(self, verifier: str) -> str:
        """
        Generate a code challenge from the verifier (S256 SHA256 hash).
        
        Args:
            verifier: The code verifier to hash
            
        Returns:
            Base64URL encoded SHA256 hash of the verifier
        """
        import hashlib
        import base64
        
        # Create SHA256 hash of the verifier
        hash_bytes = hashlib.sha256(verifier.encode('utf-8')).digest()
        # Convert to Base64URL
        return base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')
    
    def get_authorization_url(self, redirect_uri: str, scope: str = "data:read") -> str:
        """
        Generate the authorization URL for user login.
        
        Args:
            redirect_uri: The URI where TIDAL will redirect after authorization
                          Must match what's registered in TIDAL developer portal
            scope: OAuth scopes to request (default: "data:read")
            
        Returns:
            Authorization URL that redirects user to TIDAL login page
        """
        import urllib.parse
        
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        # Build authorization request parameters
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'  # PKCE S256 required by TIDAL
        }
        
        url = f"{self.AUTHORIZATION_URL}?" + urllib.parse.urlencode(params)
        return {
            'url': url,
            'code_verifier': code_verifier,  # Store for later exchange
            'redirect_uri': redirect_uri
        }
    
    def exchange_code_for_tokens(self, code: str, code_verifier: str, 
                                  redirect_uri: str) -> dict:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from TIDAL redirect
            code_verifier: Original code verifier used to generate challenge
            redirect_uri: Same URI as used in authorization request
            
        Returns:
            Dictionary containing access_token, refresh_token, token_type, expires_in
        """
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'code_verifier': code_verifier
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                self.TOKEN_ENDPOINT,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                tokens = response.json()
                return {
                    'access_token': tokens.get('access_token'),
                    'refresh_token': tokens.get('refresh_token'),
                    'token_type': tokens.get('token_type', 'Bearer'),
                    'expires_in': int(tokens.get('expires_in')),
                    'scope': tokens.get('scope', '')
                }
            else:
                raise CodeExchangeFailedError(f"Token exchange failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            raise CodeExchangeFailedError(f"Exchange error: {e}")
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh the access token using the refresh token.
        
        Args:
            refresh_token: The refresh token from token exchange
            
        Returns:
            Dictionary containing refreshed tokens
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                self.REFRESH_ENDPOINT,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                tokens = response.json()
                return {
                    'access_token': tokens.get('access_token'),
                    'refresh_token': tokens.get('refresh_token', refresh_token),  # Keep old if not provided
                    'token_type': tokens.get('token_type', 'Bearer'),
                    'expires_in': int(tokens.get('expires_in')),
                    'scope': tokens.get('scope', '')
                }
            else:
                raise TokenRefreshFailedError(f"Token refresh failed with {response.status_code}: {response.text}")
                
        except Exception as e:
            raise TokenRefreshFailedError(f"Refresh error: {e}")
    
    def save_token(self, token_data: dict) -> bool:
        """
        Save tokens to JSON file for persistence.
        
        Args:
            token_data: Dictionary with access_token, refresh_token, etc.
            
        Returns:
            True if saved successfully
        """
        os.makedirs(os.path.dirname(self.DEFAULT_TOKEN_STORE_PATH), exist_ok=True)
        
        with open(self.DEFAULT_TOKEN_STORE_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        return True
    
    def load_token(self) -> dict | None:
        """
        Load tokens from JSON file.
        
        Returns:
            Dictionary of tokens if valid token exists, None otherwise
        """
        if not os.path.exists(self.DEFAULT_TOKEN_STORE_PATH):
            return None
        
        try:
            with open(self.DEFAULT_TOKEN_STORE_PATH, 'r') as f:
                token_data = json.load(f)
            
            # Check if token is still valid (not expired)
            created_at = token_data.get('created_at', 0)
            expires_in = token_data.get('expires_in', 14400)  # Default 4 hours
            current_age = (os.path.getmtime(self.DEFAULT_TOKEN_STORE_PATH) - created_at) * 1000
            
            if current_age < expires_in:
                return token_data
            else:
                print(f"   ⚠️  Token expired, refreshing...")
                # Try to refresh if possible
                try:
                    new_token = self.refresh_access_token(token_data['refresh_token'])
                    new_token['created_at'] = os.path.getmtime(self.DEFAULT_TOKEN_STORE_PATH)
                    self.save_token(new_token)
                    return new_token
                except Exception as e:
                    print(f"   ⚠️  Could not refresh token: {e}")
                    return None
                    
        except json.JSONDecodeError:
            print("   ⚠️  Invalid token file, please re-authenticate")
            return None
    
    def has_valid_token(self) -> bool:
        """
        Check if we have a valid cached token.
        
        Returns:
            True if valid token exists and is not expired
        """
        token = self.load_token()
        return token is not None
