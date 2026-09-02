import json
import os
import settings
DEFAULT_DATA = {
    "coins": 0,
    "highest_level": 1,
    "player_name": settings.DEFAULT_PLAYER_NAME,
    "opponent_name": settings.DEFAULT_OPPONENT_NAME,
    "owned_skins": [settings.DEFAULT_SKIN_ID],
    "equipped_skin": settings.DEFAULT_SKIN_ID,
    "owned_player_colors": [settings.DEFAULT_PLAYER_COLOR_ID],
    "equipped_player_color": settings.DEFAULT_PLAYER_COLOR_ID,
    "owned_backgrounds": [settings.DEFAULT_BACKGROUND_ID],
    "equipped_background": settings.DEFAULT_BACKGROUND_ID,
}

def _ensure_default_owned(owned, default_id):
    if default_id not in owned:
        owned.append(default_id)
    return owned

def load():
    if not os.path.isfile(settings.PROGRESS_FILE):
        return dict(DEFAULT_DATA)
    try:
        with open(settings.PROGRESS_FILE, "r") as f:
            data = json.load(f)

        owned_skins = _ensure_default_owned(data.get("owned_skins", []), settings.DEFAULT_SKIN_ID)
        owned_colors = _ensure_default_owned(data.get("owned_player_colors", []), settings.DEFAULT_PLAYER_COLOR_ID)
        owned_bgs = _ensure_default_owned(data.get("owned_backgrounds", []), settings.DEFAULT_BACKGROUND_ID)

        return {
            "coins": int(data.get("coins", 0)),
            "highest_level": int(data.get("highest_level", 1)),
            "player_name": data.get("player_name", settings.DEFAULT_PLAYER_NAME) or settings.DEFAULT_PLAYER_NAME,
            "opponent_name": data.get("opponent_name", settings.DEFAULT_OPPONENT_NAME) or settings.DEFAULT_OPPONENT_NAME,
            "owned_skins": owned_skins,
            "equipped_skin": data.get("equipped_skin", settings.DEFAULT_SKIN_ID),
            "owned_player_colors": owned_colors,
            "equipped_player_color": data.get("equipped_player_color", settings.DEFAULT_PLAYER_COLOR_ID),
            "owned_backgrounds": owned_bgs,
            "equipped_background": data.get("equipped_background", settings.DEFAULT_BACKGROUND_ID),
        }
    except (json.JSONDecodeError, OSError, ValueError):
        return dict(DEFAULT_DATA)


def save(data):
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    try:
        with open(settings.PROGRESS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass
    return data
