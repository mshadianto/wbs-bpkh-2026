"""
Supabase Database Implementation
Cloud database for production deployments
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

import requests
import bcrypt

from .base import DatabaseInterface


class SupabaseDatabase(DatabaseInterface):
    """Supabase implementation of DatabaseInterface"""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

    def _request(
        self,
        method: str,
        table: str,
        data: Any = None,
        params: Dict = None
    ) -> requests.Response:
        """Make HTTP request to Supabase"""
        url = f"{self.url}/rest/v1/{table}"
        return requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data,
            params=params
        )

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        year = datetime.now().year
        resp = self._request(
            'GET', 'reports',
            params={'report_id': f'like.WBS-{year}-%', 'select': 'id'}
        )
        count = len(resp.json()) + 1 if resp.ok else 1
        return f"WBS-{year}-{count:06d}"

    def _generate_pin(self) -> str:
        return f"{secrets.randbelow(1000000):06d}"

    def _hash_pin(self, pin: str) -> str:
        return hashlib.sha256(pin.encode()).hexdigest()

    # ==================== Report Operations ====================

    def insert_report(self, report_data: Dict[str, Any]) -> Tuple[str, str]:
        report_id = self._generate_report_id()
        pin = self._generate_pin()
        pin_hash = self._hash_pin(pin)

        data = {
            'report_id': report_id,
            'pin_hash': pin_hash,
            'what': report_data.get('what'),
            'where_location': report_data.get('where_location'),
            'when_time': report_data.get('when_time'),
            'who_involved': report_data.get('who_involved'),
            'how_method': report_data.get('how_method'),
            'evidence_description': report_data.get('evidence_description'),
            'source_channel': report_data.get('source_channel', 'web'),
            'status': 'submitted'
        }

        resp = self._request('POST', 'reports', data)
        if not resp.ok:
            raise Exception(f"Failed to insert report: {resp.text}")

        return report_id, pin

    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        resp = self._request(
            'GET', 'reports',
            params={'report_id': f'eq.{report_id}', 'limit': '1'}
        )
        if resp.ok and resp.json():
            return resp.json()[0]
        return None

    def get_all_reports(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        params = {
            'order': 'created_at.desc',
            'limit': str(limit),
            'offset': str(offset)
        }

        if status:
            params['status'] = f'eq.{status}'
        if category:
            params['category'] = f'eq.{category}'

        resp = self._request('GET', 'reports', params=params)
        return resp.json() if resp.ok else []

    def update_report(self, report_id: str, updates: Dict[str, Any]) -> bool:
        updates['updated_at'] = datetime.now().isoformat()
        resp = self._request(
            'PATCH', 'reports',
            data=updates,
            params={'report_id': f'eq.{report_id}'}
        )
        return resp.ok

    def verify_report_access(self, report_id: str, pin: str) -> bool:
        pin_hash = self._hash_pin(pin)
        resp = self._request(
            'GET', 'reports',
            params={
                'report_id': f'eq.{report_id}',
                'pin_hash': f'eq.{pin_hash}',
                'select': 'id'
            }
        )
        return resp.ok and len(resp.json()) > 0

    # ==================== User Operations ====================

    def create_user(self, user_data: Dict[str, Any]) -> int:
        resp = self._request('POST', 'users', user_data)
        if resp.ok and resp.json():
            return resp.json()[0]['id']
        raise Exception(f"Failed to create user: {resp.text}")

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        resp = self._request(
            'GET', 'users',
            params={'username': f'eq.{username}', 'limit': '1'}
        )
        if resp.ok and resp.json():
            return resp.json()[0]
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        resp = self._request(
            'GET', 'users',
            params={'id': f'eq.{user_id}', 'limit': '1'}
        )
        if resp.ok and resp.json():
            return resp.json()[0]
        return None

    def get_all_users(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {'is_active': 'eq.true', 'order': 'full_name'}
        if role:
            params['role'] = f'eq.{role}'

        resp = self._request('GET', 'users', params=params)
        return resp.json() if resp.ok else []

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            # Update last login
            self._request(
                'PATCH', 'users',
                data={'last_login': datetime.now().isoformat()},
                params={'id': f'eq.{user["id"]}'}
            )
            return user
        return None

    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        resp = self._request(
            'PATCH', 'users',
            data=updates,
            params={'id': f'eq.{user_id}'}
        )
        return resp.ok

    # ==================== Message Operations ====================

    def get_or_create_conversation(self, report_id: str) -> int:
        # Check existing
        resp = self._request(
            'GET', 'conversations',
            params={'report_id': f'eq.{report_id}', 'limit': '1'}
        )

        if resp.ok and resp.json():
            return resp.json()[0]['id']

        # Create new
        resp = self._request('POST', 'conversations', {'report_id': report_id})
        if resp.ok and resp.json():
            return resp.json()[0]['id']

        raise Exception("Failed to create conversation")

    def add_message(
        self,
        conversation_id: int,
        sender_type: str,
        content: str,
        sender_id: Optional[int] = None,
        message_type: str = "chat"
    ) -> int:
        data = {
            'conversation_id': conversation_id,
            'sender_type': sender_type,
            'sender_id': sender_id,
            'content': content,
            'message_type': message_type
        }

        resp = self._request('POST', 'messages', data)
        if resp.ok and resp.json():
            # Update conversation timestamp
            self._request(
                'PATCH', 'conversations',
                data={'updated_at': datetime.now().isoformat()},
                params={'id': f'eq.{conversation_id}'}
            )
            return resp.json()[0]['id']

        raise Exception(f"Failed to add message: {resp.text}")

    def get_messages(
        self,
        conversation_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        resp = self._request(
            'GET', 'messages',
            params={
                'conversation_id': f'eq.{conversation_id}',
                'order': 'created_at.asc',
                'limit': str(limit),
                'offset': str(offset)
            }
        )
        return resp.json() if resp.ok else []

    def mark_messages_read(self, conversation_id: int, reader_type: str) -> int:
        sender_type = 'manager' if reader_type == 'reporter' else 'reporter'

        resp = self._request(
            'PATCH', 'messages',
            data={'is_read': True},
            params={
                'conversation_id': f'eq.{conversation_id}',
                'sender_type': f'eq.{sender_type}',
                'is_read': 'eq.false'
            }
        )
        return len(resp.json()) if resp.ok else 0

    # ==================== Statistics ====================

    def get_statistics(self) -> Dict[str, Any]:
        # Get all reports for statistics
        resp = self._request('GET', 'reports', params={'select': 'id,status,category,severity,created_at'})
        reports = resp.json() if resp.ok else []

        total = len(reports)
        by_status = {}
        by_category = {}
        by_severity = {}
        this_month = 0

        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)

        for r in reports:
            # By status
            status = r.get('status', 'unknown')
            by_status[status] = by_status.get(status, 0) + 1

            # By category
            if r.get('category'):
                cat = r['category']
                by_category[cat] = by_category.get(cat, 0) + 1

            # By severity
            if r.get('severity'):
                sev = r['severity']
                by_severity[sev] = by_severity.get(sev, 0) + 1

            # This month
            if r.get('created_at'):
                created = datetime.fromisoformat(r['created_at'].replace('Z', '+00:00'))
                if created >= month_start:
                    this_month += 1

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
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        resp = self._request(
            'GET', 'reports',
            params={
                'created_at': f'gte.{start_date}',
                'select': 'created_at'
            }
        )

        if not resp.ok:
            return []

        # Group by date
        date_counts = {}
        for r in resp.json():
            date = r['created_at'][:10]  # YYYY-MM-DD
            date_counts[date] = date_counts.get(date, 0) + 1

        return [{'date': d, 'count': c} for d, c in sorted(date_counts.items())]

    def health_check(self) -> bool:
        try:
            resp = self._request('GET', 'users', params={'limit': '1'})
            return resp.ok
        except Exception:
            return False

    def close(self):
        pass  # No persistent connection to close
