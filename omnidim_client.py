import requests
from typing import Dict, Optional
import config
#

class OmniDimClient:
    """Client for interacting with OmniDimension API to dispatch calls."""
    
    def __init__(self, api_key: str):
        """
        Initialize the OmniDim API client.
        
        Args:
            api_key: Your OmniDimension API key
        """
        self.agent_id = int(config.AGENT_ID)
        self.api_key = api_key
        self.base_url = "https://backend.omnidim.io/api/v1"
    
    def dispatch_call(self, phone_number: str, lead_data: Dict) -> Optional[str]:
        """
        Dispatch a call to a phone number using the configured agent.
        
        Args:
            phone_number: Phone number to call (with country code)
            lead_data: Dictionary containing lead information (name, email, etc.)
            
        Returns:
            Call ID if successful, None if failed
        """
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        call_context = {
            "customer_name": lead_data.get('name', 'Unknown'),
            "email": lead_data.get('email', 'N/A'),
            "lead_id": lead_data.get('lead_id', 'N/A')
        }
        
        payload = {
            "agent_id": self.agent_id,
            "to_number": phone_number,
            "call_context": call_context
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/calls/dispatch",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get('call_id') or data.get('id') or "success"
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
            return None

