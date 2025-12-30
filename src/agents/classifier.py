"""
Classifier Agent
Classifies reports into categories and severity levels
"""

import time
import re
from typing import Dict, Any

from .base import BaseAgent, AgentResult
from ..config import ReportCategory, SeverityLevel


class ClassifierAgent(BaseAgent):
    """Agent for classifying whistleblowing reports"""

    # Keywords for category detection
    CATEGORY_KEYWORDS = {
        ReportCategory.FRAUD: [
            'penipuan', 'tipu', 'palsu', 'manipulasi', 'fiktif', 'pemalsuan',
            'fraud', 'fake', 'bohong', 'menipu'
        ],
        ReportCategory.CORRUPTION: [
            'korupsi', 'suap', 'gratifikasi', 'sogok', 'kickback', 'fee',
            'komisi ilegal', 'mark up', 'markup', 'penggelembungan'
        ],
        ReportCategory.EMBEZZLEMENT: [
            'penggelapan', 'gelapkan', 'curi', 'mencuri', 'embezzle',
            'ambil uang', 'hilang dana', 'seleweng'
        ],
        ReportCategory.CONFLICT_OF_INTEREST: [
            'konflik kepentingan', 'conflict of interest', 'keluarga',
            'rekanan', 'vendor', 'perusahaan sendiri', 'bisnis pribadi'
        ],
        ReportCategory.ABUSE_OF_POWER: [
            'penyalahgunaan wewenang', 'abuse of power', 'jabatan',
            'posisi', 'kekuasaan', 'otoritas', 'memaksa'
        ],
        ReportCategory.HARASSMENT: [
            'pelecehan', 'harassment', 'bully', 'intimidasi', 'ancam',
            'seksual', 'verbal', 'fisik'
        ],
        ReportCategory.DISCRIMINATION: [
            'diskriminasi', 'pilih kasih', 'tidak adil', 'rasis',
            'sara', 'agama', 'suku'
        ],
        ReportCategory.SAFETY_VIOLATION: [
            'keselamatan', 'safety', 'bahaya', 'berbahaya', 'k3',
            'kecelakaan', 'risiko'
        ],
        ReportCategory.POLICY_VIOLATION: [
            'pelanggaran kebijakan', 'sop', 'aturan', 'prosedur',
            'policy violation', 'regulasi'
        ]
    }

    # Keywords for severity
    SEVERITY_KEYWORDS = {
        SeverityLevel.CRITICAL: [
            'sistematis', 'besar', 'masif', 'miliaran', 'pimpinan',
            'direktur', 'komisaris', 'korupsi besar', 'serius'
        ],
        SeverityLevel.HIGH: [
            'signifikan', 'berkelanjutan', 'berulang', 'ratusan juta',
            'manager', 'kepala', 'kerugian besar'
        ],
        SeverityLevel.MEDIUM: [
            'moderat', 'puluhan juta', 'beberapa kali', 'staff senior'
        ],
        SeverityLevel.LOW: [
            'kecil', 'minor', 'pertama kali', 'tidak sengaja', 'juta'
        ]
    }

    def __init__(self):
        super().__init__("ClassifierAgent")

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Classify a report.

        Args:
            input_data: Dict with 'what', 'who', 'how' fields

        Returns:
            AgentResult with category, severity, and confidence scores
        """
        start_time = time.time()

        # Validate input
        error = self.validate_input(input_data, ['what'])
        if error:
            return self._create_result(False, error=error)

        # Combine text for analysis
        text = ' '.join([
            str(input_data.get('what', '')),
            str(input_data.get('who', '')),
            str(input_data.get('how', ''))
        ]).lower()

        # Classify category
        category, category_confidence = self._classify_category(text)

        # Classify severity
        severity, severity_confidence = self._classify_severity(text)

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(severity, category_confidence)

        processing_time = (time.time() - start_time) * 1000

        return self._create_result(
            success=True,
            data={
                'category': category,
                'category_confidence': category_confidence,
                'severity': severity,
                'severity_confidence': severity_confidence,
                'risk_score': risk_score,
                'keywords_found': self._extract_keywords(text)
            },
            processing_time_ms=processing_time
        )

    def _classify_category(self, text: str) -> tuple:
        """Classify report category based on keywords"""
        scores = {}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[category] = score

        if not scores:
            return ReportCategory.OTHER.value, 0.5

        best_category = max(scores.items(), key=lambda x: x[1])
        confidence = min(best_category[1] / 3, 1.0)  # Normalize to 0-1

        return best_category[0].value, confidence

    def _classify_severity(self, text: str) -> tuple:
        """Classify report severity based on keywords"""
        scores = {}

        for severity, keywords in self.SEVERITY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[severity] = score

        if not scores:
            return SeverityLevel.MEDIUM.value, 0.5

        best_severity = max(scores.items(), key=lambda x: x[1])
        confidence = min(best_severity[1] / 2, 1.0)

        return best_severity[0].value, confidence

    def _calculate_risk_score(self, severity: str, confidence: float) -> float:
        """Calculate overall risk score 0-100"""
        severity_weights = {
            SeverityLevel.CRITICAL.value: 1.0,
            SeverityLevel.HIGH.value: 0.75,
            SeverityLevel.MEDIUM.value: 0.5,
            SeverityLevel.LOW.value: 0.25
        }

        base_score = severity_weights.get(severity, 0.5) * 100
        adjusted_score = base_score * (0.5 + confidence * 0.5)

        return round(adjusted_score, 2)

    def _extract_keywords(self, text: str) -> list:
        """Extract relevant keywords found in text"""
        found = []
        all_keywords = []

        for keywords in self.CATEGORY_KEYWORDS.values():
            all_keywords.extend(keywords)
        for keywords in self.SEVERITY_KEYWORDS.values():
            all_keywords.extend(keywords)

        for kw in set(all_keywords):
            if kw in text:
                found.append(kw)

        return found[:10]  # Limit to 10 keywords
