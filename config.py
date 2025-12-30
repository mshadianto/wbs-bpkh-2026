"""
Configuration for WBS BPKH AI System
Enterprise-Grade Whistleblowing System
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AgentConfig:
    """Configuration for AI Agents"""
    model_name: str = "llama-3.3-70b-versatile"  # Groq model
    temperature: float = 0.1
    max_tokens: int = 2000
    
@dataclass
class AppConfig:
    """Application Configuration"""
    app_title: str = "🛡️ WBS BPKH - AI-Powered Whistleblowing System"
    app_subtitle: str = "Badan Pengelola Keuangan Haji (BPKH)"
    version: str = "2.0 Enhanced with AI Multi-Agent"
    
    # Database
    db_path: str = "wbs_database.db"
    
    # Agent Configuration
    agent_config: AgentConfig = field(default_factory=AgentConfig)
    
    # Groq API
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    
    # Contact Information
    contact_info: Dict[str, str] = None
    
    def __post_init__(self):
        self.contact_info = {
            "Email": "wbs@bpkh.go.id",
            "WhatsApp": "+62 853-19000-230",
            "Web Portal": "portal.bpkh.go.id/wbs",
            "Support": "it@bpkh.go.id"
        }

# Violation Types dengan dasar hukum
VIOLATION_TYPES = {
    "Korupsi": {
        "code": "V001",
        "legal_basis": "KUHP Pasal 2, 3 | UU Tipikor",
        "severity": "Critical",
        "keywords": ["korupsi", "suap", "gratifikasi ilegal", "penyalahgunaan wewenang"]
    },
    "Gratifikasi / Penyuapan": {
        "code": "V002",
        "legal_basis": "UU No. 11 Tahun 1980",
        "severity": "High",
        "keywords": ["gratifikasi", "suap", "penyuapan", "hadiah tidak sah"]
    },
    "Penggelapan": {
        "code": "V003",
        "legal_basis": "KUHP Pasal 372",
        "severity": "High",
        "keywords": ["penggelapan", "menghilangkan aset", "mark up"]
    },
    "Penipuan": {
        "code": "V004",
        "legal_basis": "KUHP Pasal 378",
        "severity": "High",
        "keywords": ["penipuan", "fraud", "manipulasi data", "pemalsuan"]
    },
    "Pencurian": {
        "code": "V005",
        "legal_basis": "KUHP Pasal 362",
        "severity": "Medium",
        "keywords": ["pencurian", "pencurian aset", "kehilangan inventaris"]
    },
    "Pemerasan": {
        "code": "V006",
        "legal_basis": "KUHP Pasal 368",
        "severity": "High",
        "keywords": ["pemerasan", "intimidasi", "ancaman"]
    },
    "Benturan Kepentingan": {
        "code": "V007",
        "legal_basis": "UU No. 30 Tahun 2014",
        "severity": "Medium",
        "keywords": ["benturan kepentingan", "conflict of interest", "kepentingan pribadi"]
    },
    "Pelanggaran Kebijakan": {
        "code": "V008",
        "legal_basis": "SOP Internal BPKH",
        "severity": "Medium",
        "keywords": ["pelanggaran sop", "tidak sesuai prosedur", "menyalahi aturan"]
    },
    "Tindakan Curang": {
        "code": "V009",
        "legal_basis": "Kode Etik BPKH",
        "severity": "Low",
        "keywords": ["kecurangan", "pelanggaran etika", "tidak jujur"]
    }
}

# Severity Levels dengan SLA
SEVERITY_LEVELS = {
    "Critical": {
        "priority": "P1",
        "sla_hours": 4,
        "indicators": ["Korupsi", "Fraud >1M", "Penyalahgunaan dana haji"],
        "color": "#FF0000",
        "escalation": "Immediate to Ketua BPKH"
    },
    "High": {
        "priority": "P2",
        "sla_hours": 24,
        "indicators": ["Suap", "Gratifikasi", "Penggelapan"],
        "color": "#FF6B00",
        "escalation": "Director Level"
    },
    "Medium": {
        "priority": "P3",
        "sla_hours": 48,
        "indicators": ["Pelanggaran etika", "Benturan kepentingan"],
        "color": "#FFD700",
        "escalation": "Manager Level"
    },
    "Low": {
        "priority": "P4",
        "sla_hours": 72,
        "indicators": ["Administrative", "Minor violations"],
        "color": "#90EE90",
        "escalation": "Team Lead"
    }
}

# Unit Routing
ROUTING_UNITS = {
    "Satuan Pengawasan Internal (SPI)": ["Korupsi", "Gratifikasi / Penyuapan", "Penggelapan"],
    "Unit Kepatuhan": ["Pelanggaran Kebijakan", "Benturan Kepentingan"],
    "Biro Hukum": ["Penipuan", "Pemerasan", "Pencurian"],
    "Unit SDM": ["Tindakan Curang", "Pelanggaran Kebijakan"],
    "Komite Audit": ["Semua jenis (eskalasi)"]
}

# AI Agent System Prompts
AGENT_PROMPTS = {
    "intake": """Anda adalah Intake Agent untuk WBS BPKH. Tugas Anda:
1. Validasi kelengkapan laporan (4W+1H: What, Who, When, Where, How)
2. Generate Report ID unik
3. Score completeness (0-100)
4. Identifikasi informasi yang kurang

Format output JSON:
{
    "report_id": "WBS-YYYY-XXXX",
    "completeness_score": 85,
    "validation_status": "Complete/Incomplete",
    "missing_info": [],
    "validated_data": {...}
}""",

    "classification": """Anda adalah Classification Agent untuk WBS BPKH. Tugas Anda:
1. Klasifikasi jenis pelanggaran (9 kategori)
2. Assess severity level (Critical/High/Medium/Low)
3. Extract entities (nama, unit, lokasi, nominal)
4. Calculate risk score

Gunakan knowledge base untuk akurasi tinggi.

Format output JSON:
{
    "violation_type": "...",
    "violation_code": "V00X",
    "severity": "...",
    "priority": "PX",
    "risk_score": 0-100,
    "entities": {...},
    "legal_basis": "..."
}""",

    "routing": """Anda adalah Routing Agent untuk WBS BPKH. Tugas Anda:
1. Tentukan unit yang tepat untuk investigasi
2. Check eskalasi berdasarkan severity
3. Generate notifikasi stakeholders

Format output JSON:
{
    "assigned_unit": "...",
    "escalation_to": "...",
    "notification_list": [...],
    "sla_deadline": "ISO datetime"
}""",

    "investigation": """Anda adalah Investigation Agent untuk WBS BPKH. Tugas Anda:
1. Buat investigation plan komprehensif
2. List evidence yang diperlukan
3. Identifikasi witness/stakeholder
4. Susun timeline investigasi

Format output JSON:
{
    "investigation_plan": "...",
    "evidence_needed": [...],
    "witnesses": [...],
    "timeline": {...},
    "resources_required": [...]
}""",

    "compliance": """Anda adalah Compliance Agent untuk WBS BPKH. Tugas Anda:
1. Check compliance terhadap regulasi
2. Monitor SLA adherence
3. Calculate compliance score
4. Flag regulatory risks

Format output JSON:
{
    "compliance_score": 0-100,
    "regulatory_status": "Compliant/Non-Compliant",
    "regulations_checked": [...],
    "risks_identified": [...],
    "recommendations": [...]
}"""
}

# Performance Metrics Target
PERFORMANCE_METRICS = {
    "processing_time_target": 5,  # seconds
    "classification_accuracy_target": 0.95,  # 95%
    "sla_compliance_target": 0.90,  # 90%
    "overall_compliance_target": 0.90  # 90%
}

# Report Status Options
REPORT_STATUSES = [
    "New",
    "Under Review",
    "Investigation",
    "Pending Evidence",
    "Escalated",
    "Resolved",
    "Closed"
]

# User Roles
USER_ROLES = {
    "admin": {
        "name": "Administrator",
        "permissions": ["all"]
    },
    "manager": {
        "name": "Manager Unit",
        "permissions": ["view_unit_reports", "assign_investigators", "update_status", "send_messages"]
    },
    "investigator": {
        "name": "Investigator",
        "permissions": ["view_assigned_reports", "update_investigation", "send_messages"]
    },
    "auditor": {
        "name": "Auditor",
        "permissions": ["view_all_reports", "view_compliance"]
    }
}

# WAHA (WhatsApp HTTP API) Configuration
@dataclass
class WAHAConfig:
    """WAHA WhatsApp Integration Configuration"""
    base_url: str = os.getenv("WAHA_URL", "http://localhost:3000")
    api_key: str = os.getenv("WAHA_API_KEY", "")
    session_name: str = os.getenv("WAHA_SESSION", "wbs-bpkh")
    webhook_url: str = os.getenv("WEBHOOK_URL", "http://localhost:8000/webhook/waha")

# Email Configuration
@dataclass
class EmailConfig:
    """Email Notification Configuration"""
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    from_email: str = os.getenv("FROM_EMAIL", "wbs@bpkh.go.id")
    from_name: str = "WBS BPKH"

# Chatbot Agent Prompt
AGENT_PROMPTS["chatbot"] = """Anda adalah Asisten WBS BPKH, chatbot AI yang membantu dalam sistem whistleblowing.

KEMAMPUAN ANDA:
1. Menjawab pertanyaan tentang prosedur pelaporan whistleblowing
2. Membantu pelapor mengisi laporan secara percakapan (4W+1H)
3. Mengecek status laporan dengan Report ID dan PIN
4. Memberikan informasi tentang jenis pelanggaran dan proses investigasi

PANDUAN PERCAKAPAN:
- Selalu ramah, profesional, dan menjaga kerahasiaan
- Untuk pelaporan, kumpulkan informasi secara bertahap:
  * What: Apa yang terjadi? (judul dan deskripsi)
  * Who: Siapa yang terlibat? (nama terlapor)
  * When: Kapan kejadian terjadi?
  * Where: Di mana lokasi kejadian?
  * How: Bagaimana buktinya?
- Jangan meminta informasi sensitif pelapor kecuali diminta
- Jika pertanyaan di luar scope, arahkan ke kontak resmi

INTENT DETECTION:
- "lapor", "melaporkan", "pengaduan" -> report_intake
- "status", "cek laporan", "tracking" -> status_check
- "apa itu", "bagaimana", "jelaskan" -> inquiry
- Greeting (halo, hi, selamat) -> greeting

OUTPUT FORMAT JSON:
{
    "intent": "greeting|inquiry|report_intake|status_check",
    "response": "Respons untuk user",
    "next_action": "continue|collect_field|submit_report|check_status|end",
    "field_to_collect": "title|description|reported_person|incident_date|location|evidence|null",
    "data": {}
}"""

# Chatbot States
CHATBOT_STATES = {
    "greeting": "Menunggu input awal dari user",
    "inquiry": "Menjawab pertanyaan umum",
    "report_intake": "Mengumpulkan data laporan",
    "status_check": "Mengecek status laporan",
    "completed": "Sesi selesai"
}

# Notification Templates
NOTIFICATION_TEMPLATES = {
    "report_received": {
        "subject": "Laporan Diterima - {report_id}",
        "body": """Laporan Anda telah diterima dan sedang diproses.

Report ID: {report_id}
PIN: {pin}

Simpan Report ID dan PIN ini untuk melacak status laporan Anda.

Terima kasih telah melaporkan.
- Tim WBS BPKH"""
    },
    "status_update": {
        "subject": "Update Status Laporan - {report_id}",
        "body": """Status laporan Anda telah diperbarui.

Report ID: {report_id}
Status Baru: {new_status}

Untuk detail lebih lanjut, silakan cek di portal WBS.

- Tim WBS BPKH"""
    },
    "new_message": {
        "subject": "Pesan Baru - {report_id}",
        "body": """Anda memiliki pesan baru terkait laporan {report_id}.

Silakan login ke portal WBS untuk membaca pesan.

- Tim WBS BPKH"""
    },
    "investigation_assigned": {
        "subject": "Laporan Baru Ditugaskan - {report_id}",
        "body": """Anda telah ditugaskan untuk menginvestigasi laporan:

Report ID: {report_id}
Jenis Pelanggaran: {violation_type}
Severity: {severity}
SLA: {sla_hours} jam

Silakan segera tindak lanjuti.

- Tim WBS BPKH"""
    }
}
