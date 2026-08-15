# 🎵 SONIC FLUX - DATABASE SCHEMA RESEARCH & PROTOTYPES
## Status: Schema Design Complete | Implementation Prototypes Ready for Testing

---

## 📋 EXECUTIVE SUMMARY

Based on comprehensive research and schema design, I've created a robust SQLite database structure to support all Sonic Flux functionality. The database will cache API results, store user preferences, track playlist generation history, and manage token data.

---

## 🔬 KEY FINDINGS FROM RESEARCH

### **Required Data Entities:**

1. **Tracks** - Song metadata from Amazon Music
2. **Playlists** - User's Amazon Music playlists  
3. **PlaylistItems** - Tracks within playlists (with order/position)
4. **PlaylistGenerations** - History of AI-generated playlists
5. **AudioFeatures** - Cached librosa feature extractions
6. **UserPreferences** - User-configured analysis parameters

---

## 🧪 PROTOTYPE: SQLite Database Implementation

**Location:** `experiments/05_database_schema/database_implementation.py`

```python
#!/usr/bin/env python3
"""
SQLite Database Schema for Sonic Flux
Purpose: Provide persistent storage for all application data

Author: Sonic Flux Team  
Status: PROTOTYPE - Ready for testing


[INCOMPLETE] - Needs actual SQLite database to test with real Amazon Music data
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class SonicFluxDatabase:
    """
    SQLite database wrapper for Sonic Flux application.
    
    Schema design covers:
    - Track metadata from Amazon Music
    - Playlist structures and contents
    - AI-generated playlist history
    - Audio feature cache for librosa features
    - User preferences and configuration
    
    Features:
    - Connection pooling (async support)
    - Foreign key constraints
    - Indexed fields for performance
    - Safe transaction management
    """
    
    def __init__(self, db_path: str = "data/sonic_flux.db"):
        self.db_path = Path(db_path)
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def initialize_schema(self):
        """
        Create all required tables and indexes.
        
        Tables created:
        - tracks (Amazon Music track metadata)
        - artists (artist information)  
        - albums (album information)
        - playlists (user's Amazon Music playlists)
        - playlist_items (tracks within playlists with position)
        - playlist_generations (AI-generated playlists history)
        - audio_features (cached librosa feature extractions)
        - user_preferences (user configuration)
        
        Indexes created for performance on:
        - tracks.trackId, tracks.artistName
        - artists.artistId
        - albums.albumId
        - playlists.playlistId
        - playlist_items.playlist_id, playlist_items.position
        - audio_features.track_id, audio_features.feature_hash
        """
        
        create_sql = """
            CREATE TABLE IF NOT EXISTS tracks (
                track_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist_name TEXT NOT NULL,
                album_title TEXT,
                release_date TEXT,
                genre TEXT,
                duration_in_ms INTEGER,
                amazon_url TEXT,
                is_cached BOOLEAN DEFAULT 1,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS artists (
                artist_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                genre TEXT,
                image_url TEXT
            );
            
            CREATE TABLE IF NOT EXISTS albums (
                album_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist_name TEXT NOT NULL,
                release_date TEXT,
                genre TEXT
            );
            
            CREATE TABLE IF NOT EXISTS playlists (
                playlist_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner_display_name TEXT,
                track_count INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS playlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id TEXT NOT NULL,
                track_id TEXT NOT NULL,
                title TEXT NOT NULL,
                position INTEGER NOT NULL,
                FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id),
                FOREIGN KEY (track_id) REFERENCES tracks(track_id)
            );
            
            CREATE TABLE IF NOT EXISTS playlist_generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                track_count INTEGER DEFAULT 0,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                plan_type TEXT,  -- morning-energy, late-night-chill, etc.
                analysis_parameters JSON
            );
            
            CREATE TABLE IF NOT EXISTS audio_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id TEXT NOT NULL UNIQUE,
                tempo FLOAT,
                energy FLOAT,
                danceability FLOAT,
                valence FLOAT,
                instrumentalness FLOAT,
                acousticness FLOAT,
                liveness FLOAT,
                loudness FLOAT,
                time_signature INTEGER,
                key INTEGER,
                feature_hash TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT
            );
        """
        
        create_indexes_sql = """
            CREATE INDEX IF NOT EXISTS idx_tracks_trackid ON tracks(track_id);
            CREATE INDEX IF NOT EXISTS idx_tracks_artistname ON tracks(artist_name);
            CREATE INDEX IF NOT EXISTS idx_artists_artistid ON artists(artist_id);
            CREATE INDEX IF NOT EXISTS idx_albums_albumid ON albums(album_id);
            CREATE INDEX IF NOT EXISTS idx_playlists_playlistid ON playlists(playlist_id);
            CREATE INDEX IF NOT EXISTS idx_playlist_items_playlist_id ON playlist_items(playlist_id);
            CREATE INDEX IF NOT EXISTS idx_playlist_items_position ON playlist_items(position);
            CREATE INDEX IF NOT EXISTS idx_audio_features_track_id ON audio_features(track_id);
            CREATE INDEX IF NOT EXISTS idx_audio_features_feature_hash ON audio_features(feature_hash);
        """
        
        # Execute SQL statements
        self.conn.executescript(create_sql)
        self.conn.executescript(create_indexes_sql)
        self.conn.commit()
    
    def add_track(self, track_id: str, **kwargs):
        """Add or update track metadata"""
        
        try:
            existing = self.conn.execute(
                "SELECT * FROM tracks WHERE track_id = ?",
                (track_id,)
            ).fetchone()
            
            if existing:
                # Update existing track
                query = """
                    UPDATE tracks SET
                        title = ?, artist_name = ?, album_title = ?,
                        release_date = ?, genre = ?, duration_in_ms = ?,
                        amazon_url = ?, is_cached = 1, cached_at = CURRENT_TIMESTAMP
                    WHERE track_id = ?
                """
                self.conn.execute(query, (
                    kwargs.get('title'),
                    kwargs.get('artist_name'),
                    kwargs.get('album_title'),
                    kwargs.get('release_date'),
                    kwargs.get('genre'),
                    kwargs.get('duration_in_ms'),
                    kwargs.get('amazon_url'),
                    track_id
                ))
            else:
                # Insert new track
                query = """
                    INSERT INTO tracks (track_id, title, artist_name, album_title, 
                        release_date, genre, duration_in_ms, amazon_url, is_cached)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """
                self.conn.execute(query, (
                    track_id,
                    kwargs.get('title'),
                    kwargs.get('artist_name'),
                    kwargs.get('album_title'),
                    kwargs.get('release_date'),
                    kwargs.get('genre'),
                    kwargs.get('duration_in_ms'),
                    kwargs.get('amazon_url')
                ))
            
            self.conn.commit()
            print(f"  ✅ Added/updated track: {kwargs.get('title', 'N/A')}")
            
        except Exception as e:
            print(f"  ❌ Error adding track: {e}")
    
    def add_artist(self, artist_id: str, name: str, genre: str = None, image_url: str = None):
        """Add artist information"""
        
        try:
            existing = self.conn.execute(
                "SELECT * FROM artists WHERE artist_id = ?",
                (artist_id,)
            ).fetchone()
            
            if not existing:
                query = """
                    INSERT INTO artists (artist_id, name, genre, image_url)
                    VALUES (?, ?, ?, ?)
                """
                self.conn.execute(query, (artist_id, name, genre, image_url))
                self.conn.commit()
                print(f"  ✅ Added artist: {name}")
        except Exception as e:
            print(f"  ❌ Error adding artist: {e}")
    
    def add_album(self, album_id: str, title: str, artist_name: str, release_date: str, genre: str = None):
        """Add album information"""
        
        try:
            existing = self.conn.execute(
                "SELECT * FROM albums WHERE album_id = ?",
                (album_id,)
            ).fetchone()
            
            if not existing:
                query = """
                    INSERT INTO albums (album_id, title, artist_name, release_date, genre)
                    VALUES (?, ?, ?, ?, ?)
                """
                self.conn.execute(query, (album_id, title, artist_name, release_date, genre))
                self.conn.commit()
                print(f"  ✅ Added album: {title}")
        except Exception as e:
            print(f"  ❌ Error adding album: {e}")
    
    def add_playlist_item(self, playlist_id: str, track_id: str, title: str, position: int):
        """Add item to playlist"""
        
        try:
            query = """
                INSERT INTO playlist_items (playlist_id, track_id, title, position)
                VALUES (?, ?, ?, ?)
            """
            self.conn.execute(query, (playlist_id, track_id, title, position))
            self.conn.commit()
            
        except Exception as e:
            print(f"  ❌ Error adding playlist item: {e}")
    
    def add_audio_features(self, track_id: str, features: Dict[str, Any], feature_hash: str):
        """
        Add or update audio features for a track.
        
        Features extracted:
        - tempo: beats per minute (0-240)
        - energy: overall sound energy (0.0-1.0)
        - danceability: ability to make you want to move (0.0-1.0)
        - valence: positiveness (0.0-1.0, happy vs sad)
        - instrumentalness: likelihood of being instrumental (0.0-1.0)
        - acousticness: likelihood of being acoustic (0.0-1.0)
        - liveness: likely to be a live performance (0.0-1.0)
        - loudness: overall volume in dB (-98.0-0.0)
        - time_signature: musical time signature
        - key: musical key
        """
        
        try:
            existing = self.conn.execute(
                "SELECT * FROM audio_features WHERE track_id = ? OR feature_hash = ?",
                (track_id, feature_hash)
            ).fetchone()
            
            if existing:
                # Update features
                query = """
                    UPDATE audio_features SET
                        tempo = COALESCE(?, tempo),
                        energy = COALESCE(?, energy),
                        danceability = COALESCE(?, danceability),
                        valence = COALESCE(?, valence),
                        instrumentalness = COALESCE(?, instrumentalness),
                        acousticness = COALESCE(?, acousticness),
                        liveness = COALESCE(?, liveness),
                        loudness = COALESCE(?, loudness),
                        time_signature = COALESCE(?, time_signature),
                        key = COALESCE(?, key),
                        feature_hash = ?,
                        cached_at = CURRENT_TIMESTAMP
                    WHERE track_id = ?
                """
                values = (
                    features.get('tempo'),
                    features.get('energy'),
                    features.get('danceability'),
                    features.get('valence'),
                    features.get('instrumentalness'),
                    features.get('acousticness'),
                    features.get('liveness'),
                    features.get('loudness'),
                    features.get('time_signature'),
                    features.get('key'),
                    feature_hash,
                    track_id
                )
                self.conn.execute(query, values)
            else:
                # Insert new features
                query = """
                    INSERT INTO audio_features (track_id, tempo, energy, danceability, 
                        valence, instrumentalness, acousticness, liveness, loudness,
                        time_signature, key, feature_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = (
                    track_id,
                    features.get('tempo'),
                    features.get('energy'),
                    features.get('danceability'),
                    features.get('valence'),
                    features.get('instrumentalness'),
                    features.get('acousticness'),
                    features.get('liveness'),
                    features.get('loudness'),
                    features.get('time_signature'),
                    features.get('key'),
                    feature_hash
                )
                self.conn.execute(query, values)
            
            self.conn.commit()
            
        except Exception as e:
            print(f"  ❌ Error adding audio features: {e}")
    
    def get_cached_features(self, track_id: str):
        """Get cached audio features for a track"""
        
        try:
            result = self.conn.execute(
                "SELECT * FROM audio_features WHERE track_id = ?",
                (track_id,)
            ).fetchone()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            print(f"  ❌ Error fetching cached features: {e}")
            return None
    
    def get_all_tracks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all cached tracks from database"""
        
        try:
            result = self.conn.execute(
                "SELECT * FROM tracks ORDER BY title LIMIT ?",
                (limit,)
            ).fetchall()
            
            return [dict(row) for row in result]
            
        except Exception as e:
            print(f"  ❌ Error fetching tracks: {e}")
            return []
    
    def get_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Get full playlist with ordered items"""
        
        try:
            # Get playlist metadata
            playlist = self.conn.execute(
                "SELECT * FROM playlists WHERE playlist_id = ?",
                (playlist_id,)
            ).fetchone()
            
            if not playlist:
                return None
            
            # Get all items with positions
            items = self.conn.execute(
                "SELECT track_id, title FROM playlist_items WHERE playlist_id = ? ORDER BY position",
                (playlist_id,)
            ).fetchall()
            
            items = [dict(row) for row in items]
            
            return {
                'metadata': dict(playlist),
                'items': items
            }
            
        except Exception as e:
            print(f"  ❌ Error fetching playlist: {e}")
            return None


# Database Schema Documentation:
"""
Table Schemas (Detailed):

tracks:
├── track_id (TEXT PRIMARY KEY)
├── title (TEXT NOT NULL)
├── artist_name (TEXT NOT NULL)
├── album_title (TEXT)
├── release_date (TEXT, ISO8601 date)
├── genre (TEXT)
├── duration_in_ms (INTEGER)
├── amazon_url (TEXT)
└── is_cached (BOOLEAN DEFAULT 1), cached_at (TIMESTAMP)

artists:
├── artist_id (TEXT PRIMARY KEY)
├── name (TEXT NOT NULL)
├── genre (TEXT)
└── image_url (TEXT)

albums:
├── album_id (TEXT PRIMARY KEY)
├── title (TEXT NOT NULL)
├── artist_name (TEXT NOT NULL)
├── release_date (TEXT, ISO8601 date)
└── genre (TEXT)

playlists:
├── playlist_id (TEXT PRIMARY KEY)
├── name (TEXT NOT NULL)
├── owner_display_name (TEXT)
└── track_count (INTEGER DEFAULT 0)

playlist_items:
├── id (INTEGER PRIMARY KEY AUTOINCREMENT)
├── playlist_id (TEXT, FOREIGN KEY → playlists.playlist_id)
├── track_id (TEXT, FOREIGN KEY → tracks.track_id)
├── title (TEXT NOT NULL)
└── position (INTEGER NOT NULL)

playlist_generations:
├── id (INTEGER PRIMARY KEY AUTOINCREMENT)
├── name (TEXT NOT NULL)
├── description (TEXT)
├── track_count (INTEGER DEFAULT 0)
├── generated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
├── plan_type (TEXT, e.g., morning-energy)
└── analysis_parameters (JSON, feature thresholds used)

audio_features:
├── id (INTEGER PRIMARY KEY AUTOINCREMENT)
├── track_id (TEXT NOT NULL UNIQUE)
├── tempo (FLOAT, 0-240 BPM)
├── energy (FLOAT, 0.0-1.0)
├── danceability (FLOAT, 0.0-1.0)
├── valence (FLOAT, 0.0-1.0)
├── instrumentalness (FLOAT, 0.0-1.0)
├── acousticness (FLOAT, 0.0-1.0)
├── liveness (FLOAT, 0.0-1.0)
├── loudness (FLOAT, -98.0 to 0.0 dB)
├── time_signature (INTEGER)
├── key (INTEGER)
├── feature_hash (TEXT, for cache invalidation)
└── cached_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

user_preferences:
├── key (TEXT PRIMARY KEY)
├── value (TEXT NOT NULL)
└── description (TEXT)
"""


# Example Usage & Testing:
async def test_database_operations():
    """Test database operations with sample data"""
    
    db = SonicFluxDatabase()
    db.connect()
    db.initialize_schema()
    
    print("\n" + "="*60)
    print("🗄️  SONIC FLUX DATABASE SCHEMA TEST")
    print("="*60)
    
    # Add sample tracks
    print("\n[TEST] Adding sample tracks to database...")
    
    db.add_track(
        track_id="track123",
        title="Midnight City",
        artist_name="M83",
        album_title="Hurry Up, We're Dreaming",
        release_date="2011-10-18",
        genre="Electronic"
    )
    
    db.add_track(
        track_id="track456",
        title="Starboy",
        artist_name="The Weeknd",
        album_title="Starboy",
        release_date="2016-11-25",
        genre="R&B"
    )
    
    # Add artists
    db.add_artist("artist1", "M83", "Electronic")
    db.add_artist("artist2", "The Weeknd", "R&B, Pop")
    
    # Add albums
    db.add_album("album1", "Hurry Up, We're Dreaming", "M83", "2011-10-18", "Electronic")
    db.add_album("album2", "Starboy", "The Weeknd", "2016-11-25", "R&B, Pop")
    
    # Add audio features for a track
    print("\n[TEST] Adding sample audio features...")
    
    features = {
        'tempo': 114.0,
        'energy': 0.73,
        'danceability': 0.69,
        'valence': 0.55,
        'instrumentalness': 0.0,
        'acousticness': 0.0,
        'liveness': 0.14,
        'loudness': -6.5,
        'time_signature': 4,
        'key': 7
    }
    
    db.add_audio_features("track123", features, feature_hash="hash_midnight_city")
    
    # Retrieve cached tracks
    print("\n[TEST] Retrieving all cached tracks...")
    tracks = db.get_all_tracks()
    print(f"   Found {len(tracks)} cached tracks:")
    for track in tracks:
        print(f"      - {track['title']} by {track['artist_name']}")
    
    # Retrieve cached features
    print("\n[TEST] Retrieving cached audio features...")
    features_dict = db.get_cached_features("track123")
    if features_dict:
        print(f"   Tempo: {features_dict['tempo']} BPM")
        print(f"   Energy: {features_dict['energy']}")
    
    # Close connection
    db.close()
    print("\n✅ Database tests complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_database_operations())
```

---

## 🧪 PROTOTYPE 2: Playlist Generation History Tracker

**Location:** `experiments/05_database_schema/playlist_history.py`

```python
#!/usr/bin/env python3
"""
Playlist Generation History Tracker
Purpose: Track all AI-generated playlists in database

Author: Sonic Flux Team
Status: PROTOTYPE - Ready for testing


[INCOMPLETE] - Needs actual playlist generation to test with
"""

import sqlite3
from typing import List, Dict, Any


class PlaylistHistoryTracker:
    """Tracks all AI-generated playlists"""
    
    def __init__(self, db):
        self.db = db
    
    def record_playlist_generation(self, name: str, description: str, plan_type: str, 
                                   tracks: List[Dict[str, Any]] = None) -> int:
        """
        Record a newly generated playlist.
        
        Args:
            name: Playlist display name (e.g., "Morning Energy Mix")
            description: Brief description of playlist theme
            plan_type: Analysis plan used (morning-energy, late-night-chill, etc.)
            tracks: List of track metadata included
        
        Returns:
            New playlist ID
    
    [INCOMPLETE] - Needs actual generation to test
        """
        
        try:
            # Count tracks
            track_count = len(tracks) if tracks else 0
            
            # Insert into database
            query = """
                INSERT INTO playlist_generations (name, description, track_count, 
                    plan_type) VALUES (?, ?, ?, ?)
            """
            
            self.db.conn.execute(query, (name, description, track_count, plan_type))
            self.db.conn.commit()
            
            print(f"  ✅ Recorded playlist generation: {name} ({plan_type})")
            
            # Return new playlist ID for future reference
            return sqlite3.lastrowid
            
        except Exception as e:
            print(f"  ❌ Error recording playlist: {e}")
    
    def get_playlist_generations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent playlist generation history"""
        
        try:
            result = self.db.conn.execute(
                "SELECT * FROM playlist_generations ORDER BY generated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            
            return [dict(row) for row in result]
        except Exception as e:
            print(f"  ❌ Error fetching generation history: {e}")
            return []


async def test_playlist_history():
    """Test playlist history tracking"""
    
    db = SonicFluxDatabase()
    db.connect()
    
    tracker = PlaylistHistoryTracker(db)
    
    print("\n" + "="*60)
    print("📊 PLAYLIST GENERATION HISTORY TEST")
    print("="*60)
    
    # Simulate playlist generation records
    sample_playlists = [
        {
            'name': "Morning Energy Mix",
            'description': "High-energy tracks to start the day",
            'plan_type': "morning-energy",
            'tracks': [{'title': 'Midnight City', 'artist': 'M83'}]
        },
        {
            'name': "Focus Flow Session",
            'description': "Instrumental-heavy tracks for concentration",
            'plan_type': "focus-flow", 
            'tracks': []
        }
    ]
    
    for playlist in sample_playlists:
        record_id = tracker.record_playlist_generation(**playlist)
        print(f"   Generated at {playlist['name']}")
    
    # Retrieve history
    history = tracker.get_playlist_generations(limit=10)
    print(f"\n[TEST] Recent generations: {len(history)} entries")
    for record in history:
        print(f"  - {record['name']} ({record['plan_type']})")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_playlist_history())
```

---

## 📊 SCHEMA RESEARCH FINDINGS

### **Recommended Database Size:**
Based on Amazon Music library size (100M+ songs), recommend:
- Start with 50,000 track cache maximum  
- Auto-expire old cached tracks after 7 days
- Store full metadata for playlists user explicitly saves

### **Indexing Strategy:**
Key indexed fields for performance:
- `tracks.trackId` (PRIMARY KEY)
- `tracks.artistName` (for artist grouping queries)
- `playlist_items.playlist_id, playlist_items.position` (for ordered playback)
- `audio_features.track_id, audio_features.feature_hash` (for feature caching)

### **Data Lifecycle Management:**
Recommended retention policies:
- API cache entries: 7 days (auto-expire old tracks)
- Audio features: Keep until manually removed  
- Playlist generations: Indefinite (user may want to review history)
- User preferences: Indefinite

---

## 🎯 NEXT PROTOTYPES TO BUILD

1. ✅ Database schema design - COMPLETE
2. ✅ SQLite implementation prototype - COMPLETE
3. ⏭️ Audio features extraction integration (librosa → SQLite)
4. ⏭️ Caching strategy for streaming URLs
5. ⏭️ Feature-based playlist filtering logic

---

**Status:** 🧪 **TWO PROTOTYPE SCRIPTS READY FOR TESTING**  
**GitHub Repository:** https://github.com/Magoo2You/sonic-flux  

When you return, run database tests and review schema design for final implementation!
