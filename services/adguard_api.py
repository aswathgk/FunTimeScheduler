"""
AdGuard Home API client for FunTime Scheduler.
Handles communication with AdGuard Home to block/unblock websites.
"""

import requests
import logging
import os
from typing import List, Dict, Optional
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class AdGuardAPI:
    """AdGuard Home API client."""
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        """Initialize AdGuard API client."""
        self.base_url = base_url or os.getenv('ADGUARD_URL', 'http://localhost:3000')
        self.username = username or os.getenv('ADGUARD_USERNAME', 'admin')
        self.password = password or os.getenv('ADGUARD_PASSWORD', '')
        
        # Remove trailing slash
        self.base_url = self.base_url.rstrip('/')
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set timeout
        self.timeout = 10
        
        logger.info(f"AdGuard API initialized for {self.base_url}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if self.username and self.password:
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            return {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
        return {'Content-Type': 'application/json'}
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> Optional[Dict]:
        """Make HTTP request to AdGuard API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Some endpoints return empty responses
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AdGuard API request failed: {method} {url} - {e}")
            return None
        except ValueError as e:
            logger.error(f"AdGuard API response parsing failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test connection to AdGuard Home."""
        try:
            response = self._make_request('GET', '/control/status')
            if response is not None:
                logger.info("AdGuard connection test successful")
                return True
            else:
                logger.error("AdGuard connection test failed")
                return False
        except Exception as e:
            logger.error(f"AdGuard connection test error: {e}")
            return False
    
    def get_filtering_status(self) -> Optional[Dict]:
        """Get current filtering status."""
        return self._make_request('GET', '/control/filtering/status')
    
    def get_blocked_services(self) -> Optional[List[str]]:
        """Get list of blocked services."""
        response = self._make_request('GET', '/control/blocked_services/list')
        if response is not None:
            return response.get('blocked_services', [])
        return None
    
    def add_custom_filter(self, name: str, url: str) -> bool:
        """Add a custom filter list."""
        data = {
            'name': name,
            'url': url,
            'enabled': True
        }
        response = self._make_request('POST', '/control/filtering/add_url', data)
        return response is not None
    
    def get_custom_filters(self) -> Optional[List[Dict]]:
        """Get list of custom filters."""
        response = self._make_request('GET', '/control/filtering/status')
        if response is not None:
            return response.get('filters', [])
        return None
    
    def block_domain(self, domain: str) -> bool:
        """
        Block a domain by adding it to user rules.
        AdGuard Home uses DNS filtering rules format.
        """
        try:
            # Get current user rules
            current_rules = self.get_user_rules()
            if current_rules is None:
                logger.error("Failed to get current user rules")
                return False
            
            # Create blocking rule
            block_rule = f"||{domain}^"
            
            # Check if rule already exists
            if block_rule in current_rules:
                logger.info(f"Domain {domain} is already blocked")
                return True
            
            # Add new rule
            updated_rules = current_rules + [block_rule]
            
            # Update user rules
            if self.set_user_rules(updated_rules):
                logger.info(f"Successfully blocked domain: {domain}")
                return True
            else:
                logger.error(f"Failed to block domain: {domain}")
                return False
                
        except Exception as e:
            logger.error(f"Error blocking domain {domain}: {e}")
            return False
    
    def unblock_domain(self, domain: str) -> bool:
        """
        Unblock a domain by removing it from user rules.
        """
        try:
            # Get current user rules
            current_rules = self.get_user_rules()
            if current_rules is None:
                logger.error("Failed to get current user rules")
                return False
            
            # Create blocking rule to remove
            block_rule = f"||{domain}^"
            
            # Check if rule exists
            if block_rule not in current_rules:
                logger.info(f"Domain {domain} is not currently blocked")
                return True
            
            # Remove rule
            updated_rules = [rule for rule in current_rules if rule != block_rule]
            
            # Update user rules
            if self.set_user_rules(updated_rules):
                logger.info(f"Successfully unblocked domain: {domain}")
                return True
            else:
                logger.error(f"Failed to unblock domain: {domain}")
                return False
                
        except Exception as e:
            logger.error(f"Error unblocking domain {domain}: {e}")
            return False
    
    def get_user_rules(self) -> Optional[List[str]]:
        """Get current user-defined filtering rules."""
        response = self._make_request('GET', '/control/filtering/status')
        if response is not None:
            user_rules = response.get('user_rules', [])
            # AdGuard Home returns user_rules as either a list or a string
            if isinstance(user_rules, list):
                # If it's already a list, return it as-is (filtering out empty rules)
                return [rule.strip() for rule in user_rules if rule and rule.strip()]
            elif isinstance(user_rules, str):
                # If it's a string, split by newlines (legacy format)
                return [rule.strip() for rule in user_rules.split('\n') if rule.strip()]
            return []
        return None
    
    def set_user_rules(self, rules: List[str]) -> bool:
        """Set user-defined filtering rules."""
        # AdGuard Home expects rules as an array
        data = {'rules': rules}
        response = self._make_request('POST', '/control/filtering/set_rules', data)
        return response is not None
    
    def is_domain_blocked(self, domain: str) -> bool:
        """Check if a specific domain is currently blocked."""
        try:
            current_rules = self.get_user_rules()
            if current_rules is None:
                return False
            
            block_rule = f"||{domain}^"
            return block_rule in current_rules
            
        except Exception as e:
            logger.error(f"Error checking if domain {domain} is blocked: {e}")
            return False
    
    def get_stats(self) -> Optional[Dict]:
        """Get AdGuard Home statistics."""
        return self._make_request('GET', '/control/stats')
    
    def reset_stats(self) -> bool:
        """Reset AdGuard Home statistics."""
        response = self._make_request('POST', '/control/stats_reset')
        return response is not None
