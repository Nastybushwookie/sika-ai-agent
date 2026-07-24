"""
RingCentral Telephony Provider Implementation
Implements the TelephonyProvider interface for RingCentral API integration.
"""
import json
from typing import Dict, Any
from ringcentral import SDK as RingCentralSDK
from .interface import TelephonyProvider


class RingCentralProvider(TelephonyProvider):
    """RingCentral telephony provider implementation."""
    
    def __init__(self):
        self.sdk = None
        self.platform = None
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the RingCentral SDK with credentials."""
        try:
            self.sdk = RingCentralSDK(
                client_id=config.get('ringcentral_client_id'),
                client_secret=config.get('ringcentral_client_secret'),
                server_url=config.get('ringcentral_server', 'https://platform.ringcentral.com')
            )
            self.platform = self.sdk.platform()
            
            # Perform login to get access token
            self.platform.login(
                username=config.get('ringcentral_username'),
                extension=config.get('ringcentral_extension', '101'),
                password=config.get('ringcentral_password')
            )
            return True
        except Exception as e:
            print(f"RingCentral initialization failed: {str(e)}")
            return False
            
    def receive_inbound_call(self, phone_number: str) -> str:
        """
        Handle inbound call routing.
        Returns the webhook URL for RingCentral to route the call to the AI agent.
        """
        # In a real implementation, this would configure RingCentral's call routing
        # or return the webhook URL that RingCentral should POST to when a call is received
        webhook_url = f"{config.get('webhook_base_url', 'https://api.yourcompany.com')}/vapi/webhook"
        return webhook_url
        
    def initiate_outbound_call(self, destination_phone: str, webhook_url: str) -> str:
        """Initiate an outbound call to a destination phone number."""
        try:
            # RingCentral REST API call for making outbound calls
            response = self.platform.post('/restapi/v1.0/account/~/extension/~/call', {
                'from': {'phoneNumber': config.get('ringcentral_phone_number')},
                'to': {'phoneNumber': destination_phone},
                'callMode': 'talk',
                'webhook': {'eventFilters': [
                    'callStatusChanged(ringing,started,completed)',
                    'sessionCreated'
                ], 'payloadTemplate': json.dumps({
                    'sessionId': '${message.sessionId}',
                    'status': '${message.callStatus}'
                })}
            })
            
            call_info = response.json()
            return call_info['id']  # Return the call session ID
        except Exception as e:
            print(f"RingCentral outbound call failed: {str(e)}")
            raise
            
    def transfer_call(self, call_id: str, transfer_destination: str) -> bool:
        """Transfer an active call to another number or live agent (warm transfer)."""
        try:
            # RingCentral REST API for call transfer
            response = self.platform.post(f'/restapi/v1.0/account/~/extension/~/call/{call_id}/transfer', {
                'destination': {'phoneNumber': transfer_destination}
            })
            return response.status_code == 200 or response.status_code == 201
        except Exception as e:
            print(f"RingCentral call transfer failed: {str(e)}")
            return False
            
    def end_call(self, call_id: str) -> bool:
        """End or hang up an active call."""
        try:
            # RingCentral REST API to terminate a call
            response = self.platform.post(f'/restapi/v1.0/account/~/extension/~/call/{call_id}/terminate')
            return response.status_code == 200 or response.status_code == 204
        except Exception as e:
            print(f"RingCentral end call failed: {str(e)}")
            return False
            
    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Retrieve the current status of a call session."""
        try:
            response = self.platform.get(f'/restapi/v1.0/account/~/extension/~/call/{call_id}')
            call_info = response.json()
            return {
                'id': call_info.get('id'),
                'status': call_info.get('status', {}).get('presenceStatus'),
                'direction': call_info.get('direction'),
                'duration': call_info.get('duration')
            }
        except Exception as e:
            print(f"RingCentral get call status failed: {str(e)}")
            return {}
            
    def send_sms(self, destination_phone: str, message: str) -> bool:
        """Send an SMS message to a phone number."""
        try:
            response = self.platform.post('/restapi/v1.0/account/~/extension/~/sms', {
                'from': {'phoneNumber': config.get('ringcentral_phone_number')},
                'to': [{'phoneNumber': destination_phone}],
                'text': message
            })
            return response.status_code == 201
        except Exception as e:
            print(f"RingCentral SMS send failed: {str(e)}")
            return False