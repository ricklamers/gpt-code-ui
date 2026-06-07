"""Integration tests for MiniMax provider support.

These tests verify the MiniMax API integration end-to-end.
They require MINIMAX_API_KEY to be set in the environment and
are skipped otherwise.
"""

import asyncio
import json
import os
import importlib
import unittest
from unittest.mock import patch, MagicMock

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")
SKIP_REASON = "MINIMAX_API_KEY not set; skipping integration tests"


def _reload_main_with_minimax():
    """Reload main module configured for MiniMax."""
    env = os.environ.copy()
    env["OPENAI_API_TYPE"] = "minimax"
    env["MINIMAX_API_KEY"] = MINIMAX_API_KEY
    env.pop("OPENAI_API_BASE", None)
    env.pop("MINIMAX_MODELS", None)

    with patch.dict(os.environ, env):
        with patch.dict("sys.modules", {
            "gpt_code_ui.kernel_program.main": MagicMock(APP_PORT=5010),
            "pandas": MagicMock(),
        }):
            import gpt_code_ui.webapp.main as main_mod
            importlib.reload(main_mod)
            return main_mod


@unittest.skipUnless(MINIMAX_API_KEY, SKIP_REASON)
class TestMiniMaxLiveAPI(unittest.TestCase):
    """Integration tests that call the real MiniMax API."""

    def test_generate_code_with_minimax_m3(self):
        """MiniMax M3 generates Python code from a prompt."""
        mod = _reload_main_with_minimax()
        loop = asyncio.new_event_loop()
        code, text, status = loop.run_until_complete(
            mod.get_code("Print 'hello world'", model="MiniMax-M3")
        )
        loop.close()

        self.assertEqual(status, 200)
        self.assertIsNotNone(code)
        self.assertIn("hello", code.lower())

    def test_generate_code_with_minimax_m27(self):
        """MiniMax M2.7 generates Python code from a prompt."""
        mod = _reload_main_with_minimax()
        loop = asyncio.new_event_loop()
        code, text, status = loop.run_until_complete(
            mod.get_code("Print 'hello world'", model="MiniMax-M2.7")
        )
        loop.close()

        self.assertEqual(status, 200)
        self.assertIsNotNone(code)
        self.assertIn("hello", code.lower())

    def test_generate_code_with_minimax_m27_highspeed(self):
        """MiniMax M2.7-highspeed generates Python code from a prompt."""
        mod = _reload_main_with_minimax()
        loop = asyncio.new_event_loop()
        code, text, status = loop.run_until_complete(
            mod.get_code("Print the number 42", model="MiniMax-M2.7-highspeed")
        )
        loop.close()

        self.assertEqual(status, 200)
        self.assertIsNotNone(code)
        self.assertIn("42", code)

    def test_models_endpoint_returns_minimax_models(self):
        """The /models endpoint returns MiniMax models when configured."""
        mod = _reload_main_with_minimax()
        model_names = [m["name"] for m in mod.AVAILABLE_MODELS]
        self.assertIn("MiniMax-M3", model_names)
        self.assertIn("MiniMax-M2.7", model_names)
        self.assertIn("MiniMax-M2.7-highspeed", model_names)
        # M3 should be the default (first in list)
        self.assertEqual(model_names[0], "MiniMax-M3")


if __name__ == "__main__":
    unittest.main()
