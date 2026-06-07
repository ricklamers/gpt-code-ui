"""Unit tests for MiniMax provider support in gpt-code-ui."""

import json
import os
import importlib
import unittest
from unittest.mock import patch, MagicMock


class TestProviderDetection(unittest.TestCase):
    """Test that the PROVIDER variable is set correctly based on env vars."""

    def _reload_main(self):
        """Reload the webapp main module to pick up env var changes."""
        # We need to mock heavy imports that fail without a running kernel
        with patch.dict("sys.modules", {
            "gpt_code_ui.kernel_program.main": MagicMock(APP_PORT=5010),
            "pandas": MagicMock(),
        }):
            import gpt_code_ui.webapp.main as main_mod
            importlib.reload(main_mod)
            return main_mod

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-minimax-key",
    }, clear=False)
    def test_explicit_minimax_provider(self):
        """OPENAI_API_TYPE=minimax selects MiniMax provider."""
        mod = self._reload_main()
        self.assertEqual(mod.PROVIDER, "minimax")

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "",
        "MINIMAX_API_KEY": "test-minimax-key",
    }, clear=False)
    def test_auto_detect_minimax_when_only_minimax_key(self):
        """MiniMax is auto-detected when MINIMAX_API_KEY is set and OPENAI_API_KEY is not."""
        # Remove OPENAI_API_KEY if present
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        env["OPENAI_API_TYPE"] = ""
        env["MINIMAX_API_KEY"] = "test-minimax-key"
        with patch.dict(os.environ, env, clear=True):
            mod = self._reload_main()
            self.assertEqual(mod.PROVIDER, "minimax")

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "open_ai",
        "OPENAI_API_KEY": "sk-test",
    }, clear=False)
    def test_explicit_openai_provider(self):
        """OPENAI_API_TYPE=open_ai selects OpenAI provider."""
        mod = self._reload_main()
        self.assertEqual(mod.PROVIDER, "open_ai")


class TestMiniMaxModels(unittest.TestCase):
    """Test that AVAILABLE_MODELS is populated correctly for MiniMax."""

    def _reload_main(self):
        with patch.dict("sys.modules", {
            "gpt_code_ui.kernel_program.main": MagicMock(APP_PORT=5010),
            "pandas": MagicMock(),
        }):
            import gpt_code_ui.webapp.main as main_mod
            importlib.reload(main_mod)
            return main_mod

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-key",
    }, clear=False)
    def test_default_minimax_models(self):
        """Default MiniMax models include M3, M2.7 and M2.7-highspeed; M3 is first."""
        # Remove custom MINIMAX_MODELS if set
        env = os.environ.copy()
        env.pop("MINIMAX_MODELS", None)
        env["OPENAI_API_TYPE"] = "minimax"
        env["MINIMAX_API_KEY"] = "test-key"
        with patch.dict(os.environ, env):
            mod = self._reload_main()
            model_names = [m["name"] for m in mod.AVAILABLE_MODELS]
            self.assertIn("MiniMax-M3", model_names)
            self.assertIn("MiniMax-M2.7", model_names)
            self.assertIn("MiniMax-M2.7-highspeed", model_names)
            # M3 should be first (default)
            self.assertEqual(model_names[0], "MiniMax-M3")

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-key",
        "MINIMAX_MODELS": '[{"displayName": "Custom", "name": "custom-model"}]',
    }, clear=False)
    def test_custom_minimax_models(self):
        """Custom MINIMAX_MODELS env var overrides defaults."""
        mod = self._reload_main()
        self.assertEqual(len(mod.AVAILABLE_MODELS), 1)
        self.assertEqual(mod.AVAILABLE_MODELS[0]["name"], "custom-model")


class TestMiniMaxApiConfig(unittest.TestCase):
    """Test that openai library is configured correctly for MiniMax."""

    def _reload_main(self):
        with patch.dict("sys.modules", {
            "gpt_code_ui.kernel_program.main": MagicMock(APP_PORT=5010),
            "pandas": MagicMock(),
        }):
            import gpt_code_ui.webapp.main as main_mod
            importlib.reload(main_mod)
            return main_mod

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-minimax-key",
    }, clear=False)
    def test_minimax_sets_openai_api_type_to_open_ai(self):
        """MiniMax provider sets openai.api_type to 'open_ai' for compatibility."""
        import openai
        env = os.environ.copy()
        env.pop("OPENAI_API_BASE", None)
        env["OPENAI_API_TYPE"] = "minimax"
        env["MINIMAX_API_KEY"] = "test-minimax-key"
        with patch.dict(os.environ, env):
            self._reload_main()
            self.assertEqual(openai.api_type, "open_ai")

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-minimax-key",
    }, clear=False)
    def test_minimax_sets_default_base_url(self):
        """MiniMax provider defaults to https://api.minimax.io/v1."""
        import openai
        env = os.environ.copy()
        env.pop("OPENAI_API_BASE", None)
        env["OPENAI_API_TYPE"] = "minimax"
        env["MINIMAX_API_KEY"] = "test-minimax-key"
        with patch.dict(os.environ, env):
            self._reload_main()
            self.assertEqual(openai.api_base, "https://api.minimax.io/v1")

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-minimax-key",
        "OPENAI_API_BASE": "https://custom.minimax.endpoint/v1",
    }, clear=False)
    def test_minimax_custom_base_url(self):
        """Custom OPENAI_API_BASE overrides the MiniMax default."""
        import openai
        self._reload_main()
        self.assertEqual(openai.api_base, "https://custom.minimax.endpoint/v1")

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-minimax-key",
    }, clear=False)
    def test_minimax_uses_minimax_api_key(self):
        """MiniMax provider uses MINIMAX_API_KEY for openai.api_key."""
        import openai
        self._reload_main()
        self.assertEqual(openai.api_key, "test-minimax-key")


class TestMiniMaxTemperatureClamping(unittest.TestCase):
    """Test that temperature is clamped for MiniMax provider."""

    def _reload_main(self):
        with patch.dict("sys.modules", {
            "gpt_code_ui.kernel_program.main": MagicMock(APP_PORT=5010),
            "pandas": MagicMock(),
        }):
            import gpt_code_ui.webapp.main as main_mod
            importlib.reload(main_mod)
            return main_mod

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-key",
    }, clear=False)
    @patch("openai.ChatCompletion.create")
    def test_temperature_clamped_for_minimax(self, mock_create):
        """Temperature is clamped to (0, 1] for MiniMax."""
        mock_create.return_value = MagicMock(
            choices=[MagicMock(
                finish_reason="stop",
                message=MagicMock(content="```python\nprint('hello')\n```")
            )]
        )
        mod = self._reload_main()
        import asyncio
        loop = asyncio.new_event_loop()
        loop.run_until_complete(mod.get_code("test prompt", model="MiniMax-M2.7"))
        loop.close()

        call_kwargs = mock_create.call_args[1]
        temp = call_kwargs.get("temperature", None)
        self.assertIsNotNone(temp)
        self.assertGreater(temp, 0)
        self.assertLessEqual(temp, 1.0)


class TestMiniMaxModelRouting(unittest.TestCase):
    """Test that MiniMax uses 'model' parameter (not 'deployment_id')."""

    def _reload_main(self):
        with patch.dict("sys.modules", {
            "gpt_code_ui.kernel_program.main": MagicMock(APP_PORT=5010),
            "pandas": MagicMock(),
        }):
            import gpt_code_ui.webapp.main as main_mod
            importlib.reload(main_mod)
            return main_mod

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "minimax",
        "MINIMAX_API_KEY": "test-key",
    }, clear=False)
    @patch("openai.ChatCompletion.create")
    def test_minimax_uses_model_parameter(self, mock_create):
        """MiniMax requests use 'model' key, not 'deployment_id'."""
        mock_create.return_value = MagicMock(
            choices=[MagicMock(
                finish_reason="stop",
                message=MagicMock(content="```python\nprint('hello')\n```")
            )]
        )
        mod = self._reload_main()
        import asyncio
        loop = asyncio.new_event_loop()
        loop.run_until_complete(mod.get_code("test prompt", model="MiniMax-M2.7"))
        loop.close()

        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs["model"], "MiniMax-M2.7")
        self.assertNotIn("deployment_id", call_kwargs)


class TestInvalidProvider(unittest.TestCase):
    """Test that invalid provider raises ValueError."""

    def _reload_main(self):
        with patch.dict("sys.modules", {
            "gpt_code_ui.kernel_program.main": MagicMock(APP_PORT=5010),
            "pandas": MagicMock(),
        }):
            import gpt_code_ui.webapp.main as main_mod
            importlib.reload(main_mod)
            return main_mod

    @patch.dict(os.environ, {
        "OPENAI_API_TYPE": "invalid_provider",
    }, clear=False)
    def test_invalid_provider_raises(self):
        """Unknown OPENAI_API_TYPE raises ValueError."""
        with self.assertRaises(ValueError):
            self._reload_main()


class TestEnvExampleFile(unittest.TestCase):
    """Test that .env.minimax-example file is valid."""

    def test_minimax_env_example_exists(self):
        """The .env.minimax-example file exists."""
        path = os.path.join(
            os.path.dirname(__file__), "..", ".env.minimax-example"
        )
        self.assertTrue(os.path.exists(path))

    def test_minimax_env_example_contains_key_vars(self):
        """The .env.minimax-example file contains required configuration."""
        path = os.path.join(
            os.path.dirname(__file__), "..", ".env.minimax-example"
        )
        with open(path) as f:
            content = f.read()
        self.assertIn("MINIMAX_API_KEY", content)
        self.assertIn("OPENAI_API_TYPE=minimax", content)


if __name__ == "__main__":
    unittest.main()
