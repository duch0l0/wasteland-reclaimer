"""Звук: каждый файл assets/sounds/music записан в CREDITS_AUDIO.md, ключи, которые вызывает код, звучат."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(ROOT, "assets", "sounds")


def own_keys():
    return {re.sub(r"_\d+$", "", f[:-4]) for f in os.listdir(SFX) if f.endswith(".ogg")}


class AudioFiles(unittest.TestCase):
    def test_keys_used_by_code_have_own_sound(self):
        used = set()
        for dp, _, fs in os.walk(os.path.join(ROOT, "src")):
            for f in fs:
                if f.endswith(".py"):
                    with open(os.path.join(dp, f), encoding="utf-8") as fh:
                        used |= set(re.findall(r'audio\.play\(\s*"([a-z_]+)"', fh.read()))
        pending = {"hit_bullet"}   # пока играет прежний hit (FALLBACK)
        missing = used - own_keys() - pending
        self.assertFalse(missing, f"нет своего файла для: {sorted(missing)}")

    def test_all_files_credited(self):
        with open(os.path.join(ROOT, "CREDITS_AUDIO.md"), encoding="utf-8") as f:
            tokens = set(re.findall(r"[a-z][a-z_]*\*?", f.read()))
        exact = {t for t in tokens if not t.endswith("*")}
        prefixes = {t[:-1] for t in tokens if t.endswith("*")}   # «step_dirt_*»
        for key in own_keys():
            self.assertTrue(key in exact or any((key + "_").startswith(p) for p in prefixes),
                            f"{key}: нет записи в CREDITS_AUDIO.md")


if __name__ == "__main__":
    unittest.main()
