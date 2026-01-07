"""
TaSched - Resource Service
Asset discovery and loading (PyInstaller compatible)
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from tasched.constants import ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR


class ResourceService:
    """
    Manages asset loading with support for both development and PyInstaller builds
    """

    def __init__(self):
        self.base_path = self._get_base_path()
        self.assets_path = self._get_assets_path()
        self.images_path = self._get_images_path()
        self.sounds_path = self._get_sounds_path()

    def _get_base_path(self) -> Path:
        """
        Get the base path of the application
        Works in both development and PyInstaller builds
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys._MEIPASS)
        else:
            # Running in development
            # Navigate from services/ up to project root
            return Path(__file__).parent.parent.parent

    def _get_assets_path(self) -> Path:
        """Get assets directory path"""
        return self.base_path / ASSETS_DIR

    def _get_images_path(self) -> Path:
        """Get images directory path"""
        return self.base_path / IMAGES_DIR

    def _get_sounds_path(self) -> Path:
        """Get sounds directory path"""
        return self.base_path / SOUNDS_DIR

    def resource_path(self, relative_path: str) -> str:
        """
        Get absolute path to resource

        Args:
            relative_path: Relative path from project root

        Returns:
            Absolute path as string
        """
        full_path = self.base_path / relative_path
        return str(full_path)

    def find_asset(self, filename: str, asset_type: str = None) -> Optional[str]:
        """
        Find an asset file by name

        Args:
            filename: Name of the asset file
            asset_type: Optional type hint ('image', 'sound', or None for all)

        Returns:
            Absolute path to asset if found, None otherwise
        """
        search_paths = []

        if asset_type == 'image':
            search_paths = [self.images_path]
        elif asset_type == 'sound':
            search_paths = [self.sounds_path]
        else:
            # Search in all asset directories
            search_paths = [
                self.images_path,
                self.sounds_path,
                self.assets_path
            ]

        for search_path in search_paths:
            if search_path.exists():
                asset_path = search_path / filename
                if asset_path.exists() and asset_path.is_file():
                    return str(asset_path)

        return None

    def get_image(self, filename: str) -> Optional[str]:
        """Get path to image asset"""
        return self.find_asset(filename, 'image')

    def get_sound(self, filename: str) -> Optional[str]:
        """Get path to sound asset"""
        return self.find_asset(filename, 'sound')

    def list_sounds(self) -> List[str]:
        """
        List all available sound files

        Returns:
            List of sound file paths
        """
        sounds = []
        if self.sounds_path.exists():
            for file_path in self.sounds_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.mp3', '.wav', '.ogg']:
                    sounds.append(str(file_path))
        return sorted(sounds)

    def list_sound_names(self) -> List[str]:
        """
        List all available sound file names (without path)

        Returns:
            List of sound filenames
        """
        sounds = []
        if self.sounds_path.exists():
            for file_path in self.sounds_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.mp3', '.wav', '.ogg']:
                    sounds.append(file_path.name)
        return sorted(sounds)

    def list_images(self) -> List[str]:
        """
        List all available image files

        Returns:
            List of image file paths
        """
        images = []
        if self.images_path.exists():
            for file_path in self.images_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.ico']:
                    images.append(str(file_path))
        return sorted(images)

    def asset_exists(self, filename: str, asset_type: str = None) -> bool:
        """
        Check if an asset exists

        Args:
            filename: Name of the asset file
            asset_type: Optional type hint ('image', 'sound', or None)

        Returns:
            True if asset exists, False otherwise
        """
        return self.find_asset(filename, asset_type) is not None

    def get_data_path(self) -> Path:
        """Get data directory path"""
        data_path = self.base_path / "tasched" / "data"
        # Ensure directory exists
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path

    def get_data_file(self, filename: str) -> str:
        """Get path to a data file"""
        return str(self.get_data_path() / filename)


# Global resource service instance
_resource_service = None


def get_resource_service() -> ResourceService:
    """
    Get or create the global resource service instance

    Returns:
        ResourceService instance
    """
    global _resource_service
    if _resource_service is None:
        _resource_service = ResourceService()
    return _resource_service
