"""
Twilio Telephony Provider Implementation
Implements the TelephonyProvider interface for Twilio API integration.
"""
import json
from typing import Dict, Any
from twilio.rest import Client as TwilioClient
from .interface import TelephonyProvider


class TwilioProvider(TelephonyProvider):
    """Twilio telephony provider implementation."""
    
    def __init__(self):
        self.client = None
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the Twilio client with credentials."""
        try:
            account_sid = config.get('twilio_account_sid')
            auth_token = config.get('twilio_auth_token')
            
            self.client = TwilioClient(account_sid, auth_token)
            return True
        except Exception as e:
            print(f"Twilio initialization failed: {str(e)}")
            return False
            
    def receive_inbound_call(self, phone_number: str) -> str:
        """
        Handle inbound call routing.
        Returns the TwiML URL for Twilio to route the call to the AI agent.
        """
        webhook_url = f"{config.get('webhook_base_url', 'https://api.yourcompany.com')}/twilio/webhook"
        return webhook_url
        
    def initiate_outbound_call(self, destination_phone: str, webhook_url: str) -> str:
        """Initiate an outbound call to a destination phone number."""
        try:
            # Twilio REST API for making outbound calls
            call = self.client.calls.create(
                url=webhook_url,  # TwiML URL that handles the call logic
                to=destination_phone,
                from_=config.get('twilio_phone_number'),
                method="POST"
            )
            
            return call.sid  # Return the call session ID
        except Exception as e:
            print(f"Twilio outbound call failed: {str(e)}")
            raise
            
    def transfer_call(self, call_id: str, transfer_destination: str) -> bool:
        """Transfer an active call to another number or live agent (warm transfer)."""
        try:
            # In Twilio, call transfer is typically done via TwiML <Dial> or <Conference>
            # For programmatic transfer, we update the call with new TwiML
            call = self.client.calls(call_id).update(
                twiml=f'<Response><Dial>{transfer_destination}</Dial></Response>'
            )
            return True
        except Exception as e:
            print(f"Twilio call transfer failed: {str(e)}")
            return False
            
    def end_call(self, call_id: str) -> bool:
        """End or hang up an active call."""
        try:
            # Twilio REST API to terminate a call
            self.client.calls(call_id).update(status='completed')
            return True
        except Exception as e:
            print(f"Twilio end call failed: {str(e)}")
            return False
            
    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Retrieve the current status of a call session."""
        try:
            call = self.client.calls(call_id).fetch()
            return {
                'id': call.sid,
                'status': call.status,
                'direction': call.direction,
                'duration': call.duration if call.duration else 0
            }
        except Exception as e:
            print(f"Twilio get call status failed: {str(e)}")
            return {}
            
    def send_sms(self, destination_phone: str, message: str) -> bool:
        """Send an SMS message to a phone number."""
        try:
            self.client.messages.create(
                body=message,
                from_=config.get('twilio_phone_number'),
                to=destination_phone
            )
            return True
        except Exception as e:
            print(f"Twilio SMS send failed: {str(e)}")
            return False