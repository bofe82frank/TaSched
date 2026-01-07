"""
TaSched - Audio Service
Sound playback using pygame.mixer with proper overlap prevention
"""

import pygame
import os
from typing import Optional
from tasched.constants import (
    AUDIO_FREQUENCY,
    AUDIO_SIZE,
    AUDIO_CHANNELS,
    AUDIO_BUFFER
)


class AudioService:
    """
    Manages audio playback with pygame.mixer
    Prevents sound overlap and handles graceful failures
    """

    def __init__(self):
        self.initialized = False
        self.enabled = True
        self.volume = 0.7
        self.current_sound = None
        self._initialize()

    def _initialize(self):
        """Initialize pygame mixer"""
        try:
            # Initialize pygame mixer
            pygame.mixer.init(
                frequency=AUDIO_FREQUENCY,
                size=AUDIO_SIZE,
                channels=AUDIO_CHANNELS,
                buffer=AUDIO_BUFFER
            )
            self.initialized = True
            print("[AudioService] Pygame mixer initialized successfully")
        except Exception as e:
            print(f"[AudioService] Failed to initialize mixer: {e}")
            self.initialized = False
            self.enabled = False

    def set_volume(self, volume: float):
        """
        Set playback volume

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.initialized:
            pygame.mixer.music.set_volume(self.volume)

    def enable(self):
        """Enable audio playback"""
        self.enabled = True

    def disable(self):
        """Disable audio playback"""
        self.enabled = False
        self.stop()

    def play_sound(self, sound_path: str, loop: bool = False) -> bool:
        """
        Play a sound file

        Args:
            sound_path: Path to the sound file
            loop: If True, loop the sound indefinitely

        Returns:
            True if sound started playing, False otherwise
        """
        if not self.enabled or not self.initialized:
            return False

        if not sound_path or not os.path.exists(sound_path):
            print(f"[AudioService] Sound file not found: {sound_path}")
            return False

        try:
            # Stop any currently playing sound
            self.stop()

            # Load and play the new sound
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.set_volume(self.volume)

            if loop:
                pygame.mixer.music.play(loops=-1)  # Loop indefinitely
            else:
                pygame.mixer.music.play()

            self.current_sound = sound_path
            print(f"[AudioService] Playing: {os.path.basename(sound_path)}")
            return True

        except Exception as e:
            print(f"[AudioService] Error playing sound: {e}")
            return False

    def play_warning_sound(self, sound_path: str) -> bool:
        """
        Play a warning sound (one-shot, no loop)

        Args:
            sound_path: Path to the warning sound

        Returns:
            True if sound started playing, False otherwise
        """
        return self.play_sound(sound_path, loop=False)

    def play_timeup_sound(self, sound_path: str) -> bool:
        """
        Play a time-up sound (one-shot, no loop)

        Args:
            sound_path: Path to the time-up sound

        Returns:
            True if sound started playing, False otherwise
        """
        return self.play_sound(sound_path, loop=False)

    def play_background_music(self, sound_path: str) -> bool:
        """
        Play background music (looped)

        Args:
            sound_path: Path to the background music

        Returns:
            True if music started playing, False otherwise
        """
        return self.play_sound(sound_path, loop=True)

    def stop(self):
        """Stop currently playing sound"""
        if self.initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                self.current_sound = None
            except Exception as e:
                print(f"[AudioService] Error stopping sound: {e}")

    def pause(self):
        """Pause currently playing sound"""
        if self.initialized:
            try:
                pygame.mixer.music.pause()
            except Exception as e:
                print(f"[AudioService] Error pausing sound: {e}")

    def unpause(self):
        """Resume paused sound"""
        if self.initialized:
            try:
                pygame.mixer.music.unpause()
            except Exception as e:
                print(f"[AudioService] Error resuming sound: {e}")

    def is_playing(self) -> bool:
        """
        Check if a sound is currently playing

        Returns:
            True if sound is playing, False otherwise
        """
        if not self.initialized:
            return False
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False

    def fadeout(self, duration_ms: int = 1000):
        """
        Fade out current sound

        Args:
            duration_ms: Fade out duration in milliseconds
        """
        if self.initialized and self.is_playing():
            try:
                pygame.mixer.music.fadeout(duration_ms)
            except Exception as e:
                print(f"[AudioService] Error fading out sound: {e}")

    def cleanup(self):
        """Clean up audio resources"""
        if self.initialized:
            try:
                self.stop()
                pygame.mixer.quit()
                self.initialized = False
            except Exception as e:
                print(f"[AudioService] Error during cleanup: {e}")


# Global audio service instance
_audio_service = None


def get_audio_service() -> AudioService:
    """
    Get or create the global audio service instance

    Returns:
        AudioService instance
    """
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
