import os
import pygame
from settings import SOUNDS_DIR
class AssetManager:
    def __init__(self):
        self._sound_cache = {}
        self._warned = set()

    def load_sound(self, filename):
        if filename in self._sound_cache:
            return self._sound_cache[filename]

        path = os.path.join(SOUNDS_DIR, filename)
        sound = None

        if os.path.isfile(path):
            try:
                sound = pygame.mixer.Sound(path)
            except pygame.error as e:
                self._warn(f"Failed to load sound '{filename}': {e}")
        else:
            self._warn(f"Sound not found, using silent placeholder: '{filename}'")

        if sound is None:
            sound = self._make_silent_sound()

        self._sound_cache[filename] = sound
        return sound

    def _make_silent_sound(self):
        try:
            return pygame.mixer.Sound(buffer=bytes(bytearray(4)))
        except Exception:
            class _DummySound:
                def play(self, *a, **k):
                    return None

                def set_volume(self, *a, **k):
                    return None

            return _DummySound()

    def _warn(self, message):
        if message not in self._warned:
            print(f"[AssetManager] {message}")
            self._warned.add(message)
