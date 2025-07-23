"""
Ultra SSL Bypass - Completely disable SSL verification everywhere
"""

import os
import ssl
import warnings
import sys

def nuclear_ssl_bypass():
    """Nuclear option - disable SSL verification completely"""
    
    # Environment variables
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['SSL_VERIFY'] = 'false'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Completely disable SSL
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Monkey patch ssl module
    ssl.create_default_context = ssl._create_unverified_context
    ssl.match_hostname = lambda cert, hostname: True
    
    # Disable all SSL warnings
    warnings.filterwarnings('ignore')
    
    # Patch at import time
    try:
        import urllib3
        urllib3.disable_warnings()
        from urllib3.exceptions import InsecureRequestWarning
        urllib3.disable_warnings(InsecureRequestWarning)
    except:
        pass
    
    try:
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        # Force requests to not verify SSL
        requests.adapters.DEFAULT_RETRIES = 3
        requests.Session.verify = False
    except:
        pass
    
    try:
        import httpx
        # Monkey patch httpx Client to never verify SSL
        original_init = httpx.Client.__init__
        def no_verify_init(self, *args, **kwargs):
            kwargs['verify'] = False
            return original_init(self, *args, **kwargs)
        httpx.Client.__init__ = no_verify_init
        
        # Also patch AsyncClient
        original_async_init = httpx.AsyncClient.__init__
        def no_verify_async_init(self, *args, **kwargs):
            kwargs['verify'] = False
            return original_async_init(self, *args, **kwargs)
        httpx.AsyncClient.__init__ = no_verify_async_init
    except:
        pass
    
    print("🔥 Nuclear SSL bypass activated - ALL SSL verification disabled")

# Apply immediately when imported
nuclear_ssl_bypass()
