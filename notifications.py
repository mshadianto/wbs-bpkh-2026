"""
Notification Service for WBS BPKH
Handles email and WhatsApp notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, List
from datetime import datetime

from config import EmailConfig, WAHAConfig, NOTIFICATION_TEMPLATES
from waha_integration import WAHAClient


class EmailNotifier:
    """Send email notifications"""

    def __init__(self, config: EmailConfig = None):
        self.config = config or EmailConfig()
        self.enabled = self.config.smtp_host and self.config.smtp_user

    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email notification"""
        if not self.enabled:
            print("[WARN] Email not configured, skipping notification")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.config.sender_email
            msg["To"] = to_email

            # Add plain text
            msg.attach(MIMEText(body, "plain"))

            # Add HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            # Connect and send
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.sendmail(self.config.sender_email, to_email, msg.as_string())

            print(f"[OK] Email sent to {to_email}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False

    def send_report_created(self, to_email: str, report_id: str, pin: str) -> bool:
        """Send notification for new report"""
        template = NOTIFICATION_TEMPLATES.get("report_created", {})
        subject = template.get("subject", "Laporan WBS Berhasil Dibuat").format(report_id=report_id)
        body = template.get("body", "Laporan {report_id} telah dibuat. PIN: {pin}").format(
            report_id=report_id, pin=pin
        )

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <h2 style="color: #667eea;">WBS BPKH - Laporan Berhasil Dibuat</h2>
                <p>Terima kasih telah melaporkan. Berikut informasi akses laporan Anda:</p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Report ID:</strong> <span style="color: #667eea; font-size: 1.2em;">{report_id}</span></p>
                    <p><strong>PIN:</strong> <span style="color: #667eea; font-size: 1.2em;">{pin}</span></p>
                </div>
                <p style="color: #666;">Simpan informasi ini untuk melacak status laporan Anda.</p>
                <p style="color: #888; font-size: 0.9em;">Email ini dikirim otomatis, mohon tidak membalas.</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body, html_body)

    def send_status_update(self, to_email: str, report_id: str, old_status: str, new_status: str) -> bool:
        """Send notification for status change"""
        template = NOTIFICATION_TEMPLATES.get("status_update", {})
        subject = template.get("subject", "Update Status Laporan {report_id}").format(report_id=report_id)
        body = template.get("body", "Status laporan berubah: {old_status} -> {new_status}").format(
            report_id=report_id, old_status=old_status, new_status=new_status
        )

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <h2 style="color: #667eea;">WBS BPKH - Update Status Laporan</h2>
                <p>Status laporan Anda telah diperbarui:</p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Report ID:</strong> {report_id}</p>
                    <p><strong>Status Sebelumnya:</strong> {old_status}</p>
                    <p><strong>Status Baru:</strong> <span style="color: #28a745; font-weight: bold;">{new_status}</span></p>
                </div>
                <p style="color: #666;">Login ke portal WBS untuk melihat detail lebih lanjut.</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body, html_body)

    def send_new_message(self, to_email: str, report_id: str, sender: str) -> bool:
        """Send notification for new message"""
        template = NOTIFICATION_TEMPLATES.get("new_message", {})
        subject = template.get("subject", "Pesan Baru untuk Laporan {report_id}").format(report_id=report_id)
        body = template.get("body", "Anda menerima pesan baru dari {sender}").format(
            report_id=report_id, sender=sender
        )

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <h2 style="color: #667eea;">WBS BPKH - Pesan Baru</h2>
                <p>Anda menerima pesan baru terkait laporan Anda:</p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Report ID:</strong> {report_id}</p>
                    <p><strong>Pengirim:</strong> {sender}</p>
                </div>
                <p style="color: #666;">Login ke portal WBS untuk membaca dan membalas pesan.</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body, html_body)


class WhatsAppNotifier:
    """Send WhatsApp notifications via WAHA"""

    def __init__(self, config: WAHAConfig = None):
        self.config = config or WAHAConfig()
        self.client = WAHAClient(self.config)
        self.enabled = bool(self.config.base_url)

    def send_message(self, phone: str, message: str) -> bool:
        """Send WhatsApp message"""
        if not self.enabled:
            print("[WARN] WhatsApp not configured, skipping notification")
            return False

        result = self.client.send_message(phone, message)
        success = result.get("success", False) or "id" in result

        if success:
            print(f"[OK] WhatsApp sent to {phone}")
        else:
            print(f"[ERROR] WhatsApp failed: {result.get('error', 'Unknown error')}")

        return success

    def send_report_created(self, phone: str, report_id: str, pin: str) -> bool:
        """Send notification for new report"""
        message = f"""*WBS BPKH - Laporan Berhasil*

Terima kasih telah melaporkan.

*SIMPAN INFORMASI INI:*
Report ID: *{report_id}*
PIN: *{pin}*

Gunakan Report ID dan PIN untuk melacak status laporan di portal WBS.

_Pesan otomatis, tidak perlu dibalas._"""

        return self.send_message(phone, message)

    def send_status_update(self, phone: str, report_id: str, old_status: str, new_status: str) -> bool:
        """Send notification for status change"""
        message = f"""*WBS BPKH - Update Status*

Laporan *{report_id}* telah diupdate.

Status: {old_status} -> *{new_status}*

Akses portal WBS untuk detail lebih lanjut."""

        return self.send_message(phone, message)

    def send_new_message(self, phone: str, report_id: str, sender: str) -> bool:
        """Send notification for new message"""
        message = f"""*WBS BPKH - Pesan Baru*

Anda menerima pesan baru untuk laporan *{report_id}* dari *{sender}*.

Login ke portal WBS untuk membaca dan membalas."""

        return self.send_message(phone, message)


class NotificationService:
    """Unified notification service"""

    def __init__(self, db=None):
        self.db = db
        self.email = EmailNotifier()
        self.whatsapp = WhatsAppNotifier()

    def notify_report_created(self, report_id: str, pin: str, email: str = None, phone: str = None) -> Dict:
        """Send notifications for new report"""
        results = {"email": False, "whatsapp": False}

        if email:
            results["email"] = self.email.send_report_created(email, report_id, pin)

        if phone:
            results["whatsapp"] = self.whatsapp.send_report_created(phone, report_id, pin)

        # Log notification
        if self.db:
            self._log_notification(report_id, "report_created", results)

        return results

    def notify_status_update(self, report_id: str, old_status: str, new_status: str,
                             email: str = None, phone: str = None) -> Dict:
        """Send notifications for status change"""
        results = {"email": False, "whatsapp": False}

        if email:
            results["email"] = self.email.send_status_update(email, report_id, old_status, new_status)

        if phone:
            results["whatsapp"] = self.whatsapp.send_status_update(phone, report_id, old_status, new_status)

        # Log notification
        if self.db:
            self._log_notification(report_id, "status_update", results)

        return results

    def notify_new_message(self, report_id: str, sender: str,
                           email: str = None, phone: str = None) -> Dict:
        """Send notifications for new message"""
        results = {"email": False, "whatsapp": False}

        if email:
            results["email"] = self.email.send_new_message(email, report_id, sender)

        if phone:
            results["whatsapp"] = self.whatsapp.send_new_message(phone, report_id, sender)

        # Log notification
        if self.db:
            self._log_notification(report_id, "new_message", results)

        return results

    def _log_notification(self, report_id: str, notification_type: str, results: Dict):
        """Log notification to database"""
        if self.db:
            try:
                self.db.log_notification(
                    report_id=report_id,
                    notification_type=notification_type,
                    channels=results,
                    timestamp=datetime.now().isoformat()
                )
            except Exception as e:
                print(f"[WARN] Failed to log notification: {e}")

    def get_contact_for_report(self, report_id: str) -> Dict:
        """Get contact info for a report"""
        if not self.db:
            return {}

        try:
            access = self.db.get_report_access(report_id)
            if access:
                return {
                    "email": access.get("email"),
                    "phone": access.get("phone")
                }
        except Exception as e:
            print(f"[ERROR] Failed to get contact: {e}")

        return {}


# Convenience functions
def send_report_notification(report_id: str, pin: str, email: str = None, phone: str = None) -> Dict:
    """Send report created notification"""
    service = NotificationService()
    return service.notify_report_created(report_id, pin, email, phone)


def send_status_notification(report_id: str, old_status: str, new_status: str,
                            email: str = None, phone: str = None) -> Dict:
    """Send status update notification"""
    service = NotificationService()
    return service.notify_status_update(report_id, old_status, new_status, email, phone)


def send_message_notification(report_id: str, sender: str,
                             email: str = None, phone: str = None) -> Dict:
    """Send new message notification"""
    service = NotificationService()
    return service.notify_new_message(report_id, sender, email, phone)
