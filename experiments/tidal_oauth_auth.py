"""
TIDAL OAuth Authentication Helper - Browser-Based Authorization Flow
======================================================================
This script handles the browser-based OAuth authorization flow:

1. Launches browser and navigates to TIDAL authorization page
2. Waits for user to authorize and complete login
3. Captures redirect URL with authorization code
4. Exchanges code for tokens using PKCE

USAGE:
    python experiments/tidal_oauth_auth.py
    
This will open your default browser and guide you through the authorization process.
After authorization, tokens will be saved to data/tidal_token_store.json
"""

import sys
import os
import time
import subprocess


def main():
    """Run the OAuth authentication flow."""
    
    print("\n" + "=" * 80)
    print("🎵 SONIC FLUX - TIDAL OAUTH AUTHORIZATION FLOW")
    print("=" * 80)
    print("\nThis will guide you through authorizing Sonic Flux to access your TIDAL account.")
    
    # Load credentials from .env (secure loading)
    try:
        from tidal_api_auth_test import load_credentials_securely
        client_id, client_secret = load_credentials_securely()
        print(f"\n✅ Client ID loaded (secured)")
    except Exception as e:
        print(f"\n❌ Failed to load credentials: {e}")
        return
    
    # Check if we already have a valid token
    try:
        sys.path.insert(0, r'C:\HermesWiiM\src\modules')
        from tidal_oauth_flow_client import TidalOAuthFlowClient
        
        api = TidalOAuthFlowClient(client_id, client_secret)
        
        if api.has_valid_token():
            print("\n✅ You already have a valid cached token!")
            
            # Load and display token info
            token_info = api.load_token()
            print(f"\nToken details:")
            print(f"  • Scope: {token_info.get('scope', 'Not specified')}")
            print(f"  • Expires in: {token_info.get('expires_in')} ms ({token_info.get('expires_in')/1000:.1f} seconds)")
            
            print("\n🎉 You're already authenticated! Try using the API now.")
            print("   Run: python experiments/tidal_api_test_secure.py")
            return
            
    except Exception as e:
        print(f"\n⚠️  Could not check existing token (will proceed with new auth): {e}")
    
    # Get redirect URI - must match what's registered in TIDAL developer portal
    # For local development, use http://localhost:8000/callback or similar
    REDIRECT_URI = "http://localhost:8000/callback"
    
    print(f"\n📌 Using redirect URI: {REDIRECT_URI}")
    print("   ⚠️  Make sure this matches what you registered in the TIDAL developer portal!")
    
    # Generate authorization URL with PKCE
    auth_info = api.get_authorization_url(redirect_uri=REDIRECT_URI, scope="data:read data:write")
    auth_url = auth_info['url']
    code_verifier = auth_info['code_verifier']
    redirect_uri = auth_info['redirect_uri']
    
    print(f"\n📌 Authorization URL generated with PKCE (S256)")
    
    # Launch browser to authorization page
    print("\n🔍 Launching your default browser to TIDAL authorization page...")
    print("   Please complete the following steps:\n")
    print("   1. Approve any permissions requested by Sonic Flux")
    print("   2. Enter your TIDAL username/password if prompted")
    print("   3. Wait for browser to redirect back to localhost with authorization code\n")
    
    try:
        import webbrowser
        webbrowser.open(auth_url)
        
        print(f"✅ Browser opened! Authorization URL:\n{auth_url[:200]}...")
        
        # Poll for completion (check if we captured the redirect)
        print("\n⏳ Waiting for authorization to complete...")
        print("   Check your browser for the redirect to http://localhost:8000/callback\n")
        
        print("\n📋 To check if authorization is complete:")
        print("   1. Look for a URL like: http://localhost:8000/callback?code=YOUR_AUTH_CODE&...")
        print("   2. If you see this, copy the entire code parameter value (after 'code=')")
        print("   3. Paste it below when prompted\n")
        
        # Wait for user confirmation
        input("\n⚠️  Press ENTER to check browser and provide authorization code:")
        
        auth_code = None
        
        while not auth_code:
            auth_code = input("Paste the authorization code from URL: ").strip()
            
            if not auth_code:
                print("\n❌ Code cannot be empty. Please copy it from the redirect URL.")
                continue
            
            # Verify it looks like a valid TIDAL auth code (long alphanumeric string)
            if len(auth_code) < 32 or len(auth_code) > 100:
                print(f"\n⚠️  Code length ({len(auth_code)}) seems unusual. Check the URL again.")
                continue
            
            # Exchange code for tokens
            print(f"\n📌 Exchanging authorization code for tokens...")
            
            try:
                tokens = api.exchange_code_for_tokens(
                    code=auth_code,
                    code_verifier=code_verifier,
                    redirect_uri=redirect_uri
                )
                
                print("\n✅ Token exchange successful!")
                print(f"\nToken details:")
                print(f"  • Access Token: {tokens['access_token'][:30]}...")
                print(f"  • Expires in: {tokens['expires_in']} ms ({tokens['expires_in']/1000:.1f} seconds)")
                print(f"  • Scope: {tokens.get('scope', 'Not specified')}")
                
                # Save tokens to file
                api.save_token(tokens)
                print("\n💾 Tokens saved to:", api.DEFAULT_TOKEN_STORE_PATH)
                
                # Display token expiry info
                created_at = time.time() * 1000
                expires_in = tokens['expires_in']
                expiration_time = (created_at + expires_in) / 1000
                
                print(f"\n📌 Token will expire at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiration_time))}")
                
                print("\n" + "=" * 80)
                print("🎉 AUTHORIZATION COMPLETE!")
                print("=" * 80)
                print("\nYou can now use the API with full user-scoped access!")
                print("\nTry these commands:")
                print("  • python experiments/tidal_api_test_secure.py")
                print("  • python src/modules/tidal_api.py (import and call methods)")
                
            except Exception as e:
                print(f"\n❌ Token exchange failed: {e}")
                print("\n⚠️  This could mean:")
                print("   • Redirect URI doesn't match what's registered in TIDAL developer portal")
                print("   • Authorization code expired (try again)")
                print("   • Client credentials are incorrect")
                
                # Show how to check registered redirect URI
                print("\n📌 To verify your registered redirect URI:")
                print("   1. Go to: https://developer.tidal.com/documentation/api-sdk/authorization")
                print("   2. Check the 'Redirect URI' field in your app registration")
                print("   3. Make sure it matches: http://localhost:8000/callback\n")

    except Exception as e:
        print(f"\n❌ Error launching browser or completing flow: {e}")
    
    print("\n" + "=" * 80)
    print("AUTHORIZATION FLOW COMPLETE (or interrupted)")
    print("=" * 80)


if __name__ == "__main__":
    main()
