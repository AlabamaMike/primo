"""
SSL Bypass Configuration for Windows Development
This module ensures all SSL certificate issues are resolved
"""

import os
import ssl
import warnings
import urllib3
from urllib3.exceptions import InsecureRequestWarning

def configure_ssl_bypass():
    """Configure SSL bypass for all HTTP libraries"""
    
    # Disable SSL warnings
    urllib3.disable_warnings(InsecureRequestWarning)
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    # Set environment variables
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['SSL_VERIFY'] = 'false'
    
    # Monkey patch SSL context
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Patch httpx if available
    try:
        import httpx
        # Create a custom client that doesn't verify SSL
        original_client = httpx.Client
        
        def unverified_client(*args, **kwargs):
            kwargs['verify'] = False
            return original_client(*args, **kwargs)
        
        httpx.Client = unverified_client
    except ImportError:
        pass
    
    # Patch requests if available
    try:
        import requests
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        # Monkey patch requests.Session to disable SSL verification
        original_request = requests.Session.request
        
        def no_ssl_request(self, method, url, **kwargs):
            kwargs['verify'] = False
            return original_request(self, method, url, **kwargs)
        
        requests.Session.request = no_ssl_request
    except ImportError:
        pass
    
    print("🔓 SSL verification disabled for all HTTP libraries")

# Apply SSL bypass immediately when this module is imported
configure_ssl_bypass()
