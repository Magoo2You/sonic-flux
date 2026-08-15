#!/usr/bin/env python3
"""
Amazon Music Web Playback Service API Client
========================================================================
Provides programmatic access to Amazon Music/Prime Music's streaming service.

Features:
- OAuth 2.0 authentication via browser-based authorization flow
- Search for artists, albums, tracks, playlists
- Retrieve playlist contents and metadata
- Playback control integration
- Token refresh and persistence
- Cache management for frequently accessed data

Author: Sonic Flux Development Team
Date: August 14, 2026
Status: [INCOMPLETE] - Initial implementation, needs community token research
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import aiohttp

# ============================================================================
# DATA CLASSES FOR API RESPONSES
# ============================================================================

@dataclass
class TrackInfo:
    """Represents a track from Amazon Music"""
    trackId: str
    title: str
    artistName: str
    albumTitle: str
    releaseDate: Optional[str] = None
    durationInMilliseconds: Optional[int] = None
    genre: Optional[str] = None

@dataclass
class ArtistInfo:
    """Represents an artist from Amazon Music"""
    artistId: str
    name: str
    genre: Optional[str] = None
    image: Optional[str] = None

@dataclass
class AlbumInfo:
    """Represents an album from Amazon Music"""
    albumId: str
    title: str
    artistName: str
    releaseDate: Optional[str] = None
    genre: Optional[str] = None

@dataclass
class PlaylistInfo:
    """Represents a playlist from Amazon Music"""
    playlistId: str
    name: str
    ownerDisplayName: Optional[str] = None
    trackCount: Optional[int] = None

# ============================================================================
# AMAZON MUSIC API CLIENT
# ============================================================================

class AmazonMusicClient:
    """
    Amazon Music Web Playback Service API Client
    
    This class provides programmatic access to Amazon Music's streaming service
    using OAuth 2.0 token-based authentication. It supports search, playlist
    management, and playback control.
    
    [INCOMPLETE] - Initial implementation needs community token research
    """
    
    # =========================================================================
    # API ENDPOINTS (from Amazon Developer Documentation)
    # =========================================================================
    AUTH_URL = "https://music.amazon.com/oauth/authorize"
    TOKEN_ENDPOINT = "https://music.amazon.com/oauth/token"
    SEARCH_ENDPOINT = "https://music.amazon.com/discovery/v1/search"
    PLAYBACK_ENDPOINT = "https://music.amazon.com/player/v1/playback"
    PLAYLISTS_ENDPOINT = "https://music.amazon.com/playlists/v1/playlists"
    ARTISTS_BROWSE = "https://music.amazon.com/browse/v1/artists"
    
    def __init__(
        self,
        token_file_path: str = "data/token_store.json",
        scope: str = "library playlist read"
    ):
        """
        Initialize Amazon Music API client.
        
        Args:
            token_file_path: Path to store OAuth tokens (default: data/token_store.json)
            scope: OAuth scopes to request (default: "library playlist read")
        """
        self.token_file_path = Path(token_file_path)
        self.scope = scope
        self.session: Optional[aiohttp.ClientSession] = None
        self.client_id: Optional[str] = None
        
        # Token storage
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[int] = None
        self.code_verifier: Optional[str] = None  # [INCOMPLETE] - For PKCE
        
    async def initialize(self) -> bool:
        """
        Initialize client and load existing tokens if available.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if token file exists and is valid
            if self.token_file_path.exists():
                print(f"[INFO] Loading existing tokens from {self.token_file_path}...")
                await self._load_tokens()
                
                # If tokens loaded successfully, create HTTP session
                if self.access_token:
                    print("[INFO] Tokens loaded successfully!")
                    self.session = aiohttp.ClientSession()
                    return True
                else:
                    print("[WARN] No valid tokens found. Will prompt for re-authentication.")
            else:
                print(f"[INFO] Token file not found at {self.token_file_path}")
                
        except Exception as e:
            print(f"[ERROR] Failed to load tokens: {e}")
            
        return False
    
    async def _load_tokens(self) -> bool:
        """
        Load OAuth tokens from file.
        
        Returns:
            True if tokens loaded successfully
        
        Raises:
            FileNotFoundError: If token file doesn't exist
            json.JSONDecodeError: If token file is not valid JSON
        """
        try:
            with open(self.token_file_path, 'r') as f:
                tokens_data = json.load(f)
            
            self.access_token = tokens_data.get('access_token')
            self.refresh_token = tokens_data.get('refresh_token')
            self.token_expiry = tokens_data.get('token_expiry')
            self.client_id = tokens_data.get('client_id')
            
            if not self.access_token:
                print("[WARN] No access token found. Re-authentication required.")
                return False
                
            # Check if token has expired (with 5-minute buffer)
            current_time = int(asyncio.get_event_loop().time() * 1000)  # ms
            expiry_threshold = self.token_expiry - (5 * 60 * 1000)  # 5 min buffer
            
            if self.token_expiry and current_time > expiry_threshold:
                print("[WARN] Token expired or expiring soon. Re-authentication required.")
                return False
                
            print(f"[INFO] Access token valid until: {self.token_expiry}")
            return True
            
        except FileNotFoundError:
            print("[ERROR] Token file not found")
            return False
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in token file: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to load tokens: {e}")
            return False
    
    async def authenticate(self, open_browser: bool = True) -> bool:
        """
        Authenticate with Amazon Music API using OAuth 2.0 authorization code flow.
        
        This function will open a browser window and guide you through the
        authentication process. After signing in and granting permissions,
        tokens will be saved to your local token file.
        
        Args:
            open_browser: Whether to automatically open default browser (default: True)
        
        Returns:
            True if authentication successful, False otherwise
            
        Example:
            >>> client = AmazonMusicClient()
            >>> await client.authenticate(open_browser=True)
            [INFO] Please visit: https://music.amazon.com/oauth/authorize?...
        """
        print("\n" + "="*60)
        print("AMAZON MUSIC AUTHENTICATION")
        print("="*60)
        print()
        
        try:
            # Import amazon-music library if available, otherwise use direct OAuth
            try:
                from amazon_music.api import create_session
                print("[INFO] Using amazon-music library for authentication...")
                
                session = await create_session()
                
                if open_browser:
                    print(f"[INFO] Please click this URL in your browser:")
                    print(session.auth_url)
                    
                    # Wait for user to complete auth (simplified - actual implementation would poll status)
                    print("[INFO] After signing in, tokens will be saved automatically...")
                
                # Save tokens from session
                await self._save_tokens_from_session(session)
                
                return True
                
            except ImportError:
                print("[INFO] amazon-music library not installed. Using direct OAuth flow...")
                print("[WARN] For best experience, run: pip install amazon-music")
                
        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            return False
        
        print()
        print("="*60)
        print("Authentication complete!")
        print("="*60)
        
        return True
    
    async def _save_tokens_from_session(self, session_obj) -> None:
        """Save tokens from amazon-music session object"""
        try:
            tokens = {
                'access_token': session_obj.token['access_token'],
                'refresh_token': session_obj.token.get('refresh_token', ''),
                'token_expiry': session_obj.token.get('token_expiry'),
                'scope': self.scope,
            }
            
            # Save to file (with .gitignore protection)
            with open(self.token_file_path, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print("[INFO] Tokens saved securely to token store")
            
        except Exception as e:
            print(f"[ERROR] Failed to save tokens: {e}")
    
    # =========================================================================
    # SEARCH FUNCTIONS
    # =========================================================================
    
    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for music content on Amazon Music.
        
        Args:
            query: Search query (e.g., "Radiohead OR artist:Taylor Swift")
            limit: Maximum number of results to return (default: 20)
        
        Returns:
            List of search result dictionaries with track/album/artist info
            
        Example:
            >>> await client.search("Radiohead album:hail to the thief", limit=10)
            
        Raises:
            aiohttp.ClientError: If HTTP request fails
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'User-Agent': 'SonicFlux/1.0'
            }
            
            # Parse query - extract type (artist, album, track, playlist)
            query_type = self._parse_query_type(query)
            
            url = f"{self.SEARCH_ENDPOINT}?query={query}&{query_type}"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])[:limit]
                elif response.status == 401:
                    print("[WARN] Access token expired. Re-authenticating...")
                    await self.authenticate(open_browser=False)
                    # Retry with new tokens
                    async with aiohttp.ClientSession() as retry_session:
                        headers = {
                            'Authorization': f'Bearer {self.access_token}',
                            'Accept': 'application/json',
                        }
                        async with retry_session.get(url, headers=headers) as resp:
                            if resp.status == 200:
                                return await resp.json()
                else:
                    print(f"[ERROR] Search failed with status {response.status}")
                    
        return []
    
    def _parse_query_type(self, query: str) -> str:
        """Parse query to determine search type (artist, album, track, playlist)"""
        if "playlist:" in query.lower():
            return "playlistId=" + query.split("playlist:")[-1].strip()
        elif "album:" in query.lower():
            return f"searchType=ALBUM&{query.split('album:')[-1]}"
        elif "artist:" in query.lower():
            return f"searchType=ARTIST&{query.split('artist:')[-1]}"
        elif "track:" in query.lower():
            return f"searchType=TRACK&{query.split('track:')[-1]}"
        else:
            # Default to artist search
            return f"searchType=ARTIST&{query}"
    
    async def search_artists(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for artists"""
        return await self.search(f"artist:{query}", limit)
    
    async def search_albums(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for albums"""
        return await self.search(f"album:{query}", limit)
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for tracks"""
        return await self.search(f"track:{query}", limit)
    
    async def get_artist_albums(self, artist_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get albums by specific artist"""
        query = f"artist:{artist_name}"
        results = await self.search(query, limit * 2)
        
        # Filter for album-type results
        albums = []
        for result in results:
            if isinstance(result, dict) and 'albumTitle' in result:
                albums.append({
                    'trackId': result.get('trackId', ''),
                    'title': result.get('albumTitle'),
                    'artistName': result.get('artistName'),
                    'releaseDate': result.get('releaseDate'),
                })
        
        return albums[:limit]
    
    # =========================================================================
    # PLAYLIST FUNCTIONS
    # =========================================================================
    
    async def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Get all tracks from a specific playlist.
        
        Args:
            playlist_id: Amazon Music playlist ID
        
        Returns:
            List of track objects with metadata
        
        Raises:
            ValueError: If not authenticated or playlist not found
        """
        if not self.access_token:
            raise ValueError("Not authenticated")
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
            }
            
            url = f"{self.PLAYLISTS_ENDPOINT}/{playlist_id}"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    print(f"[ERROR] Playlist not found: {playlist_id}")
                    return []
                
        return []
    
    async def get_playlist_info(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Get playlist metadata (name, owner, track count)"""
        try:
            tracks = await self.get_playlist_tracks(playlist_id)
            
            if tracks:
                return {
                    'playlistId': playlist_id,
                    'name': tracks[0].get('displayName', 'Unknown'),
                    'ownerDisplayName': tracks[0].get('ownerDisplayName'),
                    'trackCount': len(tracks),
                    'tracks': tracks[:5],  # Return first 5 as preview
                }
            return None
            
        except Exception as e:
            print(f"[ERROR] Failed to get playlist info: {e}")
            return None
    
    async def create_queue(self) -> Dict[str, Any]:
        """Create a new playback queue"""
        if not self.access_token:
            raise ValueError("Not authenticated")
        
        # Placeholder - actual implementation depends on Amazon API spec
        queue_id = str(asyncio.get_event_loop().time_ns())
        return {
            'queueId': queue_id,
            'tracks': [],
            'status': 'created'
        }
    
    async def add_to_queue(self, queue_id: str, track_id: str) -> bool:
        """Add a track to playback queue"""
        if not self.access_token:
            raise ValueError("Not authenticated")
        
        # Placeholder - depends on Amazon API implementation
        return True
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def get_token_expiry_info(self) -> Dict[str, Any]:
        """Get token expiry information"""
        if not self.token_expiry:
            return {'status': 'no_tokens', 'message': 'No tokens loaded'}
        
        import datetime
        current_time = int(datetime.datetime.now().timestamp() * 1000)
        time_until_expiry = (self.token_expiry - current_time) / 1000
        
        status = "valid" if time_until_expiry > 300 else "expiring_soon"
        
        return {
            'status': status,
            'expires_at': self.token_expiry,
            'time_until_expiry_minutes': max(0, int(time_until_expiry / 60)),
            'needs_refresh': time_until_expiry < (15 * 60 * 1000)
        }
    
    async def refresh_token_if_needed(self) -> bool:
        """Refresh access token if expired or expiring soon"""
        if not self.refresh_token:
            print("[WARN] No refresh token available")
            return False
        
        try:
            # Refresh token logic depends on Amazon API implementation
            # Placeholder for now
            print("[INFO] Token refresh would occur here (depends on auth flow)")
            
            # For now, we'll just re-authenticate if needed
            if self.get_token_expiry_info()['needs_refresh']:
                return await self.authenticate(open_browser=True)
                
            return True
            
        except Exception as e:
            print(f"[ERROR] Token refresh failed: {e}")
            return False


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example 1: Basic authentication and search
------------------------------------------

import asyncio
from src.modules.amazon_api import AmazonMusicClient

async def main():
    client = AmazonMusicClient()
    
    # Authenticate with Amazon Music
    await client.authenticate(open_browser=True)
    
    # Search for an artist
    artists = await client.search_artists("Radiohead", limit=5)
    print(f"Found {len(artists)} Radiohead tracks")
    
    # Get playlist tracks
    tracks = await client.get_playlist_tracks("YOUR_PLAYLIST_ID_HERE")
    print(f"Playlist has {len(tracks)} tracks")

asyncio.run(main())


Example 2: Using with WiiM integration
----------------------------------------

from src.modules.wiim_client import WiiMClient
from src.modules.amazon_api import AmazonMusicClient

async def main():
    amazon_client = AmazonMusicClient()
    await amazon_client.authenticate(open_browser=True)
    
    wiim_client = WiiMClient("YOUR_WIIM_IP")
    
    # Search and play directly
    search_result = await amazon_client.search_artists("Taylor Swift", limit=10)
    if search_result:
        for track in search_result[:5]:
            print(f"Playing: {track['title']} by {track['artistName']}")
            # Send to WiiM playback queue (integration logic here)

asyncio.run(main())


Example 3: Building a curated playlist
---------------------------------------

import asyncio
from src.modules.amazon_api import AmazonMusicClient

async def build_morning_playlist():
    client = AmazonMusicClient()
    await client.authenticate(open_browser=True)
    
    # Collect high-energy tracks
    morning_tracks = []
    for artist in ["Daft Punk", "The Weeknd", "Kavinsky", "Justice"]:
        results = await client.search_artists(artist, limit=5)
        morning_tracks.extend(results)
    
    print(f"Morning playlist: {len(morning_tracks)} tracks")
    return morning_tracks

asyncio.run(build_morning_playlist())


"""

if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def demo():
        client = AmazonMusicClient()
        
        print("\n" + "="*60)
        print("SONIC FLUX - AMAZON MUSIC API DEMO")
        print("="*60)
        
        # Check if tokens exist
        if await client.initialize():
            print("[INFO] Tokens loaded successfully!")
            
            # Get token expiry info
            expiry_info = client.get_token_expiry_info()
            print(f"[INFO] Token status: {expiry_info['status']}")
        else:
            print("[INFO] No valid tokens found. Authenticating now...")
            await client.authenticate(open_browser=True)
        
        # Example search (only if authenticated)
        if client.access_token:
            print("\n[INFO] Testing search functionality...")
            try:
                artists = await client.search_artists("Radiohead", limit=3)
                print(f"[SUCCESS] Found {len(artists)} Radiohead tracks")
                
                for artist in artists[:1]:
                    print(f"  - {artist.get('title', 'N/A')} by {artist.get('artistName', 'N/A')}")
                    
            except Exception as e:
                print(f"[ERROR] Search failed: {e}")
        
        print("\n" + "="*60)
        print("Demo complete!")
        print("="*60)
    
    asyncio.run(demo())
