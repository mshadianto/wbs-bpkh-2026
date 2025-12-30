"""
WAHA (WhatsApp HTTP API) Integration for WBS BPKH
Handles WhatsApp messaging via self-hosted WAHA
"""

import httpx
import json
from typing import Dict, Optional, List
from datetime import datetime

from config import WAHAConfig
from database import WBSDatabase
from chatbot_agent import ChatbotAgent


class WAHAClient:
    """Client for WAHA WhatsApp HTTP API"""

    def __init__(self, config: WAHAConfig = None):
        self.config = config or WAHAConfig()
        self.base_url = self.config.base_url.rstrip('/')
        self.session = self.config.session_name
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.config.api_key:
            self.headers["X-Api-Key"] = self.config.api_key

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to WAHA API"""
        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=30.0) as client:
                if method == "GET":
                    response = client.get(url, headers=self.headers)
                elif method == "POST":
                    response = client.post(url, headers=self.headers, json=data)
                elif method == "PUT":
                    response = client.put(url, headers=self.headers, json=data)
                else:
                    return {"error": f"Unsupported method: {method}"}

                if response.status_code in [200, 201]:
                    return response.json() if response.text else {"success": True}
                else:
                    return {"error": response.text, "status": response.status_code}

        except httpx.TimeoutException:
            return {"error": "Request timeout"}
        except httpx.RequestError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def check_health(self) -> Dict:
        """Check WAHA API health"""
        return self._make_request("GET", "/api/health")

    def get_sessions(self) -> Dict:
        """Get all sessions"""
        return self._make_request("GET", "/api/sessions")

    def start_session(self) -> Dict:
        """Start WhatsApp session"""
        return self._make_request("POST", f"/api/sessions/{self.session}/start")

    def stop_session(self) -> Dict:
        """Stop WhatsApp session"""
        return self._make_request("POST", f"/api/sessions/{self.session}/stop")

    def get_qr(self) -> Dict:
        """Get QR code for session authentication"""
        return self._make_request("GET", f"/api/{self.session}/auth/qr")

    def send_message(self, phone: str, message: str) -> Dict:
        """Send text message"""
        # Ensure phone number format
        phone = self._format_phone(phone)

        data = {
            "chatId": f"{phone}@c.us",
            "text": message
        }

        return self._make_request("POST", f"/api/sendText", data)

    def send_seen(self, phone: str) -> Dict:
        """Mark chat as seen"""
        phone = self._format_phone(phone)

        data = {
            "chatId": f"{phone}@c.us"
        }

        return self._make_request("POST", f"/api/sendSeen", data)

    def get_chats(self) -> Dict:
        """Get all chats"""
        return self._make_request("GET", f"/api/chats")

    def get_messages(self, phone: str, limit: int = 10) -> Dict:
        """Get messages from a chat"""
        phone = self._format_phone(phone)
        return self._make_request("GET", f"/api/chats/{phone}@c.us/messages?limit={limit}")

    def _format_phone(self, phone: str) -> str:
        """Format phone number for WhatsApp"""
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))

        # Handle Indonesian numbers
        if phone.startswith('0'):
            phone = '62' + phone[1:]
        elif phone.startswith('+62'):
            phone = phone[1:]
        elif not phone.startswith('62'):
            phone = '62' + phone

        return phone


class WAHAWebhookHandler:
    """Handle incoming WAHA webhooks"""

    def __init__(self, db: WBSDatabase, api_key: str):
        self.db = db
        self.waha_client = WAHAClient()
        self.chatbot = ChatbotAgent(api_key, db)

    def handle_webhook(self, payload: Dict) -> Dict:
        """Handle incoming webhook from WAHA"""
        event = payload.get("event")

        if event == "message":
            return self._handle_message(payload)
        elif event == "message.ack":
            return self._handle_ack(payload)
        elif event == "session.status":
            return self._handle_session_status(payload)
        else:
            return {"status": "ignored", "event": event}

    def _handle_message(self, payload: Dict) -> Dict:
        """Handle incoming message"""
        try:
            message_data = payload.get("payload", {})

            # Skip outgoing messages
            if message_data.get("fromMe", False):
                return {"status": "skipped", "reason": "outgoing message"}

            # Extract info
            chat_id = message_data.get("from", "")
            phone = chat_id.replace("@c.us", "").replace("@s.whatsapp.net", "")
            text = message_data.get("body", "")

            if not text:
                return {"status": "skipped", "reason": "no text"}

            # Get or create WA channel
            wa_channel = self.db.get_or_create_wa_channel(phone)

            # Get or create chatbot session
            session = self.db.get_session_by_phone(phone)
            if not session:
                session_id = self.chatbot.create_session('whatsapp', phone)
                self.db.update_wa_channel(phone, session_id=session_id, status='reporting')
            else:
                session_id = session['session_id']

            # Process message with chatbot
            result = self.chatbot.process_message(session_id, text)

            # Send response
            response_text = result.get("response", "Maaf, terjadi kesalahan. Silakan coba lagi.")
            send_result = self.waha_client.send_message(phone, response_text)

            # Update channel status based on chatbot state
            new_status = {
                "greeting": "idle",
                "report_intake": "reporting",
                "status_check": "tracking",
                "completed": "idle"
            }.get(result.get("state"), "idle")

            self.db.update_wa_channel(phone, status=new_status)

            # If report was created, link it
            if result.get("report_id"):
                self.db.update_wa_channel(phone, report_id=result["report_id"])

            return {
                "status": "processed",
                "phone": phone,
                "response_sent": send_result.get("success", False) or "id" in send_result
            }

        except Exception as e:
            print(f"[ERROR] Webhook handling error: {e}")
            return {"status": "error", "error": str(e)}

    def _handle_ack(self, payload: Dict) -> Dict:
        """Handle message acknowledgment"""
        # Can be used to track message delivery status
        return {"status": "ack_received"}

    def _handle_session_status(self, payload: Dict) -> Dict:
        """Handle session status change"""
        status = payload.get("payload", {}).get("status", "")
        return {"status": "session_status", "wa_status": status}

    def send_notification(self, phone: str, message: str) -> bool:
        """Send notification to a phone number"""
        result = self.waha_client.send_message(phone, message)
        return result.get("success", False) or "id" in result


def create_waha_webhook_response(success: bool = True, message: str = "OK") -> Dict:
    """Create standard webhook response"""
    return {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
