"""UI Components module"""

from .styles import ISLAMIC_CSS, COLORS, ARABIC_TEXTS
from .components import (
    render_header,
    render_footer,
    render_metric_card,
    render_report_card,
    render_message_bubble,
    render_status_badge
)
from .themes import Theme, get_theme

__all__ = [
    'ISLAMIC_CSS',
    'COLORS',
    'ARABIC_TEXTS',
    'render_header',
    'render_footer',
    'render_metric_card',
    'render_report_card',
    'render_message_bubble',
    'render_status_badge',
    'Theme',
    'get_theme'
]
