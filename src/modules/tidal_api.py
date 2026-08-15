"""
TIDAL API Client Module for Sonic Flux
=======================================

Provides OAuth 2.1 authentication and RESTful access to TIDAL's music catalogue,
metadata, and user functionality via JSON:API v2 specification.

Authentication Flows Supported:
- Client Credentials (catalog-only access) - DEFAULT FOR SONIC FLUX
- Authorization Code + PKCE (user context with refresh tokens)

OAuth Endpoints:
- Token Issuance: https://auth.tidal.com/v1/oauth2/token
- Authorization: https://login.tidal.com/authorize
- Production API: https://openapi.tidal.com/v2

JSON:API Compliance:
All responses follow JSON:API v2 specification with resource objects,
relationships, compound documents via include, and standard error objects.

See also: TIDAL Developer Portal (https://developer.tidal.com)
"""

import os
import json
import base64
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import requests


@dataclass
class TidalToken:
    """Represents a TIDAL OAuth access token."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 0
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: float = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if access token has expired."""
        if self.expires_in == 0:
            return True
        expiry_time = self.created_at + self.expires_in
        return time.time() > expiry_time
    
    @property
    def expiry_time(self) -> datetime:
        """Get token expiry datetime."""
        if self.expires_in > 0:
            return datetime.fromtimestamp(self.created_at + self.expires_in)
        return datetime.utcnow() + __import__('datetime').timedelta(seconds=self.expires_in)


class TidalApiError(Exception):
    """Base exception for TIDAL API errors."""
    pass


class AuthenticationError(TidalApiError):
    """Raised when authentication fails."""
    pass


class ApiError(TidalApiError):
    """Raised when API request fails or returns error response."""
    def __init__(self, message: str, status_code: int = None, errors: list = None):
        super().__init__(message)
        self.status_code = status_code
        self.errors = errors or []


class TidalApi:
    """
    TIDAL API Client with OAuth 2.1 authentication support.
    
    Supports both client credentials flow (catalog access) and
    authorization code + PKCE flow (user context with refresh tokens).
    
    Usage Example (Client Credentials - Catalog Access):
        from tidal_api import TidalApi
        
        api = TidalApi()
        token = api.authenticate_client_credentials()  # Get catalog access
        tracks = api.get_tracks(paths=["tidal://track/12345"])
        
    Usage Example (Authorization Code + PKCE - User Context):
        # Step 1: Redirect user to authorization URL
        auth_url = f"{api.AUTHORIZATION_ENDPOINT}?response_type=code&..."
        code = get_from_redirect()
        
        # Step 2: Exchange code for tokens
        token = api.authenticate_authorization_code(code, redirect_uri)
        
        # Step 3: Use token for user library access
        liked_tracks = api.get_user_collection_tracks(scope="liked")
    """
    
    # Endpoint URLs
    TOKEN_ENDPOINT = "https://auth.tidal.com/v1/oauth2/token"
    AUTHORIZATION_ENDPOINT = "https://login.tidal.com/authorize"
    PRODUCTION_API_BASE = "https://openapi.tidal.com/v2"
    
    # Default token storage path (can be overridden)
    DEFAULT_TOKEN_STORE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "tidal_token_store.json"
    )
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_store_path: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize TIDAL API client.
        
        Args:
            client_id: TIDAL app Client ID (load from .env if not provided)
            client_secret: TIDAL app Client Secret (load from .env if not provided)
            token_store_path: Path to JSON file for storing OAuth tokens
            base_url: Optional override for API base URL (for testing/dev)
        """
        self.client_id = client_id or self._load_client_id()
        self.client_secret = client_secret or self._load_client_secret()
        self.token_store_path = token_store_path or self.DEFAULT_TOKEN_STORE_PATH
        self.base_url = base_url or self.PRODUCTION_API_BASE
        
        # HTTP session for persistent connections
        self.session = requests.Session()
        
        # Current token (cached)
        self._current_token: Optional[TidalToken] = None
    
    def _load_client_id(self) -> str:
        """Load Client ID from .env file."""
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".env"
        )
        
        if not os.path.exists(env_file):
            raise AuthenticationError("TIDAL_CLIENT_ID not found in .env file")
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('TIDAL_CLIENT_ID=') and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        return value.strip('"\'')
        except Exception as e:
            raise AuthenticationError(f"Failed to load TIDAL_CLIENT_ID: {e}")
        
        raise AuthenticationError("TIDAL_CLIENT_ID not found in .env file")
    
    def _load_client_secret(self) -> str:
        """Load Client Secret from .env file."""
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".env"
        )
        
        if not os.path.exists(env_file):
            raise AuthenticationError("TIDAL_CLIENT_SECRET not found in .env file")
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('TIDAL_CLIENT_SECRET=') and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        return value.strip('"\'')
        except Exception as e:
            raise AuthenticationError(f"Failed to load TIDAL_CLIENT_SECRET: {e}")
        
        raise AuthenticationError("TIDAL_CLIENT_SECRET not found in .env file")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with Authorization."""
        if self._current_token and not self._current_token.is_expired:
            return {
                "Authorization": f"{self._current_token.token_type} {self._current_token.access_token}",
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.tidal.v1+json"
            }
        else:
            raise AuthenticationError("No valid access token available. Call authenticate() first.")
    
    def load_token(self) -> Optional[TidalToken]:
        """Load stored token from file."""
        if not os.path.exists(self.token_store_path):
            return None
        
        try:
            with open(self.token_store_path, 'r') as f:
                data = json.load(f)
            
            if "access_token" in data:
                token_data = {
                    "access_token": data["access_token"],
                    "token_type": data.get("token_type", "Bearer"),
                    "expires_in": data.get("expires_in", 86400),
                    "refresh_token": data.get("refresh_token"),
                    "scope": data.get("scope"),
                    "created_at": data.get("created_at", time.time())
                }
                return TidalToken(**token_data)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def save_token(self, token: TidalToken):
        """Save token to file."""
        os.makedirs(os.path.dirname(self.token_store_path), exist_ok=True)
        
        token_data = {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
            "refresh_token": token.refresh_token,
            "scope": token.scope,
            "created_at": token.created_at
        }
        
        with open(self.token_store_path, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    def authenticate_client_credentials(self) -> TidalToken:
        """
        Authenticate using client credentials flow (catalog-only access).
        
        This is the DEFAULT and RECOMMENDED flow for Sonic Flux.
        Provides access to TIDAL Catalog metadata without requiring user login.
        
        Returns:
            TidalToken with access token for catalog access
        
        Example:
            >>> api = TidalApi()
            >>> token = api.authenticate_client_credentials()
            >>> tracks = api.get_tracks(paths=["tidal://track/12345"])
        
        Raises:
            AuthenticationError: If authentication fails
        """
        # Generate base64-encoded credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Request token (client credentials flow)
        response = self.session.post(
            self.TOKEN_ENDPOINT,
            headers={"Authorization": f"Basic {b64_credentials}"},
            data={
                "grant_type": "client_credentials",
                "scope": "read-metadata"  # Default scope for catalog access
            },
            timeout=30
        )
        
        response.raise_for_status()
        
        result = response.json()
        
        # Create token object
        token = TidalToken(
            access_token=result["access_token"],
            token_type=result.get("token_type", "Bearer"),
            expires_in=result.get("expires_in", 86400),
            scope=result.get("scope"),
            created_at=time.time()
        )
        
        # Save to file
        self.save_token(token)
        
        # Cache token
        self._current_token = token
        
        print(f"✅ Client credentials authentication successful")
        print(f"   Token expires in {token.expires_in / 3600:.1f} hours")
        
        return token
    
    def authenticate_authorization_code(
        self,
        redirect_uri: str,
        code_verifier: str,
        scopes: Optional[List[str]] = None
    ) -> TidalToken:
        """
        Authenticate using authorization code + PKCE flow (user context).
        
        Required for accessing user libraries, playlists, and personalized data.
        More complex setup but provides full user context.
        
        Args:
            redirect_uri: Registered redirect URI from app settings
            code_verifier: PKCE code verifier (generated during auth)
            scopes: List of requested scopes (e.g., ["read-metadata", "read-library"])
        
        Returns:
            TidalToken with access token and refresh token
        
        Raises:
            AuthenticationError: If authentication fails
        
        Example:
            >>> # After user authorizes:
            >>> code = get_code_from_redirect()
            >>> verifier = generate_code_verifier()
            >>> code_challenge = generate_code_challenge(verifier)
            >>> auth_url = f"{AUTHORIZATION_ENDPOINT}?code_challenge={code_challenge}..."
            >>> 
            >>> # User visits auth_url, consents, and redirects back with code
            >>> token = api.authenticate_authorization_code(redirect_uri, verifier, scopes)
        """
        if not scopes:
            scopes = ["read-metadata"]
        
        scopes_str = " ".join(scopes)
        
        # Request token exchange
        response = self.session.post(
            self.TOKEN_ENDPOINT,
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "code_verifier": code_verifier,
                "redirect_uri": redirect_uri,
                "scope": scopes_str
            },
            timeout=30
        )
        
        response.raise_for_status()
        
        result = response.json()
        
        # Create token object
        token = TidalToken(
            access_token=result["access_token"],
            token_type=result.get("token_type", "Bearer"),
            expires_in=result.get("expires_in", 86400),
            refresh_token=result.get("refresh_token"),
            scope=result.get("scope"),
            created_at=time.time()
        )
        
        # Save to file
        self.save_token(token)
        
        # Cache token
        self._current_token = token
        
        print(f"✅ Authorization code authentication successful")
        if token.refresh_token:
            print(f"   Refresh token received (can renew access)")
        print(f"   Token expires in {token.expires_in / 3600:.1f} hours")
        
        return token
    
    def refresh_token(self) -> TidalToken:
        """
        Refresh access token using refresh token.
        
        Required for authorization code flow to renew expired access tokens.
        
        Returns:
            New TidalToken with fresh access token
        
        Raises:
            AuthenticationError: If refresh fails or no refresh token available
        
        Example:
            >>> token = api.refresh_token()  # Get new access token
        """
        if not self._current_token or not self._current_token.refresh_token:
            raise AuthenticationError("No refresh token available for renewal")
        
        # Request new token
        response = self.session.post(
            self.TOKEN_ENDPOINT,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._current_token.refresh_token
            },
            timeout=30
        )
        
        response.raise_for_status()
        
        result = response.json()
        
        # Create new token object
        new_token = TidalToken(
            access_token=result["access_token"],
            token_type=result.get("token_type", "Bearer"),
            expires_in=result.get("expires_in", 86400),
            scope=result.get("scope"),
            created_at=time.time()
        )
        
        # Save to file (overwrite old token)
        self.save_token(new_token)
        
        # Update cache
        self._current_token = new_token
        
        print(f"✅ Token refreshed successfully")
        
        return new_token
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request to API endpoint.
        
        Args:
            endpoint: Relative path from base URL (e.g., "tracks", "albums/123")
            params: Query parameters (optional)
        
        Returns:
            Parsed JSON response
        
        Raises:
            ApiError: If request fails or returns error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        response = self.session.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 401:
            # Try to refresh token
            print("⚠️  Token expired, attempting refresh...")
            try:
                self.refresh_token()
                return self.get(endpoint, params)
            except Exception as e:
                raise AuthenticationError(f"Token refresh failed: {e}")
        
        response.raise_for_status()
        
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make POST request to API endpoint.
        
        Args:
            endpoint: Relative path from base URL
            data: Request body (optional)
        
        Returns:
            Parsed JSON response
        
        Raises:
            ApiError: If request fails or returns error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        response = self.session.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 401:
            print("⚠️  Token expired, attempting refresh...")
            try:
                self.refresh_token()
                return self.post(endpoint, data)
            except Exception as e:
                raise AuthenticationError(f"Token refresh failed: {e}")
        
        response.raise_for_status()
        
        return response.json()
    
    def get_tracks(
        self,
        ids: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
        limit: int = 25,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get tracks by ID or path.
        
        Args:
            ids: List of track IDs (optional)
            paths: List of track paths (optional)
            limit: Number of results per page (max 25 for tracks)
            offset: Pagination offset
        
        Returns:
            JSON:API response with tracks data
        
        Example:
            >>> tracks = api.get_tracks(paths=["tidal://track/12345", "tidal://track/67890"])
            >>> for track in tracks['data']:
            >>>     print(track['id'], track['attributes']['name'])
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if ids:
            params["ids"] = ",".join(ids)
        elif paths:
            params["path"] = ",".join(paths)
        
        return self.get("tracks", params=params)
    
    def get_track(self, id_or_path: str) -> Dict[str, Any]:
        """Get single track by ID or path."""
        return self.get(f"tracks/{id_or_path}")
    
    def get_albums(
        self,
        ids: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
        limit: int = 25,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get albums by ID or path."""
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if ids:
            params["ids"] = ",".join(ids)
        elif paths:
            params["path"] = ",".join(paths)
        
        return self.get("albums", params=params)
    
    def get_artist(self, id_or_path: str) -> Dict[str, Any]:
        """Get artist by ID or path."""
        return self.get(f"artists/{id_or_path}")
    
    def search(
        self,
        query: str,
        types: Optional[List[str]] = None,
        limit: int = 25,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for tracks, albums, or artists.
        
        Args:
            query: Search term (artist name, track title, etc.)
            types: Filter by content type ("tracks", "albums", "artists")
            limit: Results per page
            offset: Pagination offset
        
        Returns:
            Search results with filtered and related fields
        
        Example:
            >>> results = api.search("The Weeknd", types=["tracks"])
            >>> for track in results['data']:
            >>>     print(track['attributes']['name'], track['relationships']['album']['data']['id'])
        """
        params = {
            "q": query,
            "limit": limit,
            "offset": offset
        }
        
        if types:
            params["types"] = ",".join(types)
        
        return self.get("tracks/search", params=params)
    
    def get_user_collection_tracks(self, scope: str = "liked") -> Dict[str, Any]:
        """
        Get user's liked tracks or playlists.
        
        Args:
            scope: Collection scope ("liked" for liked tracks, "playlists" for playlists)
        
        Returns:
            User collection with items and relationships
        
        Note: Requires user-scoped token from auth code flow
        """
    
    def get_playlist(self, id_or_path: str) -> Dict[str, Any]:
        """Get playlist by ID or path."""
        return self.get(f"playlists/{id_or_path}")
    
    def create_playlist(self, name: str, source_type: str = "catalog") -> Dict[str, Any]:
        """
        Create a new playlist.
        
        Args:
            name: Playlist name
            source_type: "catalog" for user-created playlists
        
        Returns:
            Created playlist with metadata
        """
        data = {
            "data": {
                "type": "playlist",
                "attributes": {
                    "name": name,
                    "sourceType": source_type
                }
            }
        }
        
        return self.post("playlists", data=data)
    
    def add_tracks_to_playlist(
        self,
        playlist_id: str,
        track_ids: List[str],
        scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add tracks to playlist.
        
        Args:
            playlist_id: Playlist ID or path
            track_ids: List of track IDs to add
            scope: "liked" for liked tracks, null for catalog
        
        Returns:
            Updated playlist with added items
        """
        # Note: Batch track addition uses different API pattern
        return self.post(f"playlists/{playlist_id}", data={
            "data": {
                "type": "playlist-item",
                "relationships": {
                    "playlist": {
                        "data": {"id": playlist_id, "type": "playlist"}
                    },
                    "track": {
                        "data": {"id": track_ids[0], "type": "track"}
                    }
                }
            }
        })


# Singleton instance (optional, for convenience)
_tidal_instance: Optional[TidalApi] = None


def get_tidal_api() -> TidalApi:
    """Get or create singleton TidalApi instance."""
    global _tidal_instance
    
    if _tidal_instance is None:
        _tidal_instance = TidalApi()
    
    return _tidal_instance
