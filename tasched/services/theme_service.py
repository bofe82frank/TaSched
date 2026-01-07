"""
TaSched - Theme Service
Centralized theme management and application
"""

from typing import Dict, Any
from tasched.constants import THEMES, DEFAULT_THEME


class ThemeService:
    """
    Manages application themes and provides theme values to UI components
    """

    def __init__(self, theme_name: str = DEFAULT_THEME):
        self.current_theme_name = theme_name
        self.current_theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

    def set_theme(self, theme_name: str) -> bool:
        """
        Set the active theme
        Returns True if theme was changed, False if theme not found
        """
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.current_theme = THEMES[theme_name]
            return True
        return False

    def get_theme_names(self) -> list:
        """Get list of available theme names"""
        return list(THEMES.keys())

    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """
        Get theme dictionary
        If theme_name is None, returns current theme
        """
        if theme_name:
            return THEMES.get(theme_name, self.current_theme)
        return self.current_theme

    def get_color(self, color_key: str) -> str:
        """Get specific color from current theme"""
        return self.current_theme.get(color_key, "#FFFFFF")

    @property
    def background(self) -> str:
        """Get background color"""
        return self.current_theme['background']

    @property
    def primary_text(self) -> str:
        """Get primary text color"""
        return self.current_theme['primary_text']

    @property
    def accent_1(self) -> str:
        """Get accent color 1"""
        return self.current_theme['accent_1']

    @property
    def accent_2(self) -> str:
        """Get accent color 2 (warnings)"""
        return self.current_theme['accent_2']

    @property
    def accent_3(self) -> str:
        """Get accent color 3 (clock/highlights)"""
        return self.current_theme['accent_3']

    @property
    def footer(self) -> str:
        """Get footer color"""
        return self.current_theme['footer']

    @property
    def name(self) -> str:
        """Get current theme name"""
        return self.current_theme['name']

    @property
    def description(self) -> str:
        """Get current theme description"""
        return self.current_theme['description']

    @property
    def mood(self) -> str:
        """Get current theme mood"""
        return self.current_theme['mood']

    def apply_to_widget(self, widget, bg: str = None, fg: str = None):
        """
        Apply theme colors to a tkinter widget

        Args:
            widget: The tkinter widget to style
            bg: Background color key (e.g., 'background', 'accent_1')
            fg: Foreground/text color key (e.g., 'primary_text')
        """
        try:
            if bg:
                widget.configure(bg=self.get_color(bg))
            if fg:
                widget.configure(fg=self.get_color(fg))
        except Exception:
            pass  # Some widgets don't support all config options

    def get_button_style(self) -> Dict[str, str]:
        """Get standard button styling for current theme"""
        return {
            'bg': self.accent_1,
            'fg': self.primary_text,
            'activebackground': self.accent_3,
            'activeforeground': self.background,
            'relief': 'flat',
            'bd': 0,
            'padx': 20,
            'pady': 10
        }

    def get_entry_style(self) -> Dict[str, str]:
        """Get standard entry/input styling for current theme"""
        return {
            'bg': self.background,
            'fg': self.primary_text,
            'insertbackground': self.primary_text,
            'relief': 'solid',
            'bd': 1
        }

    def get_label_style(self) -> Dict[str, str]:
        """Get standard label styling for current theme"""
        return {
            'bg': self.background,
            'fg': self.primary_text
        }

    def get_frame_style(self) -> Dict[str, str]:
        """Get standard frame styling for current theme"""
        return {
            'bg': self.background
        }


# Global theme service instance
_theme_service = None


def get_theme_service(theme_name: str = None) -> ThemeService:
    """
    Get or create the global theme service instance

    Args:
        theme_name: Optional theme name to initialize with

    Returns:
        ThemeService instance
    """
    global _theme_service
    if _theme_service is None:
        _theme_service = ThemeService(theme_name or DEFAULT_THEME)
    elif theme_name and theme_name != _theme_service.current_theme_name:
        _theme_service.set_theme(theme_name)
    return _theme_service
