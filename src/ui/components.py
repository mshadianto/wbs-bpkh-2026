"""
Reusable UI Components
Common components used across the application
"""

from typing import Optional, Dict, Any
from datetime import datetime

from .themes import get_theme
from ..config import ReportStatus, SeverityLevel


def render_header(
    title: str,
    subtitle: str = "",
    show_bismillah: bool = True
) -> str:
    """
    Render Islamic header component.

    Args:
        title: Main title text
        subtitle: Subtitle text
        show_bismillah: Whether to show bismillah

    Returns:
        HTML string for header
    """
    bismillah = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ" if show_bismillah else ""

    return f"""
    <div class="islamic-header">
        <div class="islamic-header-content">
            {f'<div class="bismillah">{bismillah}</div>' if show_bismillah else ''}
            <div class="gold-line"></div>
            <h1 class="header-title">{title}</h1>
            {f'<p class="header-subtitle">{subtitle}</p>' if subtitle else ''}
            <p class="header-org">Badan Pengelola Keuangan Haji (BPKH)</p>
        </div>
    </div>
    """


def render_footer() -> str:
    """Render Islamic footer component."""
    return """
    <div class="islamic-footer">
        <p class="dua-text">بَارَكَ اللَّهُ فِيكُمْ</p>
        <p>&copy; 2025 Badan Pengelola Keuangan Haji (BPKH)</p>
        <p style="font-size: 0.85rem; opacity: 0.8;">Menjaga Amanah Dana Haji dengan Integritas</p>
    </div>
    """


def render_metric_card(
    title: str,
    value: Any,
    icon: str = "📊",
    color: str = None,
    subtitle: str = ""
) -> str:
    """
    Render metric card component.

    Args:
        title: Card title
        value: Metric value
        icon: Emoji icon
        color: Border color (optional)
        subtitle: Additional info

    Returns:
        HTML string for metric card
    """
    theme = get_theme()
    border_color = color or theme.colors.primary

    return f"""
    <div class="metric-card" style="border-left-color: {border_color};">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div>
                <div style="font-size: 0.85rem; color: {theme.colors.text_secondary};">{title}</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: {theme.colors.primary};">{value}</div>
                {f'<div style="font-size: 0.75rem; color: {theme.colors.text_secondary};">{subtitle}</div>' if subtitle else ''}
            </div>
        </div>
    </div>
    """


def render_report_card(
    report_id: str,
    status: str,
    category: Optional[str],
    severity: Optional[str],
    created_at: Optional[datetime],
    summary: Optional[str] = None
) -> str:
    """
    Render report card component.

    Args:
        report_id: Report ID
        status: Current status
        category: Report category
        severity: Severity level
        created_at: Creation timestamp
        summary: Optional summary text

    Returns:
        HTML string for report card
    """
    theme = get_theme()

    # Get severity color
    severity_color = SeverityLevel.get_color(severity) if severity else theme.colors.text_secondary

    # Format date
    date_str = created_at.strftime("%d %b %Y") if created_at else "N/A"

    # Status display
    status_name = ReportStatus.get_display_name(status)

    summary_html = ""
    if summary:
        summary_short = summary[:100] + "..." if len(summary) > 100 else summary
        summary_html = f'<p style="margin: 0.5rem 0; color: {theme.colors.text_secondary}; font-size: 0.9rem;">{summary_short}</p>'

    return f"""
    <div class="islamic-card" style="border-left: 4px solid {severity_color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h4 style="margin: 0; color: {theme.colors.primary}; font-weight: 600;">{report_id}</h4>
                {summary_html}
            </div>
            <span class="status-badge status-{status}">{status_name}</span>
        </div>
        <div style="display: flex; gap: 1rem; margin-top: 0.75rem; font-size: 0.85rem;">
            <span>📁 {category or 'Belum dikategorikan'}</span>
            <span style="color: {severity_color};">⚡ {severity or 'N/A'}</span>
            <span>📅 {date_str}</span>
        </div>
    </div>
    """


def render_message_bubble(
    content: str,
    sender_type: str,
    timestamp: Optional[datetime] = None,
    sender_name: Optional[str] = None
) -> str:
    """
    Render message bubble component.

    Args:
        content: Message content
        sender_type: 'reporter', 'manager', or 'system'
        timestamp: Message timestamp
        sender_name: Optional sender name

    Returns:
        HTML string for message bubble
    """
    theme = get_theme()

    # Determine style based on sender
    if sender_type == 'reporter':
        css_class = "message-reporter"
        align = "left"
        label = "Pelapor"
    elif sender_type == 'manager':
        css_class = "message-manager"
        align = "right"
        label = sender_name or "Pengelola"
    else:
        css_class = "message-system"
        align = "center"
        label = "Sistem"

    time_str = timestamp.strftime("%H:%M") if timestamp else ""

    return f"""
    <div class="{css_class}" style="text-align: {align};">
        <div style="font-size: 0.75rem; color: {theme.colors.text_secondary}; margin-bottom: 0.25rem;">
            {label} {f'• {time_str}' if time_str else ''}
        </div>
        <div>{content}</div>
    </div>
    """


def render_status_badge(status: str) -> str:
    """
    Render status badge component.

    Args:
        status: Status value

    Returns:
        HTML string for status badge
    """
    theme = get_theme()

    colors = {
        'submitted': theme.colors.info,
        'under_review': theme.colors.warning,
        'investigation': theme.colors.secondary,
        'resolved': theme.colors.success,
        'closed': theme.colors.text_secondary,
        'rejected': theme.colors.error
    }

    color = colors.get(status, theme.colors.text_secondary)
    display_name = ReportStatus.get_display_name(status)

    return f"""
    <span style="
        background: {color}20;
        color: {color};
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    ">{display_name}</span>
    """


def render_5w_card(
    title_en: str,
    title_id: str,
    description: str,
    icon: str
) -> str:
    """
    Render 5W+1H card component.

    Args:
        title_en: English title (What, Where, etc.)
        title_id: Indonesian title
        description: Description text
        icon: Emoji icon

    Returns:
        HTML string for 5W card
    """
    return f"""
    <div class="element-5w">
        <span class="element-5w-icon">{icon}</span>
        <div class="element-5w-title">{title_en}</div>
        <div class="element-5w-subtitle">{title_id}</div>
        <div class="element-5w-desc">{description}</div>
    </div>
    """


def render_portal_card(
    title: str,
    description: str,
    features: list,
    icon: str
) -> str:
    """
    Render portal selection card.

    Args:
        title: Portal title
        description: Description
        features: List of feature strings
        icon: Emoji icon

    Returns:
        HTML string for portal card
    """
    features_html = "\n".join([f"<li>✅ {f}</li>" for f in features])

    return f"""
    <div class="portal-card">
        <span class="portal-icon">{icon}</span>
        <div class="portal-title">{title}</div>
        <div class="portal-desc">{description}</div>
        <div class="feature-box">
            <ul>
                {features_html}
            </ul>
        </div>
    </div>
    """
