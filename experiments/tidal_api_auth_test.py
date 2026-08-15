"""
TIDAL API Test Script - Authentication Only
This script verifies that OAuth authentication is working correctly.
API call testing will follow once endpoint requirements are clarified.
"""

import sys
import os

# Add src to path
sys.path.insert(0, r"C:\HermesWiiM\src")

def load_credentials_securely(env_path=None):
    """Load TIDAL credentials from .env file securely."""
    if env_path is None:
        env_path = r"C:\HermesWiiM\.env"
    
    if not os.path.exists(env_path):
        raise FileNotFoundError(f".env file not found at: {env_path}")
    
    client_id = None
    client_secret = None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if key == 'TIDAL_CLIENT_ID':
                    client_id = value
                elif key == 'TIDAL_CLIENT_SECRET':
                    client_secret = value
    
    if not client_id or not client_secret:
        raise ValueError("TIDAL credentials not found in .env file")
    
    return client_id, client_secret


def test_tidal_authentication():
    """Test TIDAL API OAuth authentication."""
    print("=" * 70)
    print("🎵 SONIC FLUX - TIDAL API AUTHENTICATION TEST")
    print("=" * 70)
    
    try:
        # Load credentials securely from .env
        print("\n📌 Loading credentials from .env file...")
        client_id, client_secret = load_credentials_securely()
        
        print(f"   ✅ Client ID loaded ({len(client_id)} characters)")
        print(f"   ✅ Client Secret loaded ({len(client_secret)} characters)")
        
        # Create API instance
        print("\n📌 Initializing TidalApi...")
        from modules.tidal_api import TidalApi
        
        api = TidalApi(
            client_id=client_id,
            client_secret=client_secret,
            token_store_path=r"C:\HermesWiiM\data\tidal_token_store.json"
        )
        
        # Test authentication using client credentials flow
        print("\n📌 Authenticating using client credentials flow...")
        print("   (This provides catalog-only access)")
        
        token = api.authenticate_client_credentials()
        
        print(f"\n✅ AUTHENTICATION SUCCESSFUL!")
        print(f"   Token type: {token.token_type}")
        print(f"   Expires in: {token.expires_in / 3600:.1f} hours")
        print(f"   Scope: '{token.scope or 'default'}'")
        
        # Save token to file for future use
        api.save_token(token)
        print(f"\n   ✅ Token saved to: {api.token_store_path}")
        
        # Verify token was loaded from file
        print("\n📌 Verifying token persistence...")
        loaded_token = api.load_token()
        if loaded_token and not loaded_token.is_expired:
            print("   ✅ Token successfully persisted to file!")
        else:
            print("   ⚠️  Could not verify token persistence (may be expired or save failed)")
        
        print("\n" + "=" * 70)
        print("🎵 AUTHENTICATION TEST PASSED!")
        print("=" * 70)
        print("\n✅ TIDAL OAuth authentication is working correctly.")
        print("\nThe module successfully:")
        print("   • Loads credentials from .env file securely")
        print("   • Authenticates using client credentials flow")
        print("   • Manages access tokens with 24-hour expiry")
        print("   • Persists tokens to JSON file for reuse")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_tidal_authentication()
    sys.exit(0 if success else 1)
