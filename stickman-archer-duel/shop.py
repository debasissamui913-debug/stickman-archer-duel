import settings
CATEGORIES = {
    "bow": {
        "catalog": settings.SHOP_ITEMS,
        "owned_key": "owned_skins",
        "equipped_key": "equipped_skin",
        "default_id": settings.DEFAULT_SKIN_ID,
    },
    "color": {
        "catalog": settings.PLAYER_COLOR_ITEMS,
        "owned_key": "owned_player_colors",
        "equipped_key": "equipped_player_color",
        "default_id": settings.DEFAULT_PLAYER_COLOR_ID,
    },
    "background": {
        "catalog": settings.BACKGROUND_THEMES,
        "owned_key": "owned_backgrounds",
        "equipped_key": "equipped_background",
        "default_id": settings.DEFAULT_BACKGROUND_ID,
    },
    "shield": {
        "catalog": settings.SHIELD_ITEMS,
        "owned_key": None,
        "equipped_key": None,
        "default_id": None,
    },
}


class ShopManager:
    def __init__(self, progress_data):
        self.coins = progress_data["coins"]
        self.shields = max(0, int(progress_data.get("shields", 0)))
        self.player_name = progress_data.get("player_name", settings.DEFAULT_PLAYER_NAME)
        self.opponent_name = progress_data.get("opponent_name", settings.DEFAULT_OPPONENT_NAME)

        self._owned = {}
        self._equipped = {}
        for cat, info in CATEGORIES.items():
            if cat == "shield":
                continue
            self._owned[cat] = set(progress_data.get(info["owned_key"], [info["default_id"]]))
            self._equipped[cat] = progress_data.get(info["equipped_key"], info["default_id"])

    def to_dict(self, highest_level):
        data = {
            "coins": self.coins,
            "shields": self.shields,
            "highest_level": highest_level,
            "player_name": self.player_name,
            "opponent_name": self.opponent_name,
        }
        for cat, info in CATEGORIES.items():
            if cat == "shield":
                continue
            data[info["owned_key"]] = list(self._owned[cat])
            data[info["equipped_key"]] = self._equipped[cat]
        return data

    def add_coins(self, amount):
        self.coins += amount

    def get_item(self, category, item_id):
        for item in CATEGORIES[category]["catalog"]:
            if item["id"] == item_id:
                return item
        return None

    def purchase_shield(self, item_id):
        item = self.get_item("shield", item_id)
        if item is None or self.coins < item["cost"]:
            return False
        self.coins -= item["cost"]
        self.shields += 1
        return True

    def is_owned(self, category, item_id):
        return item_id in self._owned[category]

    def can_afford(self, category, item_id):
        item = self.get_item(category, item_id)
        return item is not None and self.coins >= item["cost"]

    def purchase(self, category, item_id):
        if self.is_owned(category, item_id) or not self.can_afford(category, item_id):
            return False
        item = self.get_item(category, item_id)
        if item.get("code_required"):
            return False
        self.coins -= item["cost"]
        self._owned[category].add(item_id)
        return True

    def unlock(self, category, item_id):
        item = self.get_item(category, item_id)
        if item is None or not item.get("code_required"):
            return False
        self._owned[category].add(item_id)
        return True

    def equip(self, category, item_id):
        if item_id in self._owned[category]:
            self._equipped[category] = item_id
            return True
        return False

    def equipped_id(self, category):
        return self._equipped[category]

    
    def get_equipped_bow_colors(self):
        item = self.get_item("bow", self._equipped["bow"]) or settings.SHOP_ITEMS[0]
        return item["bow_color"], item["arrow_color"]

    def get_equipped_player_color(self):
        item = self.get_item("color", self._equipped["color"]) or settings.PLAYER_COLOR_ITEMS[0]
        return item["color"]

    def get_equipped_background_id(self):
        return self._equipped["background"]
