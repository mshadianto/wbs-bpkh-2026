"""
SQLite Database Implementation
Local database for development and small deployments
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

import bcrypt

from .base import DatabaseInterface


class SQLiteDatabase(DatabaseInterface):
    """SQLite implementation of DatabaseInterface"""

    def __init__(self, db_path: str = "wbs_database.db"):
        self.db_path = db_path
        self._is_memory = db_path == ':memory:'
        self._shared_conn = None

        # For in-memory databases, keep a persistent connection
        if self._is_memory:
            self._shared_conn = sqlite3.connect(':memory:', check_same_thread=False)
            self._shared_conn.row_factory = sqlite3.Row

        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        if self._is_memory and self._shared_conn:
            return self._shared_conn

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _get_cursor(self):
        """Context manager for database operations"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            # Don't close shared in-memory connection
            if not self._is_memory:
                conn.close()

    def _init_database(self):
        """Initialize database tables"""
        with self._get_cursor() as cursor:
            # Reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT UNIQUE NOT NULL,
                    pin_hash TEXT NOT NULL,
                    what TEXT NOT NULL,
                    where_location TEXT NOT NULL,
                    when_time TEXT NOT NULL,
                    who_involved TEXT NOT NULL,
                    how_method TEXT NOT NULL,
                    evidence_description TEXT,
                    category TEXT,
                    severity TEXT,
                    summary TEXT,
                    risk_score REAL,
                    status TEXT DEFAULT 'submitted',
                    assigned_to INTEGER,
                    resolution_notes TEXT,
                    source_channel TEXT DEFAULT 'web',
                    ai_classification TEXT,
                    ai_priority TEXT,
                    ai_recommendations TEXT,
                    compliance_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT DEFAULT 'investigator',
                    unit TEXT,
                    email TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')

            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES reports(report_id)
                )
            ''')

            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    sender_type TEXT NOT NULL,
                    sender_id INTEGER,
                    content TEXT NOT NULL,
                    message_type TEXT DEFAULT 'chat',
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id)')

            # Create default admin if not exists
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
            if cursor.fetchone()[0] == 0:
                password_hash = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', password_hash, 'Administrator', 'admin'))

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        year = datetime.now().year
        with self._get_cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM reports WHERE report_id LIKE ?', (f'WBS-{year}-%',))
            count = cursor.fetchone()[0] + 1
        return f"WBS-{year}-{count:06d}"

    def _generate_pin(self) -> str:
        """Generate 6-digit PIN"""
        return f"{secrets.randbelow(1000000):06d}"

    def _hash_pin(self, pin: str) -> str:
        """Hash PIN for storage"""
        return hashlib.sha256(pin.encode()).hexdigest()

    # ==================== Report Operations ====================

    def insert_report(self, report_data: Dict[str, Any]) -> Tuple[str, str]:
        report_id = self._generate_report_id()
        pin = self._generate_pin()
        pin_hash = self._hash_pin(pin)

        with self._get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO reports (
                    report_id, pin_hash, what, where_location, when_time,
                    who_involved, how_method, evidence_description, source_channel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report_id,
                pin_hash,
                report_data.get('what'),
                report_data.get('where_location'),
                report_data.get('when_time'),
                report_data.get('who_involved'),
                report_data.get('how_method'),
                report_data.get('evidence_description'),
                report_data.get('source_channel', 'web')
            ))

        return report_id, pin

    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT * FROM reports WHERE report_id = ?', (report_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_all_reports(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = 'SELECT * FROM reports WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)
        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        with self._get_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_report(self, report_id: str, updates: Dict[str, Any]) -> bool:
        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        values = list(updates.values()) + [report_id]

        with self._get_cursor() as cursor:
            cursor.execute(
                f'UPDATE reports SET {set_clause} WHERE report_id = ?',
                values
            )
            return cursor.rowcount > 0

    def verify_report_access(self, report_id: str, pin: str) -> bool:
        pin_hash = self._hash_pin(pin)
        with self._get_cursor() as cursor:
            cursor.execute(
                'SELECT id FROM reports WHERE report_id = ? AND pin_hash = ?',
                (report_id, pin_hash)
            )
            return cursor.fetchone() is not None

    # ==================== User Operations ====================

    def create_user(self, user_data: Dict[str, Any]) -> int:
        with self._get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, role, unit, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'],
                user_data['password_hash'],
                user_data['full_name'],
                user_data.get('role', 'investigator'),
                user_data.get('unit'),
                user_data.get('email')
            ))
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_all_users(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        query = 'SELECT * FROM users WHERE is_active = 1'
        params = []

        if role:
            query += ' AND role = ?'
            params.append(role)

        query += ' ORDER BY full_name'

        with self._get_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            # Update last login
            with self._get_cursor() as cursor:
                cursor.execute(
                    'UPDATE users SET last_login = ? WHERE id = ?',
                    (datetime.now().isoformat(), user['id'])
                )
            return user
        return None

    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        if not updates:
            return False

        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        values = list(updates.values()) + [user_id]

        with self._get_cursor() as cursor:
            cursor.execute(
                f'UPDATE users SET {set_clause} WHERE id = ?',
                values
            )
            return cursor.rowcount > 0

    # ==================== Message Operations ====================

    def get_or_create_conversation(self, report_id: str) -> int:
        with self._get_cursor() as cursor:
            cursor.execute(
                'SELECT id FROM conversations WHERE report_id = ?',
                (report_id,)
            )
            row = cursor.fetchone()
            if row:
                return row['id']

            cursor.execute(
                'INSERT INTO conversations (report_id) VALUES (?)',
                (report_id,)
            )
            return cursor.lastrowid

    def add_message(
        self,
        conversation_id: int,
        sender_type: str,
        content: str,
        sender_id: Optional[int] = None,
        message_type: str = "chat"
    ) -> int:
        with self._get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO messages (conversation_id, sender_type, sender_id, content, message_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (conversation_id, sender_type, sender_id, content, message_type))

            # Update conversation timestamp
            cursor.execute(
                'UPDATE conversations SET updated_at = ? WHERE id = ?',
                (datetime.now().isoformat(), conversation_id)
            )
            return cursor.lastrowid

    def get_messages(
        self,
        conversation_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        with self._get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                LIMIT ? OFFSET ?
            ''', (conversation_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def mark_messages_read(self, conversation_id: int, reader_type: str) -> int:
        # Mark messages from the opposite party as read
        sender_type = 'manager' if reader_type == 'reporter' else 'reporter'

        with self._get_cursor() as cursor:
            cursor.execute('''
                UPDATE messages SET is_read = 1
                WHERE conversation_id = ? AND sender_type = ? AND is_read = 0
            ''', (conversation_id, sender_type))
            return cursor.rowcount

    # ==================== Statistics ====================

    def get_statistics(self) -> Dict[str, Any]:
        with self._get_cursor() as cursor:
            # Total reports
            cursor.execute('SELECT COUNT(*) as total FROM reports')
            total = cursor.fetchone()['total']

            # By status
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM reports GROUP BY status
            ''')
            by_status = {row['status']: row['count'] for row in cursor.fetchall()}

            # By category
            cursor.execute('''
                SELECT category, COUNT(*) as count
                FROM reports WHERE category IS NOT NULL GROUP BY category
            ''')
            by_category = {row['category']: row['count'] for row in cursor.fetchall()}

            # By severity
            cursor.execute('''
                SELECT severity, COUNT(*) as count
                FROM reports WHERE severity IS NOT NULL GROUP BY severity
            ''')
            by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}

            # This month
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            cursor.execute(
                'SELECT COUNT(*) as count FROM reports WHERE created_at >= ?',
                (month_start,)
            )
            this_month = cursor.fetchone()['count']

            return {
                'total': total,
                'by_status': by_status,
                'by_category': by_category,
                'by_severity': by_severity,
                'this_month': this_month,
                'open': by_status.get('submitted', 0) + by_status.get('under_review', 0) + by_status.get('investigation', 0),
                'resolved': by_status.get('resolved', 0) + by_status.get('closed', 0)
            }

    def get_report_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        with self._get_cursor() as cursor:
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM reports
                WHERE created_at >= ?
                GROUP BY DATE(created_at)
                ORDER BY date
            ''', (start_date,))
            return [dict(row) for row in cursor.fetchall()]

    def health_check(self) -> bool:
        try:
            with self._get_cursor() as cursor:
                cursor.execute('SELECT 1')
            return True
        except Exception:
            return False

    def close(self):
        pass  # SQLite connections are closed after each operation
