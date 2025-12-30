"""
Chatbot Agent
AI assistant for Q&A and guided reporting
"""

import time
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .base import BaseAgent, AgentResult


@dataclass
class ChatSession:
    """Chat session state"""
    session_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    current_step: str = "greeting"


class ChatbotAgent(BaseAgent):
    """Chatbot agent for user assistance"""

    # Knowledge base for Q&A
    FAQ = {
        'apa itu wbs': 'Whistleblowing System (WBS) adalah sistem pelaporan pelanggaran yang memungkinkan Anda melaporkan dugaan pelanggaran secara aman dan terjamin kerahasiaannya.',
        'bagaimana melapor': 'Untuk melapor, Anda perlu mengisi formulir 5W+1H: What (apa yang terjadi), Where (dimana), When (kapan), Who (siapa yang terlibat), dan How (bagaimana kejadiannya).',
        'apakah anonim': 'Ya, identitas pelapor dijaga kerahasiaannya. BPKH hanya fokus pada informasi yang Anda laporkan, bukan identitas Anda.',
        'berapa lama proses': 'Laporan akan ditindaklanjuti dalam 1-3 hari kerja untuk review awal. Investigasi penuh dapat memakan waktu hingga 45 hari kerja.',
        'apa yang bisa dilaporkan': 'Anda dapat melaporkan: korupsi, penipuan, penggelapan, penyalahgunaan wewenang, konflik kepentingan, pelecehan, diskriminasi, dan pelanggaran lainnya.',
        'cara cek status': 'Gunakan Report ID dan PIN yang diberikan saat submit laporan untuk mengecek status di Portal Pelapor.',
        'apa itu pin': 'PIN adalah kode 6 digit rahasia yang diberikan saat Anda submit laporan. PIN digunakan untuk mengakses dan melacak laporan Anda.',
        'apakah ada perlindungan': 'Ya, pelapor dilindungi sesuai PP 71/2000. Identitas Anda akan dirahasiakan dan Anda dilindungi dari pembalasan.',
        'siapa yang menangani': 'Laporan ditangani oleh tim khusus WBS BPKH yang terlatih dan independen.',
        'bukti apa yang diperlukan': 'Bukti dapat berupa dokumen, foto, rekaman, atau keterangan saksi. Semakin lengkap bukti, semakin mudah laporan ditindaklanjuti.'
    }

    # Guided reporting steps
    REPORT_STEPS = ['what', 'where', 'when', 'who', 'how', 'confirm']

    STEP_PROMPTS = {
        'what': 'Apa kejadian yang ingin Anda laporkan? Jelaskan secara detail.',
        'where': 'Dimana kejadian tersebut terjadi?',
        'when': 'Kapan kejadian tersebut terjadi? (tanggal/periode)',
        'who': 'Siapa saja yang terlibat dalam kejadian tersebut?',
        'how': 'Bagaimana kronologi atau cara kejadian tersebut dilakukan?',
        'confirm': 'Apakah informasi yang Anda berikan sudah benar? Ketik "ya" untuk submit atau "tidak" untuk mengulang.'
    }

    def __init__(self):
        super().__init__("ChatbotAgent")
        self.sessions: Dict[str, ChatSession] = {}

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Process chat message.

        Args:
            input_data: Dict with 'message', 'session_id', optional 'mode'

        Returns:
            AgentResult with response and context
        """
        start_time = time.time()

        message = str(input_data.get('message', '')).strip()
        session_id = input_data.get('session_id', 'default')
        mode = input_data.get('mode', 'chat')  # 'chat' or 'report'

        if not message:
            return self._create_result(False, error="Pesan tidak boleh kosong")

        # Get or create session
        session = self._get_session(session_id)

        # Detect intent
        intent = self._detect_intent(message)

        # Process based on mode and intent
        if mode == 'report':
            response = self._process_guided_report(session, message)
        elif intent == 'question':
            response = self._answer_question(message)
        elif intent == 'greeting':
            response = self._generate_greeting()
        elif intent == 'start_report':
            session.current_step = 'what'
            session.context = {}
            response = f"Baik, saya akan membantu Anda membuat laporan.\n\n{self.STEP_PROMPTS['what']}"
        else:
            response = self._generate_default_response()

        # Save message to session
        session.messages.append({'role': 'user', 'content': message})
        session.messages.append({'role': 'assistant', 'content': response})

        processing_time = (time.time() - start_time) * 1000

        return self._create_result(
            success=True,
            data={
                'response': response,
                'intent': intent,
                'session_id': session_id,
                'current_step': session.current_step,
                'context': session.context
            },
            processing_time_ms=processing_time
        )

    def _get_session(self, session_id: str) -> ChatSession:
        """Get or create chat session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(session_id=session_id)
        return self.sessions[session_id]

    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()

        # Greeting patterns
        if any(g in message_lower for g in ['halo', 'hai', 'hi', 'hello', 'assalam', 'selamat']):
            return 'greeting'

        # Question patterns
        if any(q in message_lower for q in ['apa', 'bagaimana', 'kapan', 'dimana', 'siapa', 'mengapa', 'apakah', '?']):
            return 'question'

        # Report intent
        if any(r in message_lower for r in ['lapor', 'laporkan', 'mau lapor', 'ingin melaporkan', 'buat laporan']):
            return 'start_report'

        # Status check
        if any(s in message_lower for s in ['status', 'lacak', 'cek laporan', 'wbs-']):
            return 'status_check'

        return 'general'

    def _answer_question(self, message: str) -> str:
        """Answer FAQ questions"""
        message_lower = message.lower()

        # Find best matching FAQ
        best_match = None
        best_score = 0

        for key, answer in self.FAQ.items():
            # Simple keyword matching
            keywords = key.split()
            score = sum(1 for kw in keywords if kw in message_lower)

            if score > best_score:
                best_score = score
                best_match = answer

        if best_match and best_score >= 1:
            return best_match

        return "Maaf, saya tidak menemukan jawaban untuk pertanyaan tersebut. Silakan hubungi tim WBS BPKH untuk informasi lebih lanjut."

    def _generate_greeting(self) -> str:
        """Generate greeting response"""
        return """Assalamu'alaikum! 👋

Selamat datang di Whistleblowing System BPKH.

Saya adalah asisten virtual yang siap membantu Anda. Berikut yang bisa saya bantu:

1️⃣ **Menjawab pertanyaan** tentang WBS
2️⃣ **Membantu membuat laporan** pelanggaran
3️⃣ **Memberikan informasi** prosedur pelaporan

Ketik pertanyaan Anda atau ketik "lapor" untuk memulai membuat laporan."""

    def _generate_default_response(self) -> str:
        """Generate default response"""
        return """Terima kasih atas pesan Anda.

Untuk membantu Anda dengan lebih baik, silakan:
- Ajukan pertanyaan tentang WBS
- Ketik "lapor" untuk membuat laporan baru
- Ketik "status" untuk mengecek laporan

Ada yang bisa saya bantu?"""

    def _process_guided_report(self, session: ChatSession, message: str) -> str:
        """Process guided report creation"""
        current_step = session.current_step

        if current_step == 'confirm':
            if message.lower() in ['ya', 'yes', 'benar', 'submit']:
                # Ready to submit
                return "Terima kasih! Laporan Anda siap disubmit. Silakan klik tombol 'Submit Laporan' untuk melanjutkan."
            else:
                # Reset
                session.current_step = 'what'
                session.context = {}
                return f"Baik, mari mulai dari awal.\n\n{self.STEP_PROMPTS['what']}"

        # Save current answer
        session.context[current_step] = message

        # Move to next step
        steps = self.REPORT_STEPS
        current_index = steps.index(current_step)

        if current_index < len(steps) - 1:
            next_step = steps[current_index + 1]
            session.current_step = next_step

            if next_step == 'confirm':
                # Show summary
                summary = self._format_report_summary(session.context)
                return f"Berikut ringkasan laporan Anda:\n\n{summary}\n\n{self.STEP_PROMPTS['confirm']}"
            else:
                return self.STEP_PROMPTS[next_step]

        return "Laporan sudah lengkap."

    def _format_report_summary(self, context: Dict[str, str]) -> str:
        """Format report summary from context"""
        summary = []
        labels = {
            'what': '📋 Kejadian',
            'where': '📍 Lokasi',
            'when': '🕐 Waktu',
            'who': '👤 Pihak Terlibat',
            'how': '🔍 Kronologi'
        }

        for key, label in labels.items():
            if key in context:
                value = context[key][:100] + "..." if len(context.get(key, '')) > 100 else context.get(key, '')
                summary.append(f"{label}: {value}")

        return "\n".join(summary)

    def reset_session(self, session_id: str):
        """Reset a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
