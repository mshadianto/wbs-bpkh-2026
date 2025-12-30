"""
Report models
Defines the structure of whistleblowing reports
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class ReportCreate:
    """Data required to create a new report"""
    # 5W+1H Fields
    what: str                          # What happened
    where: str                         # Where it happened
    when: str                          # When it happened
    who: str                           # Who was involved
    how: str                           # How it happened

    # Optional fields
    evidence_description: Optional[str] = None
    source_channel: str = "web"

    def validate(self) -> List[str]:
        """Validate report data, return list of errors"""
        errors = []
        if not self.what or len(self.what.strip()) < 20:
            errors.append("Deskripsi kejadian minimal 20 karakter")
        if not self.where or len(self.where.strip()) < 5:
            errors.append("Lokasi kejadian harus diisi")
        if not self.when or len(self.when.strip()) < 5:
            errors.append("Waktu kejadian harus diisi")
        if not self.who or len(self.who.strip()) < 3:
            errors.append("Pihak terlibat harus diisi")
        if not self.how or len(self.how.strip()) < 10:
            errors.append("Kronologi kejadian minimal 10 karakter")
        return errors


@dataclass
class ReportUpdate:
    """Data for updating a report"""
    status: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None


@dataclass
class Report:
    """Complete report model"""
    id: int
    report_id: str                     # e.g., WBS-2025-000001
    pin_hash: str                      # Hashed PIN for access

    # 5W+1H Fields
    what: str
    where: str
    when: str
    who: str
    how: str

    # Classification (AI-generated)
    category: Optional[str] = None
    severity: Optional[str] = None
    summary: Optional[str] = None
    risk_score: Optional[float] = None

    # Status tracking
    status: str = "submitted"
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None

    # Metadata
    source_channel: str = "web"
    evidence_description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # AI Processing results
    ai_classification: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_recommendations: Optional[str] = None
    compliance_score: Optional[float] = None

    @property
    def is_critical(self) -> bool:
        """Check if report is critical severity"""
        return self.severity == "critical"

    @property
    def is_open(self) -> bool:
        """Check if report is still open"""
        return self.status not in ["resolved", "closed", "rejected"]

    @property
    def days_open(self) -> int:
        """Calculate days since report was created"""
        if not self.created_at:
            return 0
        delta = datetime.now() - self.created_at
        return delta.days

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'pin_hash': self.pin_hash,
            'what': self.what,
            'where': self.where,
            'when': self.when,
            'who': self.who,
            'how': self.how,
            'category': self.category,
            'severity': self.severity,
            'summary': self.summary,
            'risk_score': self.risk_score,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolution_notes': self.resolution_notes,
            'source_channel': self.source_channel,
            'evidence_description': self.evidence_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ai_classification': self.ai_classification,
            'ai_priority': self.ai_priority,
            'ai_recommendations': self.ai_recommendations,
            'compliance_score': self.compliance_score
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Report':
        """Create Report from database row"""
        # Handle datetime parsing
        created_at = row.get('created_at')
        updated_at = row.get('updated_at')

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))

        return cls(
            id=row.get('id', 0),
            report_id=row.get('report_id', ''),
            pin_hash=row.get('pin_hash', ''),
            what=row.get('what', ''),
            where=row.get('where_location', row.get('where', '')),
            when=row.get('when_time', row.get('when', '')),
            who=row.get('who_involved', row.get('who', '')),
            how=row.get('how_method', row.get('how', '')),
            category=row.get('category'),
            severity=row.get('severity'),
            summary=row.get('summary'),
            risk_score=row.get('risk_score'),
            status=row.get('status', 'submitted'),
            assigned_to=row.get('assigned_to'),
            resolution_notes=row.get('resolution_notes'),
            source_channel=row.get('source_channel', 'web'),
            evidence_description=row.get('evidence_description'),
            created_at=created_at,
            updated_at=updated_at,
            ai_classification=row.get('ai_classification'),
            ai_priority=row.get('ai_priority'),
            ai_recommendations=row.get('ai_recommendations'),
            compliance_score=row.get('compliance_score')
        )
