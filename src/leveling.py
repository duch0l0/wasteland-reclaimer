"""Опыт и рост характеристик персонажа."""


class LevelSystem:
    def __init__(self, xp_to_level_fn):
        self.level = 1
        self.xp = 0
        self.xp_to_level_fn = xp_to_level_fn

    @property
    def xp_needed(self):
        return self.xp_to_level_fn(self.level)

    def add_xp(self, amount):
        """Возвращает список сообщений о повышениях уровня (для UI/лога)."""
        messages = []
        self.xp += amount
        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            messages.append(f"Уровень повышен: теперь {self.level}!")
        return messages
