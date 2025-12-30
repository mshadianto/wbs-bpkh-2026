"""
Database Layer for WBS BPKH
SQLite untuk persistence dan analytics
Enhanced with user management, messaging, and multi-channel support
"""

import sqlite3
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

class WBSDatabase:
    """Database manager untuk WBS BPKH"""
    
    def __init__(self, db_path: str = "wbs_database.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database dan create tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Table: Reports
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                reported_person TEXT,
                reporter_name TEXT,
                reporter_contact TEXT,
                incident_date TEXT,
                location TEXT,
                evidence TEXT,
                violation_type TEXT,
                violation_code TEXT,
                severity TEXT,
                priority TEXT,
                assigned_unit TEXT,
                status TEXT DEFAULT 'New',
                completeness_score REAL,
                compliance_score REAL,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                full_result JSON
            )
        """)
        
        # Table: Investigation
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT NOT NULL,
                investigation_plan TEXT,
                evidence_needed TEXT,
                witnesses TEXT,
                timeline TEXT,
                status TEXT DEFAULT 'Planned',
                investigator TEXT,
                findings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
        """)
        
        # Table: Compliance History
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT NOT NULL,
                compliance_score REAL,
                regulatory_status TEXT,
                risks_identified TEXT,
                recommendations TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
        """)
        
        # Table: Analytics (aggregated metrics)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                total_reports INTEGER DEFAULT 0,
                critical_reports INTEGER DEFAULT 0,
                high_reports INTEGER DEFAULT 0,
                medium_reports INTEGER DEFAULT 0,
                low_reports INTEGER DEFAULT 0,
                avg_processing_time REAL,
                avg_compliance_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table: Users (Manager Authentication)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'investigator', 'manager', 'auditor')),
                unit TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)

        # Table: Report Access (Reporter PIN System)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT NOT NULL,
                pin_hash TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
        """)

        # Table: Conversations (Reporter-Manager Communication)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT NOT NULL,
                channel TEXT NOT NULL CHECK (channel IN ('web', 'whatsapp', 'email', 'chatbot')),
                status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
        """)

        # Table: Messages (Conversation Messages)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL CHECK (sender_type IN ('reporter', 'manager', 'system', 'chatbot')),
                sender_id INTEGER,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'chat' CHECK (message_type IN ('text', 'chat', 'file', 'status_update', 'notification')),
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Table: Chatbot Sessions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatbot_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                channel TEXT NOT NULL CHECK (channel IN ('web', 'whatsapp')),
                phone_number TEXT,
                context TEXT,
                report_draft TEXT,
                state TEXT DEFAULT 'greeting' CHECK (state IN ('greeting', 'inquiry', 'report_intake', 'status_check', 'completed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)

        # Table: WhatsApp Channels (WAHA Integration)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                report_id TEXT,
                session_id TEXT,
                status TEXT DEFAULT 'new' CHECK (status IN ('new', 'reporting', 'tracking', 'idle')),
                last_message_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
        """)

        # Table: Notifications
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT NOT NULL,
                recipient_type TEXT NOT NULL CHECK (recipient_type IN ('reporter', 'manager', 'unit')),
                recipient_id TEXT,
                channel TEXT NOT NULL CHECK (channel IN ('email', 'whatsapp', 'web')),
                notification_type TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'delivered', 'read')),
                scheduled_at TIMESTAMP,
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(report_id)
            )
        """)

        # Add new columns to reports table if they don't exist
        try:
            self.cursor.execute("ALTER TABLE reports ADD COLUMN source_channel TEXT DEFAULT 'web'")
        except:
            pass
        try:
            self.cursor.execute("ALTER TABLE reports ADD COLUMN assigned_investigator_id INTEGER")
        except:
            pass
        try:
            self.cursor.execute("ALTER TABLE reports ADD COLUMN whatsapp_phone TEXT")
        except:
            pass
        try:
            self.cursor.execute("ALTER TABLE reports ADD COLUMN manager_notes TEXT")
        except:
            pass

        # Create default admin user if not exists
        self._create_default_admin()

        self.conn.commit()
        print(f"[OK] Database initialized: {self.db_path}")

    def _create_default_admin(self):
        """Create default admin user if not exists"""
        try:
            self.cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not self.cursor.fetchone():
                # Default password: admin123 (should be changed)
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                self.cursor.execute("""
                    INSERT INTO users (username, password_hash, email, full_name, role, unit)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("admin", password_hash, "admin@bpkh.go.id", "Administrator", "admin", "Komite Audit"))
        except Exception as e:
            print(f"[WARN] Could not create default admin: {e}")
    
    def insert_report(self, report_data: Dict, processing_result: Dict) -> bool:
        """Insert new report"""
        try:
            intake = processing_result.get("intake", {})
            classification = processing_result.get("classification", {})
            routing = processing_result.get("routing", {})
            compliance = processing_result.get("compliance", {})
            
            self.cursor.execute("""
                INSERT INTO reports (
                    report_id, title, description, reported_person,
                    reporter_name, reporter_contact, incident_date, location, evidence,
                    violation_type, violation_code, severity, priority,
                    assigned_unit, completeness_score, compliance_score,
                    processing_time, full_result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                processing_result["report_id"],
                report_data.get("title"),
                report_data.get("description"),
                report_data.get("reported_person"),
                report_data.get("reporter_name"),
                report_data.get("reporter_contact"),
                report_data.get("incident_date"),
                report_data.get("location"),
                report_data.get("evidence"),
                classification.get("violation_type"),
                classification.get("violation_code"),
                classification.get("severity"),
                classification.get("priority"),
                routing.get("assigned_unit"),
                intake.get("completeness_score"),
                compliance.get("compliance_score"),
                processing_result.get("total_processing_time"),
                json.dumps(processing_result)
            ))
            
            self.conn.commit()
            
            # Insert investigation plan
            self._insert_investigation(processing_result)
            
            # Insert compliance record
            self._insert_compliance(processing_result)
            
            return True
        except Exception as e:
            print(f"[ERROR] Error inserting report: {e}")
            self.conn.rollback()
            return False
    
    def _insert_investigation(self, result: Dict):
        """Insert investigation plan"""
        investigation = result.get("investigation", {})
        
        self.cursor.execute("""
            INSERT INTO investigations (
                report_id, investigation_plan, evidence_needed,
                witnesses, timeline
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            result["report_id"],
            investigation.get("investigation_plan"),
            json.dumps(investigation.get("evidence_needed", [])),
            json.dumps(investigation.get("witnesses", [])),
            json.dumps(investigation.get("timeline", {}))
        ))
    
    def _insert_compliance(self, result: Dict):
        """Insert compliance record"""
        compliance = result.get("compliance", {})
        
        self.cursor.execute("""
            INSERT INTO compliance_history (
                report_id, compliance_score, regulatory_status,
                risks_identified, recommendations
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            result["report_id"],
            compliance.get("compliance_score"),
            compliance.get("regulatory_status"),
            json.dumps(compliance.get("risks_identified", [])),
            json.dumps(compliance.get("recommendations", []))
        ))
    
    def get_report(self, report_id: str) -> Optional[Dict]:
        """Get report by ID"""
        self.cursor.execute("""
            SELECT * FROM reports WHERE report_id = ?
        """, (report_id,))
        
        row = self.cursor.fetchone()
        if row:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_all_reports(self, limit: int = 100) -> List[Dict]:
        """Get all reports"""
        self.cursor.execute("""
            SELECT * FROM reports ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_reports_by_severity(self, severity: str) -> List[Dict]:
        """Get reports filtered by severity"""
        self.cursor.execute("""
            SELECT * FROM reports WHERE severity = ? ORDER BY created_at DESC
        """, (severity,))
        
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_reports_by_unit(self, unit: str) -> List[Dict]:
        """Get reports assigned to specific unit"""
        self.cursor.execute("""
            SELECT * FROM reports WHERE assigned_unit = ? ORDER BY created_at DESC
        """, (unit,))
        
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        stats = {}
        
        # Total reports
        self.cursor.execute("SELECT COUNT(*) FROM reports")
        stats["total_reports"] = self.cursor.fetchone()[0]
        
        # By severity
        for severity in ["Critical", "High", "Medium", "Low"]:
            self.cursor.execute("SELECT COUNT(*) FROM reports WHERE severity = ?", (severity,))
            stats[f"{severity.lower()}_reports"] = self.cursor.fetchone()[0]
        
        # By violation type
        self.cursor.execute("""
            SELECT violation_type, COUNT(*) as count 
            FROM reports 
            GROUP BY violation_type 
            ORDER BY count DESC
        """)
        stats["by_violation_type"] = dict(self.cursor.fetchall())
        
        # By assigned unit
        self.cursor.execute("""
            SELECT assigned_unit, COUNT(*) as count 
            FROM reports 
            GROUP BY assigned_unit 
            ORDER BY count DESC
        """)
        stats["by_unit"] = dict(self.cursor.fetchall())
        
        # Average scores
        self.cursor.execute("""
            SELECT 
                AVG(completeness_score) as avg_completeness,
                AVG(compliance_score) as avg_compliance,
                AVG(processing_time) as avg_processing_time
            FROM reports
        """)
        row = self.cursor.fetchone()
        stats["avg_completeness_score"] = round(row[0], 2) if row[0] else 0
        stats["avg_compliance_score"] = round(row[1], 2) if row[1] else 0
        stats["avg_processing_time"] = round(row[2], 2) if row[2] else 0
        
        # Recent reports (last 7 days)
        self.cursor.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE created_at >= datetime('now', '-7 days')
        """)
        stats["reports_last_7_days"] = self.cursor.fetchone()[0]
        
        # Recent reports (last 30 days)
        self.cursor.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE created_at >= datetime('now', '-30 days')
        """)
        stats["reports_last_30_days"] = self.cursor.fetchone()[0]
        
        return stats
    
    def get_trend_data(self, days: int = 30) -> List[Dict]:
        """Get trend data for charts"""
        self.cursor.execute("""
            SELECT 
                DATE(created_at) as report_date,
                COUNT(*) as count,
                AVG(compliance_score) as avg_compliance
            FROM reports
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(created_at)
            ORDER BY report_date
        """, (days,))
        
        rows = self.cursor.fetchall()
        return [
            {
                "date": row[0],
                "count": row[1],
                "avg_compliance": round(row[2], 2) if row[2] else 0
            }
            for row in rows
        ]
    
    def search_reports(self, keyword: str) -> List[Dict]:
        """Search reports by keyword"""
        search_term = f"%{keyword}%"
        self.cursor.execute("""
            SELECT * FROM reports 
            WHERE title LIKE ? OR description LIKE ? OR reported_person LIKE ?
            ORDER BY created_at DESC
        """, (search_term, search_term, search_term))
        
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def update_report_status(self, report_id: str, new_status: str) -> bool:
        """Update report status"""
        try:
            self.cursor.execute("""
                UPDATE reports 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE report_id = ?
            """, (new_status, report_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error updating report: {e}")
            return False
    
    def export_to_csv(self, filename: str = "wbs_reports_export.csv") -> str:
        """Export reports to CSV"""
        import csv
        
        self.cursor.execute("""
            SELECT 
                report_id, title, violation_type, severity, 
                assigned_unit, status, completeness_score, 
                compliance_score, created_at
            FROM reports
            ORDER BY created_at DESC
        """)
        
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        
        filepath = f"/home/claude/wbs-bpkh-ai/{filename}"
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        return filepath
    
    # ==================== Report ID & PIN Methods ====================

    def generate_report_id(self) -> str:
        """Generate unique Report ID: WBS-{YYYY}-{NNNNNN}"""
        year = datetime.now().year
        self.cursor.execute(
            "SELECT COUNT(*) FROM reports WHERE report_id LIKE ?",
            (f"WBS-{year}-%",)
        )
        count = self.cursor.fetchone()[0] + 1
        return f"WBS-{year}-{count:06d}"

    def generate_pin(self) -> Tuple[str, str]:
        """Generate 6-digit PIN and its hash"""
        pin = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return pin, pin_hash

    def create_report_access(self, report_id: str, email: str = None, phone: str = None) -> str:
        """Create report access credentials, returns plain PIN"""
        pin, pin_hash = self.generate_pin()
        self.cursor.execute("""
            INSERT INTO report_access (report_id, pin_hash, email, phone)
            VALUES (?, ?, ?, ?)
        """, (report_id, pin_hash, email, phone))
        self.conn.commit()
        return pin

    def validate_report_access(self, report_id: str, pin: str) -> bool:
        """Validate Report ID + PIN combination"""
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        self.cursor.execute("""
            SELECT id FROM report_access
            WHERE report_id = ? AND pin_hash = ?
        """, (report_id, pin_hash))
        result = self.cursor.fetchone()
        if result:
            # Update access count and last accessed
            self.cursor.execute("""
                UPDATE report_access
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE report_id = ? AND pin_hash = ?
            """, (report_id, pin_hash))
            self.conn.commit()
            return True
        return False

    def get_report_for_reporter(self, report_id: str) -> Optional[Dict]:
        """Get sanitized report for reporter view"""
        report = self.get_report(report_id)
        if report:
            # Remove sensitive fields
            safe_fields = ['report_id', 'title', 'status', 'severity', 'priority',
                          'assigned_unit', 'created_at', 'updated_at', 'violation_type']
            return {k: report.get(k) for k in safe_fields}
        return None

    # ==================== User Management Methods ====================

    def create_user(self, username: str, password: str, email: str,
                   full_name: str, role: str, unit: str = None) -> bool:
        """Create new user"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute("""
                INSERT INTO users (username, password_hash, email, full_name, role, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, email, full_name, role, unit))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error creating user: {e}")
            return False

    def validate_user(self, username: str, password: str) -> Optional[Dict]:
        """Validate user login credentials"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("""
            SELECT id, username, email, full_name, role, unit, is_active
            FROM users WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        row = self.cursor.fetchone()
        if row and row[6]:  # Check is_active
            # Update last login
            self.cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?
            """, (username,))
            self.conn.commit()
            return {
                "id": row[0], "username": row[1], "email": row[2],
                "full_name": row[3], "role": row[4], "unit": row[5]
            }
        return None

    def get_users(self, role: str = None) -> List[Dict]:
        """Get all users, optionally filtered by role"""
        if role:
            self.cursor.execute(
                "SELECT id, username, email, full_name, role, unit, is_active FROM users WHERE role = ?",
                (role,)
            )
        else:
            self.cursor.execute(
                "SELECT id, username, email, full_name, role, unit, is_active FROM users"
            )
        rows = self.cursor.fetchall()
        return [{"id": r[0], "username": r[1], "email": r[2], "full_name": r[3],
                 "role": r[4], "unit": r[5], "is_active": bool(r[6])} for r in rows]

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        self.cursor.execute(
            "SELECT id, username, email, full_name, role, unit FROM users WHERE id = ?",
            (user_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return {"id": row[0], "username": row[1], "email": row[2],
                    "full_name": row[3], "role": row[4], "unit": row[5]}
        return None

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields"""
        try:
            allowed = ['email', 'full_name', 'role', 'unit', 'is_active']
            updates = {k: v for k, v in kwargs.items() if k in allowed}
            if not updates:
                return False
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            self.cursor.execute(f"UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error updating user: {e}")
            return False

    # ==================== Conversation & Message Methods ====================

    def create_conversation(self, report_id: str, channel: str = 'web') -> int:
        """Create new conversation for a report"""
        self.cursor.execute("""
            INSERT INTO conversations (report_id, channel)
            VALUES (?, ?)
        """, (report_id, channel))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_conversation(self, report_id: str) -> Optional[Dict]:
        """Get conversation for a report"""
        self.cursor.execute("""
            SELECT id, report_id, channel, status, created_at
            FROM conversations WHERE report_id = ? AND status = 'active'
        """, (report_id,))
        row = self.cursor.fetchone()
        if row:
            return {"id": row[0], "report_id": row[1], "channel": row[2],
                    "status": row[3], "created_at": row[4]}
        return None

    def add_message(self, report_id: str, sender_type: str, content: str,
                   sender_id: int = None, message_type: str = 'text') -> bool:
        """Add message to conversation"""
        try:
            conv = self.get_conversation(report_id)
            if not conv:
                conv_id = self.create_conversation(report_id)
            else:
                conv_id = conv['id']

            self.cursor.execute("""
                INSERT INTO messages (conversation_id, sender_type, sender_id, content, message_type)
                VALUES (?, ?, ?, ?, ?)
            """, (conv_id, sender_type, sender_id, content, message_type))

            # Update conversation timestamp
            self.cursor.execute("""
                UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (conv_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error adding message: {e}")
            return False

    def get_messages(self, report_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a report"""
        conv = self.get_conversation(report_id)
        if not conv:
            return []

        self.cursor.execute("""
            SELECT m.id, m.sender_type, m.sender_id, m.content, m.message_type,
                   m.is_read, m.created_at, u.full_name as sender_name
            FROM messages m
            LEFT JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = ?
            ORDER BY m.created_at ASC
            LIMIT ?
        """, (conv['id'], limit))

        rows = self.cursor.fetchall()
        return [{"id": r[0], "sender_type": r[1], "sender_id": r[2], "content": r[3],
                 "message_type": r[4], "is_read": bool(r[5]), "created_at": r[6],
                 "sender_name": r[7] or ("Pelapor" if r[1] == "reporter" else "System")}
                for r in rows]

    def mark_messages_read(self, report_id: str, reader_type: str) -> bool:
        """Mark messages as read"""
        try:
            conv = self.get_conversation(report_id)
            if not conv:
                return False

            # Mark messages from opposite party as read
            opposite = 'manager' if reader_type == 'reporter' else 'reporter'
            self.cursor.execute("""
                UPDATE messages SET is_read = 1
                WHERE conversation_id = ? AND sender_type = ?
            """, (conv['id'], opposite))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error marking messages read: {e}")
            return False

    def get_unread_count(self, report_id: str, for_type: str) -> int:
        """Get unread message count"""
        conv = self.get_conversation(report_id)
        if not conv:
            return 0

        opposite = 'manager' if for_type == 'reporter' else 'reporter'
        self.cursor.execute("""
            SELECT COUNT(*) FROM messages
            WHERE conversation_id = ? AND sender_type = ? AND is_read = 0
        """, (conv['id'], opposite))
        return self.cursor.fetchone()[0]

    # ==================== Chatbot Session Methods ====================

    def create_chatbot_session(self, channel: str, phone_number: str = None) -> str:
        """Create new chatbot session"""
        session_id = secrets.token_hex(16)
        expires_at = datetime.now() + timedelta(hours=24)
        self.cursor.execute("""
            INSERT INTO chatbot_sessions (session_id, channel, phone_number, expires_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, channel, phone_number, expires_at.isoformat()))
        self.conn.commit()
        return session_id

    def get_chatbot_session(self, session_id: str) -> Optional[Dict]:
        """Get chatbot session"""
        self.cursor.execute("""
            SELECT session_id, channel, phone_number, context, report_draft, state, expires_at
            FROM chatbot_sessions WHERE session_id = ?
        """, (session_id,))
        row = self.cursor.fetchone()
        if row:
            return {
                "session_id": row[0], "channel": row[1], "phone_number": row[2],
                "context": json.loads(row[3]) if row[3] else {},
                "report_draft": json.loads(row[4]) if row[4] else {},
                "state": row[5], "expires_at": row[6]
            }
        return None

    def get_session_by_phone(self, phone_number: str) -> Optional[Dict]:
        """Get active session by phone number"""
        self.cursor.execute("""
            SELECT session_id, channel, phone_number, context, report_draft, state, expires_at
            FROM chatbot_sessions
            WHERE phone_number = ? AND expires_at > datetime('now')
            ORDER BY created_at DESC LIMIT 1
        """, (phone_number,))
        row = self.cursor.fetchone()
        if row:
            return {
                "session_id": row[0], "channel": row[1], "phone_number": row[2],
                "context": json.loads(row[3]) if row[3] else {},
                "report_draft": json.loads(row[4]) if row[4] else {},
                "state": row[5], "expires_at": row[6]
            }
        return None

    def update_chatbot_session(self, session_id: str, state: str = None,
                               context: Dict = None, report_draft: Dict = None) -> bool:
        """Update chatbot session"""
        try:
            updates = []
            values = []
            if state:
                updates.append("state = ?")
                values.append(state)
            if context is not None:
                updates.append("context = ?")
                values.append(json.dumps(context))
            if report_draft is not None:
                updates.append("report_draft = ?")
                values.append(json.dumps(report_draft))

            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                values.append(session_id)
                self.cursor.execute(
                    f"UPDATE chatbot_sessions SET {', '.join(updates)} WHERE session_id = ?",
                    values
                )
                self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error updating session: {e}")
            return False

    # ==================== WhatsApp Channel Methods ====================

    def get_or_create_wa_channel(self, phone_number: str) -> Dict:
        """Get or create WhatsApp channel"""
        self.cursor.execute(
            "SELECT id, phone_number, report_id, session_id, status FROM whatsapp_channels WHERE phone_number = ?",
            (phone_number,)
        )
        row = self.cursor.fetchone()
        if row:
            return {"id": row[0], "phone_number": row[1], "report_id": row[2],
                    "session_id": row[3], "status": row[4]}

        # Create new channel
        self.cursor.execute("""
            INSERT INTO whatsapp_channels (phone_number, status) VALUES (?, 'new')
        """, (phone_number,))
        self.conn.commit()
        return {"id": self.cursor.lastrowid, "phone_number": phone_number,
                "report_id": None, "session_id": None, "status": "new"}

    def update_wa_channel(self, phone_number: str, **kwargs) -> bool:
        """Update WhatsApp channel"""
        try:
            allowed = ['report_id', 'session_id', 'status']
            updates = {k: v for k, v in kwargs.items() if k in allowed}
            if not updates:
                return False
            updates['last_message_at'] = datetime.now().isoformat()
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [phone_number]
            self.cursor.execute(f"UPDATE whatsapp_channels SET {set_clause} WHERE phone_number = ?", values)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error updating WA channel: {e}")
            return False

    # ==================== Notification Methods ====================

    def create_notification(self, report_id: str, recipient_type: str, channel: str,
                           notification_type: str, content: str, recipient_id: str = None) -> int:
        """Create notification"""
        self.cursor.execute("""
            INSERT INTO notifications (report_id, recipient_type, recipient_id, channel, notification_type, content)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (report_id, recipient_type, recipient_id, channel, notification_type, content))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_pending_notifications(self, channel: str = None) -> List[Dict]:
        """Get pending notifications"""
        if channel:
            self.cursor.execute("""
                SELECT id, report_id, recipient_type, recipient_id, channel, notification_type, content
                FROM notifications WHERE status = 'pending' AND channel = ?
            """, (channel,))
        else:
            self.cursor.execute("""
                SELECT id, report_id, recipient_type, recipient_id, channel, notification_type, content
                FROM notifications WHERE status = 'pending'
            """)
        rows = self.cursor.fetchall()
        return [{"id": r[0], "report_id": r[1], "recipient_type": r[2], "recipient_id": r[3],
                 "channel": r[4], "notification_type": r[5], "content": r[6]} for r in rows]

    def update_notification_status(self, notification_id: int, status: str) -> bool:
        """Update notification status"""
        try:
            sent_at = datetime.now().isoformat() if status == 'sent' else None
            self.cursor.execute("""
                UPDATE notifications SET status = ?, sent_at = ? WHERE id = ?
            """, (status, sent_at, notification_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error updating notification: {e}")
            return False

    # ==================== Report Assignment Methods ====================

    def assign_investigator(self, report_id: str, investigator_id: int) -> bool:
        """Assign investigator to report"""
        try:
            self.cursor.execute("""
                UPDATE reports SET assigned_investigator_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE report_id = ?
            """, (investigator_id, report_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error assigning investigator: {e}")
            return False

    def get_reports_by_investigator(self, investigator_id: int) -> List[Dict]:
        """Get reports assigned to investigator"""
        self.cursor.execute("""
            SELECT * FROM reports WHERE assigned_investigator_id = ? ORDER BY created_at DESC
        """, (investigator_id,))
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def update_manager_notes(self, report_id: str, notes: str) -> bool:
        """Update manager notes on report"""
        try:
            self.cursor.execute("""
                UPDATE reports SET manager_notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE report_id = ?
            """, (notes, report_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Error updating notes: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")

    def __del__(self):
        """Destructor"""
        self.close()
