"""
Summarizer Agent
Generates executive summaries of reports
"""

import time
from typing import Dict, Any

from .base import BaseAgent, AgentResult


class SummarizerAgent(BaseAgent):
    """Agent for summarizing whistleblowing reports"""

    def __init__(self):
        super().__init__("SummarizerAgent")

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Generate summary for a report.

        Args:
            input_data: Dict with 5W+1H fields and optional classification

        Returns:
            AgentResult with summary and key points
        """
        start_time = time.time()

        # Validate minimum input
        error = self.validate_input(input_data, ['what'])
        if error:
            return self._create_result(False, error=error)

        # Extract key information
        what = str(input_data.get('what', '')).strip()
        where = str(input_data.get('where', '')).strip()
        when = str(input_data.get('when', '')).strip()
        who = str(input_data.get('who', '')).strip()
        how = str(input_data.get('how', '')).strip()

        category = input_data.get('category', 'belum dikategorikan')
        severity = input_data.get('severity', 'belum ditentukan')

        # Generate summary
        summary = self._generate_summary(what, where, when, who, how)

        # Extract key points
        key_points = self._extract_key_points(what, how)

        # Generate recommendations
        recommendations = self._generate_recommendations(category, severity)

        processing_time = (time.time() - start_time) * 1000

        return self._create_result(
            success=True,
            data={
                'summary': summary,
                'key_points': key_points,
                'recommendations': recommendations,
                'word_count': len(summary.split()),
                'category': category,
                'severity': severity
            },
            processing_time_ms=processing_time
        )

    def _generate_summary(
        self,
        what: str,
        where: str,
        when: str,
        who: str,
        how: str
    ) -> str:
        """Generate executive summary from 5W+1H"""

        # Truncate long texts
        what_short = what[:200] + "..." if len(what) > 200 else what
        how_short = how[:150] + "..." if len(how) > 150 else how

        summary_parts = []

        # Main description
        summary_parts.append(f"Laporan mengenai: {what_short}")

        # Location and time
        if where and when:
            summary_parts.append(f"Kejadian terjadi di {where} pada {when}.")
        elif where:
            summary_parts.append(f"Lokasi kejadian: {where}.")
        elif when:
            summary_parts.append(f"Waktu kejadian: {when}.")

        # Involved parties
        if who:
            summary_parts.append(f"Pihak yang diduga terlibat: {who}.")

        # Method
        if how:
            summary_parts.append(f"Modus: {how_short}")

        return " ".join(summary_parts)

    def _extract_key_points(self, what: str, how: str) -> list:
        """Extract key points from the report"""
        key_points = []

        combined = f"{what} {how}".lower()

        # Look for amounts
        import re
        amounts = re.findall(r'rp\.?\s*[\d\.,]+|[\d\.,]+\s*(juta|miliar|ribu)', combined)
        if amounts:
            key_points.append(f"Nilai terkait: {amounts[0]}")

        # Look for dates
        dates = re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}', combined)
        if dates:
            key_points.append(f"Tanggal terkait: {dates[0]}")

        # Look for entities
        entities = re.findall(r'pt\s+[\w\s]+|cv\s+[\w\s]+|ud\s+[\w\s]+', combined)
        if entities:
            key_points.append(f"Entitas terkait: {entities[0].title()}")

        # Add generic points based on content length
        if len(what) > 100:
            key_points.append("Deskripsi kejadian cukup detail")
        if len(how) > 50:
            key_points.append("Modus operandi dijelaskan")

        return key_points[:5]  # Limit to 5 key points

    def _generate_recommendations(self, category: str, severity: str) -> list:
        """Generate action recommendations based on classification"""
        recommendations = []

        # Severity-based recommendations
        if severity == 'critical':
            recommendations.append("Eskalasi segera ke pimpinan")
            recommendations.append("Pertimbangkan investigasi khusus")
            recommendations.append("Amankan bukti yang ada")
        elif severity == 'high':
            recommendations.append("Prioritaskan penanganan")
            recommendations.append("Libatkan tim investigasi")
        elif severity == 'medium':
            recommendations.append("Tindak lanjuti dalam 7 hari kerja")
        else:
            recommendations.append("Review dan verifikasi laporan")

        # Category-based recommendations
        if category in ['corruption', 'fraud', 'embezzlement']:
            recommendations.append("Koordinasi dengan SPI/Internal Audit")
            recommendations.append("Pertimbangkan pelaporan ke APH jika diperlukan")
        elif category in ['harassment', 'discrimination']:
            recommendations.append("Libatkan SDM/HR dalam penanganan")
            recommendations.append("Pastikan kerahasiaan pelapor")

        return recommendations[:4]  # Limit to 4 recommendations
