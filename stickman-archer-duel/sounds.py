
import settings


class SoundManager:
    def __init__(self, asset_manager):
        self.assets = asset_manager
        self.enabled = settings.SOUND_ENABLED_DEFAULT
        self.volume = settings.SOUND_VOLUME_DEFAULT
        self._cache = {}

    def play(self, key):
        if not self.enabled:
            return
        filename = settings.SOUND_FILES.get(key)
        if filename is None:
            return
        sound = self._cache.get(key)
        if sound is None:
            sound = self.assets.load_sound(filename)
            self._cache[key] = sound
        sound.set_volume(self.volume)
        sound.play()

    def set_enabled(self, enabled):
        self.enabled = enabled

    def toggle_enabled(self):
        self.enabled = not self.enabled
        return self.enabled

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))

    def adjust_volume(self, delta):
        self.set_volume(self.volume + delta)
