"""
WBS BPKH - Supabase Database Module
Uses REST API directly for reliability
"""

import os
import json
import random
import string
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseDatabase:
    """Database class using Supabase REST API"""

    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')
        self.rest_url = f"{self.url}/rest/v1"

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")

        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        print(f"[OK] Supabase database initialized: {self.url}")

    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """Make a request to Supabase REST API"""
        url = f"{self.rest_url}/{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unknown method: {method}")

            if response.status_code >= 400:
                error_msg = response.text
                print(f"[ERROR] Supabase API error: {response.status_code} - {error_msg[:200]}")
                return None

            if response.text:
                return response.json()
            return {}

        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return None

    def close(self):
        """Close connection (no-op for REST API)"""
        print("[OK] Supabase connection closed")

    # ==================== Report Methods ====================

    def generate_report_id(self) -> str:
        """Generate unique report ID"""
        year = datetime.now().year
        # Get count of reports this year
        result = self._request('GET', 'reports', params={
            'select': 'id',
            'report_id': f'like.WBS-{year}-%'
        })
        count = len(result) if result else 0
        return f"WBS-{year}-{str(count + 1).zfill(6)}"

    def insert_report(self, report_data: dict, ai_result: dict) -> bool:
        """Insert a new report"""
        try:
            data = {
                'report_id': ai_result.get('report_id'),
                'title': report_data.get('title'),
                'description': report_data.get('description'),
                'reported_person': report_data.get('reported_person'),
                'incident_date': report_data.get('incident_date'),
                'location': report_data.get('location'),
                'evidence': report_data.get('evidence'),
                'reporter_name': report_data.get('reporter_name', 'Anonim'),
                'reporter_contact': report_data.get('reporter_contact'),
                'violation_type': ai_result.get('classification', {}).get('violation_type'),
                'violation_code': ai_result.get('classification', {}).get('violation_code'),
                'severity': ai_result.get('classification', {}).get('severity', 'Medium'),
                'priority': ai_result.get('routing', {}).get('priority', 'Normal'),
                'status': 'New',
                'assigned_unit': ai_result.get('routing', {}).get('assigned_unit'),
                'compliance_score': ai_result.get('compliance', {}).get('compliance_score', 0),
                'source_channel': report_data.get('source_channel', 'web'),
                'full_result': json.dumps(ai_result)
            }

            result = self._request('POST', 'reports', data)
            return result is not None

        except Exception as e:
            print(f"[ERROR] Error inserting report: {e}")
            return False

    def get_report(self, report_id: str) -> Optional[dict]:
        """Get a single report by ID"""
        result = self._request('GET', 'reports', params={
            'report_id': f'eq.{report_id}',
            'select': '*'
        })
        return result[0] if result else None

    def get_all_reports(self, limit: int = 100) -> List[dict]:
        """Get all reports"""
        result = self._request('GET', 'reports', params={
            'select': '*',
            'order': 'created_at.desc',
            'limit': limit
        })
        return result or []

    def get_reports_by_severity(self, severity: str) -> List[dict]:
        """Get reports by severity"""
        result = self._request('GET', 'reports', params={
            'severity': f'eq.{severity}',
            'select': '*',
            'order': 'created_at.desc'
        })
        return result or []

    def get_reports_by_status(self, status: str) -> List[dict]:
        """Get reports by status"""
        result = self._request('GET', 'reports', params={
            'status': f'eq.{status}',
            'select': '*',
            'order': 'created_at.desc'
        })
        return result or []

    def search_reports(self, keyword: str) -> List[dict]:
        """Search reports by keyword"""
        result = self._request('GET', 'reports', params={
            'or': f'(title.ilike.%{keyword}%,description.ilike.%{keyword}%)',
            'select': '*',
            'order': 'created_at.desc'
        })
        return result or []

    def update_report_status(self, report_id: str, status: str) -> bool:
        """Update report status"""
        result = self._request('PATCH', 'reports',
            data={'status': status},
            params={'report_id': f'eq.{report_id}'}
        )
        return result is not None

    def update_manager_notes(self, report_id: str, notes: str) -> bool:
        """Update manager notes"""
        result = self._request('PATCH', 'reports',
            data={'manager_notes': notes},
            params={'report_id': f'eq.{report_id}'}
        )
        return result is not None

    def assign_investigator(self, report_id: str, investigator_id: int) -> bool:
        """Assign investigator to report"""
        result = self._request('PATCH', 'reports',
            data={
                'assigned_investigator_id': investigator_id,
                'status': 'Under Investigation'
            },
            params={'report_id': f'eq.{report_id}'}
        )
        return result is not None

    def get_reports_by_investigator(self, investigator_id: int) -> List[dict]:
        """Get reports assigned to investigator"""
        result = self._request('GET', 'reports', params={
            'assigned_investigator_id': f'eq.{investigator_id}',
            'select': '*',
            'order': 'created_at.desc'
        })
        return result or []

    def get_report_for_reporter(self, report_id: str) -> Optional[dict]:
        """Get limited report info for reporter"""
        return self.get_report(report_id)

    # ==================== Report Access (PIN) Methods ====================

    def _hash_pin(self, pin: str) -> str:
        """Hash PIN using SHA256"""
        return hashlib.sha256(pin.encode()).hexdigest()

    def create_report_access(self, report_id: str, email: str = None, phone: str = None) -> str:
        """Create report access with PIN"""
        pin = ''.join(random.choices(string.digits, k=6))
        pin_hash = self._hash_pin(pin)

        data = {
            'report_id': report_id,
            'pin_hash': pin_hash,
            'email': email,
            'phone': phone
        }

        result = self._request('POST', 'report_access', data)
        return pin if result is not None else None

    def validate_report_access(self, report_id: str, pin: str) -> bool:
        """Validate report access with PIN"""
        pin_hash = self._hash_pin(pin)
        result = self._request('GET', 'report_access', params={
            'report_id': f'eq.{report_id}',
            'pin_hash': f'eq.{pin_hash}'
        })
        return bool(result)

    def get_report_access(self, report_id: str) -> Optional[dict]:
        """Get report access info"""
        result = self._request('GET', 'report_access', params={
            'report_id': f'eq.{report_id}'
        })
        return result[0] if result else None

    # ==================== User Methods ====================

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        result = self._request('GET', 'users', params={
            'username': f'eq.{username}',
            'is_active': 'eq.true'
        })
        return result[0] if result else None

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        result = self._request('GET', 'users', params={
            'id': f'eq.{user_id}'
        })
        return result[0] if result else None

    def get_users(self, role: str = None) -> List[dict]:
        """Get all users, optionally filtered by role"""
        params = {'select': '*', 'order': 'full_name'}
        if role:
            params['role'] = f'eq.{role}'
        result = self._request('GET', 'users', params=params)
        return result or []

    def create_user(self, username: str, password: str, email: str,
                   full_name: str, role: str, unit: str = None) -> bool:
        """Create a new user"""
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        data = {
            'username': username,
            'password_hash': password_hash,
            'email': email,
            'full_name': full_name,
            'role': role,
            'unit': unit
        }

        result = self._request('POST', 'users', data)
        return result is not None

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user"""
        result = self._request('PATCH', 'users',
            data=kwargs,
            params={'id': f'eq.{user_id}'}
        )
        return result is not None

    def verify_password(self, stored_hash: str, password: str) -> bool:
        """Verify password against hash"""
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        except:
            return False

    # ==================== Conversation & Message Methods ====================

    def create_conversation(self, report_id: str, channel: str = 'web') -> int:
        """Create a new conversation"""
        data = {
            'report_id': report_id,
            'channel': channel
        }
        result = self._request('POST', 'conversations', data)
        return result[0]['id'] if result else None

    def get_conversation(self, report_id: str) -> Optional[dict]:
        """Get conversation by report ID"""
        result = self._request('GET', 'conversations', params={
            'report_id': f'eq.{report_id}'
        })
        return result[0] if result else None

    def add_message(self, report_id: str, sender_type: str, content: str,
                   sender_id: int = None, message_type: str = 'chat') -> bool:
        """Add a message to conversation"""
        try:
            # Get or create conversation
            conv = self.get_conversation(report_id)
            if not conv:
                conv_id = self.create_conversation(report_id)
            else:
                conv_id = conv['id']

            data = {
                'conversation_id': conv_id,
                'sender_type': sender_type,
                'sender_id': sender_id,
                'content': content,
                'message_type': message_type
            }

            result = self._request('POST', 'messages', data)
            return result is not None

        except Exception as e:
            print(f"[ERROR] Error adding message: {e}")
            return False

    def get_messages(self, report_id: str) -> List[dict]:
        """Get all messages for a report"""
        conv = self.get_conversation(report_id)
        if not conv:
            return []

        result = self._request('GET', 'messages', params={
            'conversation_id': f'eq.{conv["id"]}',
            'select': '*',
            'order': 'created_at'
        })

        messages = result or []

        # Add sender name for manager messages
        for msg in messages:
            if msg['sender_type'] == 'manager' and msg.get('sender_id'):
                user = self.get_user_by_id(msg['sender_id'])
                msg['sender_name'] = user['full_name'] if user else 'Manager'
            else:
                msg['sender_name'] = None

        return messages

    def mark_messages_read(self, report_id: str, reader_type: str) -> bool:
        """Mark messages as read"""
        conv = self.get_conversation(report_id)
        if not conv:
            return False

        # Determine which messages to mark as read
        if reader_type == 'reporter':
            sender_filter = 'manager'
        else:
            sender_filter = 'reporter'

        result = self._request('PATCH', 'messages',
            data={'is_read': True},
            params={
                'conversation_id': f'eq.{conv["id"]}',
                'sender_type': f'eq.{sender_filter}',
                'is_read': 'eq.false'
            }
        )
        return True

    def get_unread_count(self, report_id: str, reader_type: str) -> int:
        """Get unread message count"""
        conv = self.get_conversation(report_id)
        if not conv:
            return 0

        sender_filter = 'manager' if reader_type == 'reporter' else 'reporter'

        result = self._request('GET', 'messages', params={
            'conversation_id': f'eq.{conv["id"]}',
            'sender_type': f'eq.{sender_filter}',
            'is_read': 'eq.false',
            'select': 'id'
        })
        return len(result) if result else 0

    # ==================== Chatbot Session Methods ====================

    def create_chatbot_session(self, session_id: str, channel: str = 'web') -> bool:
        """Create a new chatbot session"""
        data = {
            'session_id': session_id,
            'channel': channel,
            'state': 'greeting',
            'context': json.dumps({}),
            'report_data': json.dumps({})
        }
        result = self._request('POST', 'chatbot_sessions', data)
        return result is not None

    def get_chatbot_session(self, session_id: str) -> Optional[dict]:
        """Get chatbot session"""
        result = self._request('GET', 'chatbot_sessions', params={
            'session_id': f'eq.{session_id}'
        })
        if result:
            session = result[0]
            if isinstance(session.get('context'), str):
                session['context'] = json.loads(session['context'])
            if isinstance(session.get('report_data'), str):
                session['report_data'] = json.loads(session['report_data'])
            return session
        return None

    def update_chatbot_session(self, session_id: str, state: str = None,
                               context: dict = None, report_data: dict = None) -> bool:
        """Update chatbot session"""
        data = {}
        if state:
            data['state'] = state
        if context is not None:
            data['context'] = json.dumps(context)
        if report_data is not None:
            data['report_data'] = json.dumps(report_data)

        result = self._request('PATCH', 'chatbot_sessions',
            data=data,
            params={'session_id': f'eq.{session_id}'}
        )
        return result is not None

    # ==================== Statistics Methods ====================

    def get_statistics(self) -> dict:
        """Get dashboard statistics"""
        try:
            all_reports = self.get_all_reports(limit=1000)

            stats = {
                'total_reports': len(all_reports),
                'critical_reports': len([r for r in all_reports if r.get('severity') == 'Critical']),
                'high_reports': len([r for r in all_reports if r.get('severity') == 'High']),
                'medium_reports': len([r for r in all_reports if r.get('severity') == 'Medium']),
                'low_reports': len([r for r in all_reports if r.get('severity') == 'Low']),
                'avg_compliance_score': 0,
                'reports_last_7_days': 0,
                'by_unit': {},
                'by_status': {}
            }

            if all_reports:
                scores = [r.get('compliance_score', 0) or 0 for r in all_reports]
                stats['avg_compliance_score'] = sum(scores) / len(scores) if scores else 0

                # Count by unit
                for r in all_reports:
                    unit = r.get('assigned_unit', 'Unassigned')
                    stats['by_unit'][unit] = stats['by_unit'].get(unit, 0) + 1

                # Count by status
                for r in all_reports:
                    status = r.get('status', 'New')
                    stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            return stats

        except Exception as e:
            print(f"[ERROR] Error getting statistics: {e}")
            return {}


# Test function
def test_connection():
    """Test Supabase connection"""
    try:
        db = SupabaseDatabase()
        stats = db.get_statistics()
        print(f"Statistics: {stats}")
        db.close()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
