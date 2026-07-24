"""
Telephony Provider Interface (Abstract Layer)
Defines the common interface for all telephony providers (RingCentral, Twilio, Vapi.ai, etc.)
This allows swapping phone systems without changing core agent logic.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class TelephonyProvider(ABC):
    """Abstract base class for telephony providers."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the telephony provider with configuration credentials."""
        pass
    
    @abstractmethod
    def receive_inbound_call(self, phone_number: str) -> str:
        """
        Handle inbound call routing.
        Returns the webhook URL or SIP URI to route the call to the AI agent.
        """
        pass
    
    @abstractmethod
    def initiate_outbound_call(self, destination_phone: str, webhook_url: str) -> str:
        """
        Initiate an outbound call to a destination phone number.
        Returns call ID or session identifier.
        """
        pass
    
    @abstractmethod
    def transfer_call(self, call_id: str, transfer_destination: str) -> bool:
        """
        Transfer an active call to another number or live agent (warm transfer).
        """
        pass
    
    @abstractmethod
    def end_call(self, call_id: str) -> bool:
        """End or hang up an active call."""
        pass
    
    @abstractmethod
    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Retrieve the current status of a call session."""
        pass
    
    @abstractmethod
    def send_sms(self, destination_phone: str, message: str) -> bool:
        """Send an SMS message to a phone number."""
        pass


class TelephonyAdapterFactory:
    """Factory class to create telephony provider instances based on configuration."""
    
    @staticmethod
    def get_provider(provider_type: str) -> TelephonyProvider:
        """
        Get a telephony provider instance by type.
        
        Supported types:
        - 'ringcentral'
        - 'twilio'
        - 'vapi_ai'
        """
        if provider_type.lower() == 'ringcentral':
            from .ringcentral_provider import RingCentralProvider
            return RingCentralProvider()
        elif provider_type.lower() == 'twilio':
            from .twilio_provider import TwilioProvider
            return TwilioProvider()
        elif provider_type.lower() == 'vapi_ai':
            from .vai_provider import VapiAIProvider
            return VapiAIProvider()
        else:
            raise ValueError(f"Unsupported telephony provider type: {provider_type}")
