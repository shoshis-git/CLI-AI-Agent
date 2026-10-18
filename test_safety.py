import unittest
from unittest.mock import patch

import main


class CommandSafetyTests(unittest.TestCase):
    def test_allows_read_only_command(self):
        self.assertEqual(main.validate_command("dir Documents\\Reports"), "dir Documents\\Reports")

    def test_blocks_unlisted_destructive_command(self):
        self.assertTrue(main.validate_command("del Downloads\\*.tmp").startswith("BLOCKED:"))

    def test_blocks_shell_chaining_and_substitution(self):
        for command in ("dir & del *", "dir | findstr pdf", "dir $(whoami)"):
            with self.subTest(command=command):
                self.assertTrue(main.validate_command(command).startswith("BLOCKED:"))

    def test_blocks_mutating_ipconfig_options(self):
        self.assertTrue(main.validate_command("ipconfig /release").startswith("BLOCKED:"))

    def test_preserves_clarification_response(self):
        message = "CLARIFICATION_REQUIRED: Which folder?"
        self.assertEqual(main.validate_command(message), message)

    def test_empty_instruction_requests_clarification(self):
        with patch.object(main, "USE_MOCK", True):
            self.assertTrue(main.generate_command(" ").startswith("CLARIFICATION_REQUIRED:"))

    def test_unknown_mock_instruction_does_not_return_demo_text(self):
        with patch.object(main, "USE_MOCK", True):
            result = main.generate_command("Show every folder on my computer")
        self.assertTrue(result.startswith("CLARIFICATION_REQUIRED:"))


if __name__ == "__main__":
    unittest.main()