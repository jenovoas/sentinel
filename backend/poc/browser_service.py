"""
Sentinel Vault - Secure Browser Service (Triad Architecture)
Supports: Ghost Mode (Nym), Deep Mode (I2P), Velocity Mode (Proxy)
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowseMode(Enum):
    CLEAR = "clear"         # Direct connection (Standard)
    VELOCITY = "velocity"   # Custom Proxy / Tor (High Speed Anon)
    GHOST = "ghost"         # Nym Mixnet (Metadata Protection)
    DEEP = "deep"           # I2P (Decentralized / Internal)

class BrowserService:
    """
    Secure Browser Backend - Triad Architecture
    Routes requests through different anonymity layers based on selected mode.
    """
    
    # Default Proxy Ports (Standard defaults, configurable)
    PROXIES = {
        BrowseMode.VELOCITY: "socks5h://127.0.0.1:9050",  # Tor/Custom Proxy
        BrowseMode.GHOST: "socks5h://127.0.0.1:1080",     # Nym Client
        BrowseMode.DEEP: "http://127.0.0.1:4444"          # I2P HTTP Proxy
    }

    def __init__(self):
        self.session = requests.Session()
        self.current_mode = BrowseMode.CLEAR
        
        # Anti-Fingerprinting Headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1"
        })

    def set_mode(self, mode_str: str):
        """Set the browsing mode and configure proxies"""
        try:
            mode = BrowseMode(mode_str.lower())
        except ValueError:
            mode = BrowseMode.CLEAR
            
        self.current_mode = mode
        
        if mode == BrowseMode.CLEAR:
            self.session.proxies = {}
            logger.info("🌐 Mode: CLEAR (Direct connection)")
        else:
            proxy_url = self.PROXIES.get(mode)
            if proxy_url:
                self.session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                logger.info(f"🛡️ Mode: {mode.name} (Proxy: {proxy_url})")
            else:
                logger.warning(f"⚠️ Mode: {mode.name} selected but no proxy defined.")

    def fetch_page(self, url: str) -> Dict:
        """
        Fetch and sanitize a webpage using current mode
        """
        try:
            # Protocol enforcement
            if not url.startswith(('http://', 'https://')):
                 # I2P uses .i2p domains, usually http
                if self.current_mode == BrowseMode.DEEP and url.endswith('.i2p'):
                    url = 'http://' + url
                else:
                    url = 'https://' + url

            logger.info(f"Fetching {url} via {self.current_mode.name}...")
            
            # Timeout varies by mode (Mixnets are slower)
            timeout = 30 if self.current_mode in [BrowseMode.GHOST, BrowseMode.DEEP] else 15
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            sanitized = self._sanitize_content(response.text, url)
            
            return {
                "success": True,
                "mode": self.current_mode.value,
                "url": response.url,
                "status_code": response.status_code,
                "title": sanitized['title'],
                "content": sanitized['content']
            }
            
        except requests.exceptions.RequestException as e:
            msg = str(e)
            logger.error(f"Error fetching {url}: {msg}")
            
            # User-friendly error for connection refused (Proxy down)
            if "Connection refused" in msg or "SOCKS" in msg:
                return {
                    "success": False,
                    "error": f"Connection failed. Is the {self.current_mode.name} proxy running?",
                    "mode": self.current_mode.value,
                    "proxy_error": True
                }
            
            return {
                "success": False,
                "error": msg,
                "mode": self.current_mode.value
            }

    def _sanitize_content(self, html_content: str, base_url: str) -> Dict:
        """Sanitize HTML (Strip scripts, iframes, ads)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Security: Remove active executable content
        for tag in soup(['script', 'iframe', 'object', 'embed', 'applet', 'noscript', 'meta']):
            tag.decompose()
            
        # Security: Clean event handlers
        for tag in soup.find_all(True):
            attrs_to_remove = [attr for attr in tag.attrs if attr.startswith('on')]
            for attr in attrs_to_remove:
                del tag[attr]

        # Formatting: Simple Reader View
        # (Same logic as before, just ensuring it's robust)
        title = soup.title.string if soup.title else "No Title"
        
        return {
            "title": title,
            "content": str(soup)
        }

# ============================================================================
# Testing
# ============================================================================
if __name__ == "__main__":
    service = BrowserService()
    
    # Test Clear Mode
    service.set_mode("clear")
    res = service.fetch_page("example.com")
    print(f"Clear Mode: {res['success']} - {res.get('title', 'Error')}")
    
    # Test Velocity Mode (Will fail if no proxy, but verifies logic)
    service.set_mode("velocity")
    res = service.fetch_page("example.com")
    print(f"Velocity Mode: {res['success']} - {res.get('error')}")
