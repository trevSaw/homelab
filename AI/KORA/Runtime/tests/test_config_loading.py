"""Phase 14.2D production-readiness tests for Runtime config loading.

These tests validate existing behavior only. No production functionality is
added to satisfy them.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from app import main as main_module


class ConfigLoadingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = main_module.CONFIG_DIR
        self._temp_dir = Path(__file__).resolve().parent.parent / "testdata_config"
        self._temp_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        main_module.CONFIG_DIR = self._tmp
        for child in self._temp_dir.iterdir():
            if child.is_file():
                child.unlink()
        self._temp_dir.rmdir()

    def _write(self, name: str, content: str) -> None:
        (self._temp_dir / name).write_text(content, encoding="utf-8")

    def test_missing_config_file_returns_empty_dict(self) -> None:
        main_module.CONFIG_DIR = self._temp_dir
        self.assertEqual(main_module._load_yaml("does-not-exist.yaml"), {})

    def test_malformed_yaml_raises_documented_parse_error(self) -> None:
        self._write("broken.yaml", "not: [valid\n  - yaml")
        main_module.CONFIG_DIR = self._temp_dir
        # Current behavior: malformed YAML surfaces as a YAMLError at load time
        # (fail loudly) rather than silently returning {}. Documented in
        # Phase 14.2D Known Limitations; no production change introduced here.
        with self.assertRaises(yaml.YAMLError):
            main_module._load_yaml("broken.yaml")

    def test_valid_yaml_returns_dict(self) -> None:
        self._write("valid.yaml", "key: value\nnested:\n  a: 1\n")
        main_module.CONFIG_DIR = self._temp_dir
        result = main_module._load_yaml("valid.yaml")
        self.assertEqual(result, {"key": "value", "nested": {"a": 1}})

    def test_non_dict_yaml_returns_empty_dict(self) -> None:
        self._write("list.yaml", "- item\n- item\n")
        main_module.CONFIG_DIR = self._temp_dir
        self.assertEqual(main_module._load_yaml("list.yaml"), {})


if __name__ == "__main__":
    unittest.main()
