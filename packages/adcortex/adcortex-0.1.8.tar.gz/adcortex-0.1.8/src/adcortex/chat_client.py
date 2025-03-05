"""Chat Client for ADCortex API"""
import os
# import logging
from typing import Optional, List, Dict, Any
import requests
from dataclasses import asdict
from dotenv import load_dotenv

from .types import SessionInfo, Message, Ad

# Load environment variables from .env file
load_dotenv()


DEFAULT_CONTEXT_TEMPLATE = "Here is a product the user might like: {ad_title} - {ad_description} - {link}"
AD_FETCH_URL = "https://adcortex.3102labs.com/ads/match"

# Configure logging
# logging.basicConfig(level=logging.ERROR)
# logger = logging.getLogger(__name__)

class AdcortexChatClient:
    def __init__(
        self,
        session_info: SessionInfo,
        context_template: Optional[str] = DEFAULT_CONTEXT_TEMPLATE,
        api_key: Optional[str] = None,
        num_messages_before_ad: int = 3,
        num_messages_between_ads: int = 2,
    ):
        self.session_info = session_info
        self.context_template = context_template
        self.api_key = api_key or os.getenv("ADCORTEX_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key,
        }

        if not self.api_key:
            raise ValueError("ADCORTEX_API_KEY is not set and not provided")

        self.messages: List[Message] = []  # Initialize messages
        self.num_messages_before_ad = num_messages_before_ad
        self.num_messages_between_ads = num_messages_between_ads
        self.latest_ad: Optional[Ad] = None
        self.shown_ads: List[Dict[str, Any]] = []  # Store shown ads and their message counts

    def __call__(self, role: str, content: str) -> Optional[Dict[str, Any]]:
        """Add a message and fetch an ad if applicable."""
        self.messages.append(Message(role=role, content=content))  # Add the message
        # logger.info(f"Message added: {role} - {content}")

        if self._should_show_ad():
            return self._fetch_ad()  # Fetch and return the ad if applicable
        return None  # No ad to show

    def _fetch_ad(self) -> Optional[Dict[str, Any]]:
        """Fetch an ad based on the current messages."""
        if len(self.messages) < self.num_messages_before_ad:
            # logger.warning("Not enough messages to fetch an ad.")
            return {"ads": []}  # Not enough messages to fetch an ad

        payload = self._prepare_payload()
        response_data = self._send_request(payload)

        if response_data:
            return self._handle_response(response_data)
        return None

    def _prepare_payload(self) -> Dict[str, Any]:
        """Prepare the payload for the ad request."""
        payload = {
            "RGUID": self.session_info.session_id,
            "session_info": asdict(self.session_info),
            "user_data": asdict(self.session_info.user_info),
            "messages": [asdict(message) for message in self.messages[-self.num_messages_before_ad:]],
            "platform": asdict(self.session_info.platform),
        }
        return payload

    def _send_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send the request to the ADCortex API and return the response."""
        try:
            response = requests.post(AD_FETCH_URL, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # logger.error(f"Error fetching ad: {e}")
            return None

    def _handle_response(self, response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle the response from the ad request."""
        ads = response_data.get("ads", [])
        if ads:
            self.latest_ad = Ad(**ads[0])  # Store the last ad seen
            # Store the ad and the current message count
            self.shown_ads.append({
                "ad": self.latest_ad,
                "message_count": len(self.messages)
            })
            # logger.info(f"Ad fetched: {self.latest_ad.ad_title}")
            return self.latest_ad
        # logger.info("No ads returned.")
        return {}

    def _should_show_ad(self) -> bool:
        """Determine if an ad should be shown based on message count."""
        if not self.shown_ads:
            return len(self.messages) >= self.num_messages_before_ad
        
        last_shown_ad = self.shown_ads[-1]
        messages_since_last_ad = len(self.messages) - last_shown_ad["message_count"]
        
        return messages_since_last_ad >= self.num_messages_between_ads 
    
    def create_context(self) -> str:
        """Create a context string for the last seen ad."""
        if self.latest_ad:
            return self.context_template.format(**asdict(self.latest_ad))
        return ""