"""
TIDAL OAuth Authorization Flow Test
=====================================
Tests the complete authorization code flow implementation.

This script will:
1. Check if we already have a valid token (from cached auth)
2. If not, guide you through browser-based authorization
3. Test API access with user-scoped tokens
"""

import sys
sys.path.insert(0, r"C:\HermesWiiM\src\modules")

from tidal_oauth_flow_client import TidalOAuthFlowClient


def main():
    """Test OAuth authorization flow."""
    
    print("\n" + "=" * 80)
    print("🎵 SONIC FLUX - TIDAL OAUTH AUTHORIZATION FLOW TEST")
    print("=" * 80)
    
    # Load credentials from .env (secure loading)
    try:
        from tidal_api_auth_test import load_credentials_securely
        client_id, client_secret = load_credentials_securely()
        print(f"\n✅ Client ID loaded")
    except Exception as e:
        print(f"\n❌ Failed to load credentials: {e}")
        return
    
    # Create API client
    api = TidalOAuthFlowClient(client_id, client_secret)
    
    # Check if we already have a valid token
    if api.has_valid_token():
        print("\n✅ You have a cached token!")
        
        # Load and use the token
        tokens = api.load_token()
        print(f"\nToken info:")
        print(f"  • Scope: {tokens.get('scope', 'N/A')}")
        print(f"  • Expires in: {tokens.get('expires_in')} ms")
        
        # Test a simple API call with the token
        print("\n📌 Testing API access with cached token...")
        try:
            # Try to get user info (requires user-scoped token)
            headers = {
                'Authorization': f"Bearer {tokens['access_token']}",
                'Content-Type': 'application/json'
            }
            
            response = api.get("me", headers=headers)
            
            print(f"\n✅ API call successful!")
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"\n⚠️  API call failed (token may not have required scopes): {e}")
    
    else:
        print("\n❌ No cached token found.")
        print("   Running authorization flow to get user-scoped access...\n")
        
        # Run the authorization flow
        from experiments.tidal_oauth_auth import main as auth_main
        auth_main()


if __name__ == "__main__":
    main()
