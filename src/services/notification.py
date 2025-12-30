"""
Notification Service
Handles email and WhatsApp notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple
from dataclasses import dataclass
import logging

import requests

from ..config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class NotificationResult:
    """Notification send result"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class NotificationService:
    """Service for sending notifications"""

    def __init__(self):
        self.settings = get_settings()

    # ==================== Email Notifications ====================

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> NotificationResult:
        """
        Send email notification.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body

        Returns:
            NotificationResult
        """
        if not self.settings.email.enabled:
            return NotificationResult(success=False, error="Email notifications disabled")

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings.email.from_email
            msg['To'] = to_email

            # Add plain text
            msg.attach(MIMEText(body, 'plain'))

            # Add HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            # Send
            with smtplib.SMTP(
                self.settings.email.smtp_host,
                self.settings.email.smtp_port
            ) as server:
                server.starttls()
                server.login(
                    self.settings.email.smtp_user,
                    self.settings.email.smtp_password
                )
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}")
            return NotificationResult(success=True)

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return NotificationResult(success=False, error=str(e))

    def send_report_confirmation(
        self,
        to_email: str,
        report_id: str,
        pin: str
    ) -> NotificationResult:
        """Send report submission confirmation email"""
        subject = f"Konfirmasi Laporan WBS BPKH - {report_id}"

        body = f"""
Assalamu'alaikum Wr. Wb.

Terima kasih telah menyampaikan laporan melalui Whistleblowing System BPKH.

Laporan Anda telah berhasil disubmit dengan detail berikut:
- Report ID: {report_id}
- PIN Akses: {pin}

PENTING: Simpan Report ID dan PIN Anda dengan aman.
Informasi ini diperlukan untuk melacak status laporan.

Jangan bagikan PIN Anda kepada siapapun.

Wassalamu'alaikum Wr. Wb.

--
Whistleblowing System BPKH
{self.settings.contact.web_portal}
        """

        return self.send_email(to_email, subject, body)

    def send_status_update(
        self,
        to_email: str,
        report_id: str,
        new_status: str
    ) -> NotificationResult:
        """Send status update notification"""
        subject = f"Update Status Laporan - {report_id}"

        body = f"""
Assalamu'alaikum Wr. Wb.

Status laporan Anda ({report_id}) telah diperbarui.

Status Baru: {new_status}

Silakan login ke portal WBS untuk melihat detail lebih lanjut.

Wassalamu'alaikum Wr. Wb.

--
Whistleblowing System BPKH
        """

        return self.send_email(to_email, subject, body)

    # ==================== WhatsApp Notifications ====================

    def send_whatsapp(
        self,
        phone_number: str,
        message: str
    ) -> NotificationResult:
        """
        Send WhatsApp message via WAHA.

        Args:
            phone_number: Phone number with country code (e.g., 6281234567890)
            message: Message text

        Returns:
            NotificationResult
        """
        if not self.settings.waha.enabled:
            return NotificationResult(success=False, error="WhatsApp notifications disabled")

        try:
            url = f"{self.settings.waha.api_url}/api/sendText"
            headers = {'Content-Type': 'application/json'}

            if self.settings.waha.api_key:
                headers['Authorization'] = f'Bearer {self.settings.waha.api_key}'

            payload = {
                'chatId': f'{phone_number}@c.us',
                'text': message,
                'session': self.settings.waha.session_name
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.ok:
                result = response.json()
                return NotificationResult(
                    success=True,
                    message_id=result.get('id')
                )
            else:
                return NotificationResult(
                    success=False,
                    error=f"WAHA error: {response.text}"
                )

        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return NotificationResult(success=False, error=str(e))

    def send_whatsapp_confirmation(
        self,
        phone_number: str,
        report_id: str,
        pin: str
    ) -> NotificationResult:
        """Send report confirmation via WhatsApp"""
        message = f"""
🕌 *WBS BPKH - Konfirmasi Laporan*

Assalamu'alaikum Wr. Wb.

Laporan Anda telah berhasil disubmit.

📋 *Report ID:* {report_id}
🔐 *PIN Akses:* {pin}

⚠️ *PENTING:* Simpan informasi ini dengan aman.

Gunakan Report ID dan PIN untuk melacak status laporan Anda di portal WBS.

Wassalamu'alaikum Wr. Wb.
        """

        return self.send_whatsapp(phone_number, message)

    # ==================== Combined Notifications ====================

    def notify_report_submitted(
        self,
        report_id: str,
        pin: str,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> dict:
        """
        Send report confirmation via all available channels.

        Returns:
            Dict with results for each channel
        """
        results = {}

        if email:
            results['email'] = self.send_report_confirmation(email, report_id, pin)

        if phone:
            results['whatsapp'] = self.send_whatsapp_confirmation(phone, report_id, pin)

        return results

    def notify_status_change(
        self,
        report_id: str,
        new_status: str,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> dict:
        """Send status change notification via all channels"""
        results = {}

        if email:
            results['email'] = self.send_status_update(email, report_id, new_status)

        if phone:
            message = f"🔔 Status laporan {report_id} telah diperbarui menjadi: {new_status}"
            results['whatsapp'] = self.send_whatsapp(phone, message)

        return results
