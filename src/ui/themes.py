"""
Theme Configuration
Centralized theme settings for the application
"""

from dataclasses import dataclass
from typing import Dict
from functools import lru_cache


@dataclass
class ColorScheme:
    """Color scheme for the theme"""
    primary: str = "#1B5E20"
    secondary: str = "#2E7D32"
    accent: str = "#D4AF37"
    background: str = "#F5F7FA"
    surface: str = "#FFFFFF"
    text_primary: str = "#2C3E50"
    text_secondary: str = "#5D6D7E"
    success: str = "#27AE60"
    warning: str = "#F39C12"
    error: str = "#E74C3C"
    info: str = "#3498DB"


@dataclass
class Typography:
    """Typography settings"""
    font_family: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    font_family_arabic: str = "'Amiri', serif"
    font_size_base: str = "16px"
    font_size_sm: str = "14px"
    font_size_lg: str = "18px"
    font_size_xl: str = "24px"
    font_size_xxl: str = "32px"
    line_height: str = "1.6"


@dataclass
class Spacing:
    """Spacing settings"""
    xs: str = "0.25rem"
    sm: str = "0.5rem"
    md: str = "1rem"
    lg: str = "1.5rem"
    xl: str = "2rem"
    xxl: str = "3rem"


@dataclass
class BorderRadius:
    """Border radius settings"""
    sm: str = "8px"
    md: str = "12px"
    lg: str = "16px"
    xl: str = "20px"
    xxl: str = "24px"
    full: str = "9999px"


@dataclass
class Shadows:
    """Box shadow settings"""
    sm: str = "0 2px 8px rgba(0, 0, 0, 0.04)"
    md: str = "0 4px 16px rgba(0, 0, 0, 0.08)"
    lg: str = "0 8px 32px rgba(0, 0, 0, 0.12)"
    xl: str = "0 16px 48px rgba(0, 0, 0, 0.16)"


@dataclass
class Theme:
    """Complete theme configuration"""
    name: str = "islamic"
    colors: ColorScheme = None
    typography: Typography = None
    spacing: Spacing = None
    border_radius: BorderRadius = None
    shadows: Shadows = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = ColorScheme()
        if self.typography is None:
            self.typography = Typography()
        if self.spacing is None:
            self.spacing = Spacing()
        if self.border_radius is None:
            self.border_radius = BorderRadius()
        if self.shadows is None:
            self.shadows = Shadows()

    def to_css_vars(self) -> str:
        """Generate CSS custom properties from theme"""
        return f"""
        :root {{
            --color-primary: {self.colors.primary};
            --color-secondary: {self.colors.secondary};
            --color-accent: {self.colors.accent};
            --color-background: {self.colors.background};
            --color-surface: {self.colors.surface};
            --color-text-primary: {self.colors.text_primary};
            --color-text-secondary: {self.colors.text_secondary};
            --color-success: {self.colors.success};
            --color-warning: {self.colors.warning};
            --color-error: {self.colors.error};
            --color-info: {self.colors.info};

            --font-family: {self.typography.font_family};
            --font-family-arabic: {self.typography.font_family_arabic};
            --font-size-base: {self.typography.font_size_base};

            --spacing-xs: {self.spacing.xs};
            --spacing-sm: {self.spacing.sm};
            --spacing-md: {self.spacing.md};
            --spacing-lg: {self.spacing.lg};
            --spacing-xl: {self.spacing.xl};

            --radius-sm: {self.border_radius.sm};
            --radius-md: {self.border_radius.md};
            --radius-lg: {self.border_radius.lg};
            --radius-xl: {self.border_radius.xl};

            --shadow-sm: {self.shadows.sm};
            --shadow-md: {self.shadows.md};
            --shadow-lg: {self.shadows.lg};
            --shadow-xl: {self.shadows.xl};
        }}
        """


# Predefined themes
THEMES: Dict[str, Theme] = {
    'islamic': Theme(name='islamic'),
    'dark': Theme(
        name='dark',
        colors=ColorScheme(
            primary="#4CAF50",
            secondary="#81C784",
            accent="#FFD700",
            background="#1A1A2E",
            surface="#2D2D44",
            text_primary="#FFFFFF",
            text_secondary="#B0B0B0"
        )
    )
}


@lru_cache()
def get_theme(name: str = 'islamic') -> Theme:
    """Get theme by name"""
    return THEMES.get(name, THEMES['islamic'])
