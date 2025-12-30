"""
AI Chatbot Agent for WBS BPKH
Handles natural language Q&A and guided report submission
"""

import json
import re
from datetime import datetime
from typing import Dict, Optional, List

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from config import AGENT_PROMPTS, VIOLATION_TYPES
from knowledge_base import knowledge_base
from database import WBSDatabase


class ChatbotAgent:
    """AI Chatbot for natural language interactions"""

    def __init__(self, api_key: str, db: WBSDatabase):
        self.api_key = api_key
        self.db = db
        self.client = Groq(api_key=api_key) if GROQ_AVAILABLE and api_key else None
        self.system_prompt = AGENT_PROMPTS.get("chatbot", "")

        # Fields needed for report
        self.report_fields = [
            ("title", "Judul laporan (apa yang terjadi secara singkat)"),
            ("description", "Deskripsi detail kejadian"),
            ("reported_person", "Nama atau jabatan orang yang dilaporkan"),
            ("incident_date", "Kapan kejadian terjadi"),
            ("location", "Di mana lokasi kejadian"),
            ("evidence", "Bukti atau saksi yang ada")
        ]

    def process_message(self, session_id: str, user_message: str) -> Dict:
        """Process incoming message and generate response"""
        # Get or create session
        session = self.db.get_chatbot_session(session_id)
        if not session:
            session = {
                "session_id": session_id,
                "state": "greeting",
                "context": {},
                "report_draft": {}
            }

        state = session.get("state", "greeting")
        context = session.get("context", {})
        report_draft = session.get("report_draft", {})

        # Detect intent if in greeting state
        if state == "greeting":
            intent = self._detect_intent(user_message)
            if intent == "report_intake":
                state = "report_intake"
                context["current_field"] = 0
                response = self._get_greeting_response("report")
            elif intent == "status_check":
                state = "status_check"
                context["awaiting"] = "report_id"
                response = "Tentu, saya bisa membantu mengecek status laporan Anda.\n\nMohon masukkan Report ID Anda (format: WBS-2025-XXXXXX):"
            elif intent == "inquiry":
                # Answer using knowledge base
                response = self._answer_inquiry(user_message)
                # Stay in greeting state
            else:
                response = self._get_greeting_response("welcome")

        elif state == "report_intake":
            result = self._handle_report_intake(user_message, context, report_draft)
            response = result["response"]
            context = result.get("context", context)
            report_draft = result.get("report_draft", report_draft)

            if result.get("complete"):
                state = "completed"
            elif result.get("cancelled"):
                state = "greeting"
                context = {}
                report_draft = {}

        elif state == "status_check":
            result = self._handle_status_check(user_message, context)
            response = result["response"]
            context = result.get("context", context)

            if result.get("complete"):
                state = "greeting"
                context = {}

        elif state == "inquiry":
            response = self._answer_inquiry(user_message)
            state = "greeting"

        else:
            response = self._get_greeting_response("welcome")
            state = "greeting"

        # Update session
        self.db.update_chatbot_session(
            session_id,
            state=state,
            context=context,
            report_draft=report_draft
        )

        return {
            "response": response,
            "state": state,
            "report_draft": report_draft if state == "report_intake" else None
        }

    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()

        # Report keywords
        report_keywords = ["lapor", "melaporkan", "pengaduan", "aduan", "report",
                         "laporkan", "ingin melapor", "mau lapor"]
        if any(kw in message_lower for kw in report_keywords):
            return "report_intake"

        # Status check keywords
        status_keywords = ["status", "cek", "tracking", "lacak", "progress",
                          "sudah sampai mana", "bagaimana laporan"]
        if any(kw in message_lower for kw in status_keywords):
            return "status_check"

        # Inquiry keywords
        inquiry_keywords = ["apa itu", "bagaimana", "jelaskan", "apa saja",
                           "caranya", "prosedur", "apa yang dimaksud"]
        if any(kw in message_lower for kw in inquiry_keywords):
            return "inquiry"

        # Greeting
        greeting_keywords = ["halo", "hai", "hi", "hello", "selamat", "pagi", "siang", "sore", "malam"]
        if any(kw in message_lower for kw in greeting_keywords):
            return "greeting"

        return "inquiry"

    def _get_greeting_response(self, type: str) -> str:
        """Get greeting response"""
        if type == "welcome":
            return """Selamat datang di WBS BPKH! Saya adalah asisten AI yang siap membantu Anda.

Saya dapat membantu Anda untuk:
1. **Membuat laporan** whistleblowing baru
2. **Mengecek status** laporan yang sudah ada
3. **Menjawab pertanyaan** tentang prosedur pelaporan

Silakan ketik apa yang ingin Anda lakukan, atau langsung sampaikan pertanyaan Anda."""

        elif type == "report":
            return """Baik, saya akan membantu Anda membuat laporan whistleblowing.

Laporan Anda akan dijamin kerahasiaannya sesuai PP 71/2000. Setelah selesai, Anda akan mendapatkan Report ID dan PIN untuk tracking.

Mari kita mulai. **Apa judul atau ringkasan singkat dari kejadian yang ingin Anda laporkan?**"""

    def _handle_report_intake(self, message: str, context: Dict, draft: Dict) -> Dict:
        """Handle report intake conversation"""
        current_field_idx = context.get("current_field", 0)

        # Check for cancel
        if message.lower() in ["batal", "cancel", "stop"]:
            return {
                "response": "Baik, proses pelaporan dibatalkan. Ketik 'lapor' jika ingin memulai lagi.",
                "cancelled": True
            }

        # Get current field
        if current_field_idx < len(self.report_fields):
            field_name, field_prompt = self.report_fields[current_field_idx]

            # Save the user's answer
            draft[field_name] = message

            # Move to next field
            current_field_idx += 1
            context["current_field"] = current_field_idx

            if current_field_idx < len(self.report_fields):
                # Ask for next field
                next_field_name, next_field_prompt = self.report_fields[current_field_idx]

                progress = f"[{current_field_idx}/{len(self.report_fields)}]"
                response = f"{progress} Terima kasih. Selanjutnya, **{next_field_prompt}**:"

                return {
                    "response": response,
                    "context": context,
                    "report_draft": draft
                }
            else:
                # All fields collected, confirm and submit
                return self._confirm_and_submit(draft)

        return {
            "response": "Maaf, terjadi kesalahan. Silakan ketik 'lapor' untuk memulai lagi.",
            "cancelled": True
        }

    def _confirm_and_submit(self, draft: Dict) -> Dict:
        """Confirm and submit the report"""
        # Generate report ID
        report_id = self.db.generate_report_id()

        # Prepare report data
        report_data = {
            "title": draft.get("title", ""),
            "description": draft.get("description", ""),
            "reported_person": draft.get("reported_person", ""),
            "incident_date": draft.get("incident_date", str(datetime.now().date())),
            "location": draft.get("location", ""),
            "evidence": draft.get("evidence", ""),
            "reporter_name": "Anonim (via Chatbot)",
            "reporter_contact": "Chatbot"
        }

        # Simple classification (rule-based for chatbot)
        classification = self._simple_classify(report_data)

        # Create minimal processing result
        processing_result = {
            "report_id": report_id,
            "intake": {"completeness_score": 80},
            "classification": classification,
            "routing": {
                "assigned_unit": self._determine_unit(classification["violation_type"]),
                "sla_hours": classification.get("sla_hours", 48)
            },
            "investigation": {
                "investigation_plan": "Standard investigation",
                "evidence_needed": ["Dokumen terkait"],
                "witnesses": ["Pelapor"]
            },
            "compliance": {"compliance_score": 85},
            "total_processing_time": 0
        }

        # Save to database
        success = self.db.insert_report(report_data, processing_result)

        if success:
            # Generate PIN
            pin = self.db.create_report_access(report_id)

            response = f"""Laporan Anda berhasil dikirim!

**SIMPAN INFORMASI INI:**
- Report ID: **{report_id}**
- PIN: **{pin}**

Gunakan Report ID dan PIN untuk melacak status laporan Anda.

**Ringkasan:**
- Jenis: {classification['violation_type']}
- Severity: {classification['severity']}
- Unit: {processing_result['routing']['assigned_unit']}

Terima kasih telah melaporkan. Laporan Anda akan segera ditindaklanjuti."""

            return {
                "response": response,
                "complete": True,
                "report_id": report_id,
                "pin": pin
            }
        else:
            return {
                "response": "Maaf, terjadi kesalahan saat menyimpan laporan. Silakan coba lagi atau gunakan portal web.",
                "cancelled": True
            }

    def _simple_classify(self, report_data: Dict) -> Dict:
        """Simple rule-based classification"""
        text = (report_data.get("title", "") + " " + report_data.get("description", "")).lower()

        # Match keywords
        for vtype, vdata in VIOLATION_TYPES.items():
            keywords = vdata.get("keywords", [])
            if any(kw.lower() in text for kw in keywords):
                return {
                    "violation_type": vtype,
                    "violation_code": vdata["code"],
                    "severity": vdata["severity"],
                    "sla_hours": {"Critical": 4, "High": 24, "Medium": 48, "Low": 72}.get(vdata["severity"], 48)
                }

        # Default
        return {
            "violation_type": "Tindakan Curang",
            "violation_code": "V009",
            "severity": "Low",
            "sla_hours": 72
        }

    def _determine_unit(self, violation_type: str) -> str:
        """Determine handling unit"""
        from config import ROUTING_UNITS
        for unit, types in ROUTING_UNITS.items():
            if violation_type in types:
                return unit
        return "Satuan Pengawasan Internal (SPI)"

    def _handle_status_check(self, message: str, context: Dict) -> Dict:
        """Handle status check conversation"""
        awaiting = context.get("awaiting", "report_id")

        if awaiting == "report_id":
            # Extract report ID
            report_id = message.strip().upper()
            if not report_id.startswith("WBS-"):
                return {
                    "response": "Format Report ID tidak valid. Mohon masukkan dengan format: WBS-2025-XXXXXX",
                    "context": context
                }

            context["report_id"] = report_id
            context["awaiting"] = "pin"

            return {
                "response": f"Report ID: {report_id}\n\nSekarang, mohon masukkan PIN 6 digit Anda:",
                "context": context
            }

        elif awaiting == "pin":
            pin = message.strip()
            report_id = context.get("report_id")

            if len(pin) != 6 or not pin.isdigit():
                return {
                    "response": "PIN harus 6 digit angka. Silakan coba lagi:",
                    "context": context
                }

            # Validate access
            if self.db.validate_report_access(report_id, pin):
                report = self.db.get_report_for_reporter(report_id)
                if report:
                    response = f"""**Status Laporan {report_id}**

- Status: **{report.get('status', 'N/A')}**
- Severity: {report.get('severity', 'N/A')}
- Unit Penanganan: {report.get('assigned_unit', 'N/A')}
- Tanggal Lapor: {report.get('created_at', 'N/A')[:10]}
- Update Terakhir: {report.get('updated_at', 'N/A')[:10]}

Untuk detail lebih lanjut atau berkomunikasi dengan pengelola, silakan akses portal web WBS.

Ada yang bisa saya bantu lagi?"""
                else:
                    response = "Laporan ditemukan tapi terjadi kesalahan saat mengambil data."
            else:
                response = "Report ID atau PIN tidak valid. Silakan periksa kembali."

            return {
                "response": response,
                "complete": True
            }

        return {
            "response": "Mohon masukkan Report ID Anda:",
            "context": {"awaiting": "report_id"}
        }

    def _answer_inquiry(self, question: str) -> str:
        """Answer inquiry using knowledge base and/or LLM"""
        # Search knowledge base
        kb_results = knowledge_base.search(question, top_k=3)

        if kb_results:
            # Build context from KB
            context_parts = []
            for result in kb_results:
                context_parts.append(result["content"])

            kb_context = "\n\n".join(context_parts)

            # Use LLM if available
            if self.client:
                try:
                    response = self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": f"""Anda adalah asisten WBS BPKH.
Jawab pertanyaan user berdasarkan konteks berikut:

{kb_context}

Berikan jawaban yang informatif, ringkas, dan ramah. Jika informasi tidak ada di konteks,
katakan bahwa Anda akan mengarahkan ke tim support."""},
                            {"role": "user", "content": question}
                        ],
                        temperature=0.3,
                        max_tokens=500
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    print(f"[ERROR] LLM error: {e}")

            # Fallback: return KB content directly
            return f"""Berdasarkan database pengetahuan kami:

{kb_results[0]['content'][:500]}...

Untuk informasi lebih lanjut, silakan hubungi tim WBS melalui email atau WhatsApp."""

        else:
            return """Maaf, saya tidak menemukan informasi spesifik untuk pertanyaan Anda.

Anda bisa mencoba:
1. Mengajukan pertanyaan dengan kata kunci yang berbeda
2. Menghubungi tim WBS di wbs@bpkh.go.id
3. WhatsApp: 085319000230 / 085319000140

Atau ketik 'lapor' untuk membuat laporan baru."""

    def create_session(self, channel: str = 'web', phone: str = None) -> str:
        """Create new chatbot session"""
        return self.db.create_chatbot_session(channel, phone)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.db.get_chatbot_session(session_id)

    def get_session_by_phone(self, phone: str) -> Optional[Dict]:
        """Get session by phone number"""
        return self.db.get_session_by_phone(phone)
