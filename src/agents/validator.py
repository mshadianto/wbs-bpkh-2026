"""
Validator Agent
Validates report completeness and compliance
"""

import time
import re
from typing import Dict, Any, List

from .base import BaseAgent, AgentResult


class ValidatorAgent(BaseAgent):
    """Agent for validating whistleblowing reports"""

    # Minimum content lengths
    MIN_LENGTHS = {
        'what': 20,
        'where': 5,
        'when': 5,
        'who': 3,
        'how': 10
    }

    # Suspicious patterns that might indicate fake/test reports
    SUSPICIOUS_PATTERNS = [
        r'^test',
        r'^xxx+',
        r'^aaa+',
        r'^123',
        r'^asdf',
        r'^qwerty',
        r'lorem ipsum'
    ]

    def __init__(self):
        super().__init__("ValidatorAgent")

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Validate a report.

        Args:
            input_data: Dict with 5W+1H fields

        Returns:
            AgentResult with validation results
        """
        start_time = time.time()

        errors = []
        warnings = []
        checks = []

        # Check required fields
        for field, min_len in self.MIN_LENGTHS.items():
            value = str(input_data.get(field, '')).strip()

            if not value:
                errors.append(f"Field '{field}' wajib diisi")
                checks.append({'field': field, 'status': 'error', 'message': 'Field kosong'})
            elif len(value) < min_len:
                errors.append(f"Field '{field}' minimal {min_len} karakter")
                checks.append({'field': field, 'status': 'error', 'message': f'Minimal {min_len} karakter'})
            else:
                checks.append({'field': field, 'status': 'ok', 'message': 'Valid'})

        # Check for suspicious content
        suspicious = self._check_suspicious(input_data)
        if suspicious:
            warnings.extend(suspicious)

        # Check for potential PII exposure
        pii_warnings = self._check_pii(input_data)
        warnings.extend(pii_warnings)

        # Calculate compliance score
        total_checks = len(self.MIN_LENGTHS)
        passed = len([c for c in checks if c['status'] == 'ok'])
        compliance_score = (passed / total_checks) * 100 if total_checks > 0 else 0

        is_valid = len(errors) == 0
        processing_time = (time.time() - start_time) * 1000

        return self._create_result(
            success=True,
            data={
                'is_valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'checks': checks,
                'compliance_score': round(compliance_score, 2),
                'field_count': total_checks,
                'passed_count': passed
            },
            processing_time_ms=processing_time
        )

    def _check_suspicious(self, input_data: Dict[str, Any]) -> List[str]:
        """Check for suspicious/test content"""
        warnings = []

        combined_text = ' '.join([
            str(input_data.get('what', '')),
            str(input_data.get('how', ''))
        ]).lower()

        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                warnings.append("Konten terdeteksi sebagai data uji/test")
                break

        # Check for very short combined content
        if len(combined_text) < 50:
            warnings.append("Deskripsi laporan terlalu singkat untuk diproses")

        return warnings

    def _check_pii(self, input_data: Dict[str, Any]) -> List[str]:
        """Check for potential PII (Personally Identifiable Information)"""
        warnings = []

        combined_text = ' '.join([
            str(input_data.get('what', '')),
            str(input_data.get('who', '')),
            str(input_data.get('how', ''))
        ])

        # Check for phone numbers
        if re.search(r'08\d{8,11}', combined_text):
            warnings.append("Terdeteksi nomor telepon - pertimbangkan untuk menghapus jika itu nomor Anda")

        # Check for email
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', combined_text):
            warnings.append("Terdeteksi alamat email - pastikan bukan email pribadi Anda")

        # Check for NIK pattern
        if re.search(r'\d{16}', combined_text):
            warnings.append("Terdeteksi angka 16 digit (mungkin NIK) - jangan sertakan NIK Anda")

        return warnings

    def get_validation_summary(self, result: AgentResult) -> str:
        """Generate human-readable validation summary"""
        data = result.data

        if data.get('is_valid'):
            summary = f"✅ Laporan valid (Skor: {data['compliance_score']}%)"
        else:
            summary = f"❌ Laporan tidak valid ({len(data['errors'])} error)"

        if data.get('warnings'):
            summary += f"\n⚠️ {len(data['warnings'])} peringatan"

        return summary
