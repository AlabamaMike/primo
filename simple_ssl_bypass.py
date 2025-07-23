"""
Simple SSL bypass for Supabase on Windows
"""

import os
import ssl
import warnings

def disable_ssl_verification():
    """Disable SSL verification for development"""
    
    # Set environment variables
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    
    # Create unverified SSL context
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Suppress SSL warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    
    print("🔓 SSL verification disabled")

# Apply immediately
disable_ssl_verification()
