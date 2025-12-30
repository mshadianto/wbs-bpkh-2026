"""
Utility Functions for WBS BPKH
Helper functions dan formatting utilities
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re

def format_currency(amount: float) -> str:
    """Format currency to Indonesian Rupiah"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def format_datetime(dt_string: str) -> str:
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%d %B %Y, %H:%M WIB")
    except:
        return dt_string

def format_date(date_string: str) -> str:
    """Format date string"""
    try:
        dt = datetime.fromisoformat(date_string)
        return dt.strftime("%d %B %Y")
    except:
        return date_string

def calculate_sla_status(created_at: str, sla_hours: int) -> Dict:
    """Calculate SLA status and remaining time"""
    try:
        created = datetime.fromisoformat(created_at)
        deadline = created + timedelta(hours=sla_hours)
        now = datetime.now()
        
        remaining = deadline - now
        remaining_hours = remaining.total_seconds() / 3600
        
        if remaining_hours < 0:
            status = "Overdue"
            color = "#FF0000"
        elif remaining_hours < sla_hours * 0.2:  # < 20% remaining
            status = "Critical"
            color = "#FF6B00"
        elif remaining_hours < sla_hours * 0.5:  # < 50% remaining
            status = "Warning"
            color = "#FFD700"
        else:
            status = "On Track"
            color = "#90EE90"
        
        return {
            "status": status,
            "color": color,
            "remaining_hours": max(0, round(remaining_hours, 1)),
            "deadline": deadline.isoformat(),
            "deadline_formatted": format_datetime(deadline.isoformat())
        }
    except:
        return {
            "status": "Unknown",
            "color": "#808080",
            "remaining_hours": 0,
            "deadline": "",
            "deadline_formatted": "N/A"
        }

def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    colors = {
        "Critical": "#FF0000",
        "High": "#FF6B00",
        "Medium": "#FFD700",
        "Low": "#90EE90"
    }
    return colors.get(severity, "#808080")

def get_severity_icon(severity: str) -> str:
    """Get emoji icon for severity level"""
    icons = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢"
    }
    return icons.get(severity, "⚪")

def format_json_pretty(data: Dict) -> str:
    """Format JSON for display"""
    return json.dumps(data, indent=2, ensure_ascii=False)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename untuk export"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename

def generate_report_summary(processing_result: Dict) -> str:
    """Generate executive summary dari processing result"""
    report_id = processing_result.get("report_id", "N/A")
    classification = processing_result.get("classification", {})
    routing = processing_result.get("routing", {})
    compliance = processing_result.get("compliance", {})
    
    summary = f"""
**EXECUTIVE SUMMARY**

Report ID: {report_id}
Violation Type: {classification.get('violation_type', 'N/A')}
Severity: {classification.get('severity', 'N/A')} ({classification.get('priority', 'N/A')})
Assigned Unit: {routing.get('assigned_unit', 'N/A')}
Compliance Score: {compliance.get('compliance_score', 0):.1f}%

**Key Findings:**
- Legal Basis: {classification.get('legal_basis', 'N/A')}
- Risk Score: {classification.get('risk_score', 0)}/100
- SLA Deadline: {routing.get('sla_hours', 0)} hours
- Escalation: {routing.get('escalation_to', 'N/A')}

**Recommendations:**
{chr(10).join('- ' + r for r in compliance.get('recommendations', ['No recommendations']))}
"""
    return summary.strip()

def validate_api_key(api_key: str) -> bool:
    """Validate Groq API key format"""
    if not api_key:
        return False
    # Groq API keys typically start with 'gsk_'
    if not api_key.startswith('gsk_'):
        return False
    if len(api_key) < 40:
        return False
    return True

def create_notification_message(processing_result: Dict) -> str:
    """Create notification message for stakeholders"""
    report_id = processing_result.get("report_id", "N/A")
    classification = processing_result.get("classification", {})
    routing = processing_result.get("routing", {})
    
    message = f"""
🛡️ **WBS BPKH - New Report Notification**

**Report ID:** {report_id}
**Severity:** {get_severity_icon(classification.get('severity', 'Low'))} {classification.get('severity', 'N/A')}
**Violation Type:** {classification.get('violation_type', 'N/A')}
**Assigned Unit:** {routing.get('assigned_unit', 'N/A')}
**SLA Deadline:** {routing.get('sla_hours', 0)} hours

**Action Required:**
Please review and initiate investigation as per SOP.

---
Badan Pengelola Keuangan Haji (BPKH)
"""
    return message.strip()

def export_to_pdf_data(processing_result: Dict) -> Dict:
    """Prepare data untuk PDF export"""
    return {
        "report_id": processing_result.get("report_id", "N/A"),
        "timestamp": format_datetime(processing_result.get("timestamp", "")),
        "classification": processing_result.get("classification", {}),
        "routing": processing_result.get("routing", {}),
        "investigation": processing_result.get("investigation", {}),
        "compliance": processing_result.get("compliance", {}),
        "summary": generate_report_summary(processing_result)
    }

def calculate_performance_metrics(db_stats: Dict) -> Dict:
    """Calculate performance metrics dari database statistics"""
    total = db_stats.get("total_reports", 0)
    
    if total == 0:
        return {
            "total_reports": 0,
            "avg_processing_time": 0,
            "avg_compliance_score": 0,
            "critical_percentage": 0,
            "high_percentage": 0,
            "sla_compliance_rate": 0,
            "performance_grade": "N/A"
        }
    
    critical = db_stats.get("critical_reports", 0)
    high = db_stats.get("high_reports", 0)
    
    metrics = {
        "total_reports": total,
        "avg_processing_time": db_stats.get("avg_processing_time", 0),
        "avg_compliance_score": db_stats.get("avg_compliance_score", 0),
        "critical_percentage": round((critical / total) * 100, 1),
        "high_percentage": round((high / total) * 100, 1),
        "sla_compliance_rate": 100,  # Assumed from stats
    }
    
    # Calculate performance grade
    compliance = metrics["avg_compliance_score"]
    if compliance >= 95:
        grade = "A+ (Excellent)"
    elif compliance >= 90:
        grade = "A (Very Good)"
    elif compliance >= 85:
        grade = "B+ (Good)"
    elif compliance >= 80:
        grade = "B (Fair)"
    elif compliance >= 75:
        grade = "C (Needs Improvement)"
    else:
        grade = "D (Critical Review Required)"
    
    metrics["performance_grade"] = grade
    
    return metrics

def generate_investigation_checklist(investigation_plan: Dict) -> List[str]:
    """Generate checklist dari investigation plan"""
    checklist = []
    
    # Evidence checklist
    evidence = investigation_plan.get("evidence_needed", [])
    if evidence:
        checklist.append("**Evidence Collection:**")
        for item in evidence:
            checklist.append(f"  ☐ {item}")
    
    # Witness checklist
    witnesses = investigation_plan.get("witnesses", [])
    if witnesses:
        checklist.append("\n**Witness Interviews:**")
        for witness in witnesses:
            checklist.append(f"  ☐ Interview: {witness}")
    
    # Timeline checklist
    timeline = investigation_plan.get("timeline", {})
    if timeline:
        checklist.append("\n**Timeline:**")
        for phase, duration in timeline.items():
            checklist.append(f"  ☐ {phase.title()}: {duration}")
    
    return checklist

def mask_sensitive_data(text: str, mask_type: str = "reporter") -> str:
    """Mask sensitive information"""
    if mask_type == "reporter":
        # Mask reporter name and contact
        text = re.sub(r'(\w+)@(\w+)\.(\w+)', r'***@\2.\3', text)
        text = re.sub(r'\+62\s*\d{3}[-\s]?\d{4}[-\s]?\d{3,4}', '+62 ***-****-****', text)
    elif mask_type == "amount":
        # Mask monetary amounts
        text = re.sub(r'Rp\s*[\d.,]+', 'Rp ***', text)
    
    return text

def get_violation_statistics(reports: List[Dict]) -> Dict:
    """Calculate violation type statistics"""
    stats = {}
    
    for report in reports:
        vtype = report.get("violation_type", "Unknown")
        stats[vtype] = stats.get(vtype, 0) + 1
    
    # Sort by count
    sorted_stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    
    return sorted_stats

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}min"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}hr"

def get_trend_indicator(current: float, previous: float) -> str:
    """Get trend indicator (up/down/stable)"""
    if previous == 0:
        return "➡️ New"
    
    change = ((current - previous) / previous) * 100
    
    if change > 5:
        return f"📈 +{change:.1f}%"
    elif change < -5:
        return f"📉 {change:.1f}%"
    else:
        return "➡️ Stable"

def create_error_response(error_message: str, error_type: str = "general") -> Dict:
    """Create standardized error response"""
    return {
        "status": "error",
        "error_type": error_type,
        "message": error_message,
        "timestamp": datetime.now().isoformat(),
        "recommendation": "Please check your input and try again, or contact support if the issue persists."
    }
