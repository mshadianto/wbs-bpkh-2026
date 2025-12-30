"""
WAHA (WhatsApp HTTP API) Integration
Handles WhatsApp messaging via WAHA server
"""

import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

import requests

from ..config import get_settings
from ..services import ReportService
from ..agents import ChatbotAgent

logger = logging.getLogger(__name__)


@dataclass
class WAHAMessage:
    """Incoming WhatsApp message"""
    chat_id: str
    message_id: str
    text: str
    from_number: str
    timestamp: int
    is_group: bool = False


class WAHAClient:
    """Client for WAHA API"""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.waha.api_url
        self.session = settings.waha.session_name
        self.api_key = settings.waha.api_key
        self.enabled = settings.waha.enabled

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    def send_text(self, chat_id: str, text: str) -> Dict[str, Any]:
        """
        Send text message.

        Args:
            chat_id: WhatsApp chat ID (e.g., 6281234567890@c.us)
            text: Message text

        Returns:
            API response dict
        """
        if not self.enabled:
            logger.warning("WAHA not enabled")
            return {'error': 'WAHA not enabled'}

        try:
            response = requests.post(
                f"{self.base_url}/api/sendText",
                headers=self._get_headers(),
                json={
                    'chatId': chat_id,
                    'text': text,
                    'session': self.session
                },
                timeout=30
            )

            if response.ok:
                return response.json()
            else:
                logger.error(f"WAHA send failed: {response.text}")
                return {'error': response.text}

        except Exception as e:
            logger.error(f"WAHA request error: {e}")
            return {'error': str(e)}

    def send_buttons(
        self,
        chat_id: str,
        text: str,
        buttons: list,
        footer: str = ""
    ) -> Dict[str, Any]:
        """
        Send message with buttons.

        Args:
            chat_id: WhatsApp chat ID
            text: Message text
            buttons: List of button dicts with 'id' and 'text'
            footer: Footer text

        Returns:
            API response dict
        """
        if not self.enabled:
            return {'error': 'WAHA not enabled'}

        try:
            response = requests.post(
                f"{self.base_url}/api/sendButtons",
                headers=self._get_headers(),
                json={
                    'chatId': chat_id,
                    'text': text,
                    'buttons': buttons,
                    'footer': footer,
                    'session': self.session
                },
                timeout=30
            )

            return response.json() if response.ok else {'error': response.text}

        except Exception as e:
            return {'error': str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Check WAHA session status"""
        try:
            response = requests.get(
                f"{self.base_url}/api/sessions/{self.session}",
                headers=self._get_headers(),
                timeout=10
            )
            return response.json() if response.ok else {'status': 'error'}
        except Exception:
            return {'status': 'unreachable'}

    def format_phone(self, phone: str) -> str:
        """Format phone number to WhatsApp chat ID"""
        # Remove non-digits
        digits = ''.join(filter(str.isdigit, phone))

        # Convert 08 to 628
        if digits.startswith('0'):
            digits = '62' + digits[1:]

        return f"{digits}@c.us"


class WAHAWebhookHandler:
    """Handler for WAHA webhook events"""

    def __init__(self):
        self.waha = WAHAClient()
        self.chatbot = ChatbotAgent()
        self.report_service = ReportService()

        # Session context for users
        self.user_sessions: Dict[str, Dict] = {}

    def handle_message(self, payload: Dict[str, Any]) -> None:
        """
        Handle incoming webhook message.

        Args:
            payload: Webhook payload from WAHA
        """
        try:
            # Parse message
            message = self._parse_message(payload)
            if not message:
                return

            # Skip group messages
            if message.is_group:
                return

            # Get or create session
            session = self._get_session(message.from_number)

            # Process with chatbot
            response = self._process_message(message, session)

            # Send response
            if response:
                self.waha.send_text(message.chat_id, response)

        except Exception as e:
            logger.error(f"Webhook handler error: {e}")

    def _parse_message(self, payload: Dict[str, Any]) -> Optional[WAHAMessage]:
        """Parse webhook payload to WAHAMessage"""
        try:
            event = payload.get('event')

            # Only handle message events
            if event != 'message':
                return None

            data = payload.get('payload', {})

            # Skip non-text messages
            if not data.get('body'):
                return None

            return WAHAMessage(
                chat_id=data.get('from', ''),
                message_id=data.get('id', ''),
                text=data.get('body', ''),
                from_number=data.get('from', '').replace('@c.us', ''),
                timestamp=data.get('timestamp', 0),
                is_group='@g.us' in data.get('from', '')
            )

        except Exception:
            return None

    def _get_session(self, phone: str) -> Dict[str, Any]:
        """Get or create user session"""
        if phone not in self.user_sessions:
            self.user_sessions[phone] = {
                'step': 'greeting',
                'context': {},
                'report_data': {}
            }
        return self.user_sessions[phone]

    def _process_message(
        self,
        message: WAHAMessage,
        session: Dict[str, Any]
    ) -> str:
        """Process message and generate response"""

        text = message.text.strip().lower()

        # Check for commands
        if text in ['menu', 'start', '/start']:
            session['step'] = 'greeting'
            return self._get_menu()

        if text in ['lapor', 'report', '1']:
            session['step'] = 'report_what'
            session['report_data'] = {}
            return "📝 *Buat Laporan Baru*\n\nApa kejadian yang ingin Anda laporkan? Jelaskan secara detail."

        if text in ['status', 'cek', '2']:
            session['step'] = 'check_status'
            return "🔍 *Cek Status Laporan*\n\nMasukkan Report ID Anda (contoh: WBS-2025-000001):"

        if text in ['info', 'bantuan', '3']:
            return self._get_info()

        # Handle report flow
        if session['step'].startswith('report_'):
            return self._handle_report_step(message.text, session)

        # Handle status check
        if session['step'] == 'check_status':
            return self._handle_status_check(message.text, session)

        # Default: use chatbot
        result = self.chatbot.process({
            'message': message.text,
            'session_id': message.from_number
        })

        return result.data.get('response', self._get_menu())

    def _get_menu(self) -> str:
        """Get main menu"""
        return """🕌 *Assalamu'alaikum*

Selamat datang di *WBS BPKH*
Whistleblowing System

Pilih layanan:
1️⃣ Buat Laporan Baru
2️⃣ Cek Status Laporan
3️⃣ Informasi WBS

Ketik angka atau nama layanan."""

    def _get_info(self) -> str:
        """Get WBS information"""
        return """ℹ️ *Informasi WBS BPKH*

*Apa itu WBS?*
Sistem pelaporan pelanggaran yang aman dan rahasia.

*Apa yang bisa dilaporkan?*
• Korupsi & Penipuan
• Penyalahgunaan wewenang
• Konflik kepentingan
• Pelanggaran kebijakan
• Dan lainnya

*Kerahasiaan*
Identitas pelapor dilindungi sesuai PP 71/2000.

Ketik *menu* untuk kembali."""

    def _handle_report_step(self, text: str, session: Dict) -> str:
        """Handle report creation flow"""
        step = session['step']
        report_data = session['report_data']

        steps = {
            'report_what': ('what', 'report_where', '📍 Dimana kejadian tersebut terjadi?'),
            'report_where': ('where', 'report_when', '🕐 Kapan kejadian tersebut terjadi?'),
            'report_when': ('when', 'report_who', '👤 Siapa yang terlibat dalam kejadian tersebut?'),
            'report_who': ('who', 'report_how', '🔍 Bagaimana kronologi/cara kejadian dilakukan?'),
            'report_how': ('how', 'report_confirm', None)
        }

        if step in steps:
            field, next_step, next_prompt = steps[step]
            report_data[field] = text
            session['step'] = next_step

            if next_prompt:
                return next_prompt
            else:
                # Show summary
                return self._get_report_summary(report_data)

        if step == 'report_confirm':
            if text.lower() in ['ya', 'yes', 'benar', 'kirim']:
                # Submit report
                return self._submit_report(report_data, session)
            else:
                session['step'] = 'report_what'
                session['report_data'] = {}
                return "Baik, mari mulai dari awal.\n\nApa kejadian yang ingin Anda laporkan?"

        return self._get_menu()

    def _get_report_summary(self, data: Dict) -> str:
        """Get report summary for confirmation"""
        return f"""📋 *Ringkasan Laporan*

*Kejadian:* {data.get('what', '')[:100]}...
*Lokasi:* {data.get('where', '')}
*Waktu:* {data.get('when', '')}
*Pihak Terlibat:* {data.get('who', '')}
*Kronologi:* {data.get('how', '')[:100]}...

Ketik *ya* untuk mengirim atau *tidak* untuk mengulang."""

    def _submit_report(self, data: Dict, session: Dict) -> str:
        """Submit report and return confirmation"""
        try:
            from ..models import ReportCreate

            report_data = ReportCreate(
                what=data['what'],
                where=data['where'],
                when=data['when'],
                who=data['who'],
                how=data['how'],
                source_channel='whatsapp'
            )

            result = self.report_service.submit_report(report_data)

            if result.success:
                session['step'] = 'greeting'
                session['report_data'] = {}

                return f"""✅ *Laporan Berhasil Disubmit*

📋 *Report ID:* {result.report_id}
🔐 *PIN:* {result.pin}

⚠️ *PENTING:* Simpan Report ID dan PIN Anda.
Gunakan untuk cek status laporan.

Ketik *menu* untuk kembali."""

            else:
                return f"❌ Gagal submit: {result.error}\n\nKetik *menu* untuk kembali."

        except Exception as e:
            return f"❌ Error: {str(e)}\n\nKetik *menu* untuk kembali."

    def _handle_status_check(self, report_id: str, session: Dict) -> str:
        """Handle status check flow"""
        report = self.report_service.get_report(report_id.upper())

        session['step'] = 'greeting'

        if report:
            from ..config import ReportStatus
            status_name = ReportStatus.get_display_name(report.status)

            return f"""📋 *Status Laporan*

*Report ID:* {report.report_id}
*Status:* {status_name}
*Kategori:* {report.category or 'Dalam proses'}
*Tanggal Lapor:* {report.created_at.strftime('%d %b %Y') if report.created_at else 'N/A'}

Ketik *menu* untuk kembali."""

        return "❌ Report ID tidak ditemukan.\n\nKetik *menu* untuk kembali."
