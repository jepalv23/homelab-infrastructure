
import os
import unittest
from unittest.mock import patch

from homelab_monitor.config import load_config


class TestConfig(unittest.TestCase):

    @patch.dict(
        os.environ,
        {},
        clear=True,
    )
    def test_default_configuration(self):
        config = load_config()

        self.assertEqual(
            config["proxmox_host"],
            "https://127.0.0.1:8006",
        )

        self.assertEqual(
            config["proxmox_user"],
            "monitor@pam",
        )

        self.assertFalse(
            config["verify_ssl"]
        )

        self.assertEqual(
            config["cpu_warning_percent"],
            80,
        )

        self.assertEqual(
            config["memory_warning_percent"],
            80,
        )

    @patch.dict(
        os.environ,
        {
            "PROXMOX_HOST": "https://10.10.10.10:8006",
            "PROXMOX_USER": "monitor@pam",
            "PROXMOX_TOKEN": "test-token",
            "PROXMOX_VERIFY_SSL": "true",
            "CPU_WARNING_PERCENT": "90",
            "MEMORY_WARNING_PERCENT": "85",
        },
        clear=True,
    )
    def test_environment_configuration(self):
        config = load_config()

        self.assertEqual(
            config["proxmox_host"],
            "https://10.10.10.10:8006",
        )

        self.assertEqual(
            config["proxmox_user"],
            "monitor@pam",
        )

        self.assertEqual(
            config["proxmox_token"],
            "test-token",
        )

        self.assertTrue(
            config["verify_ssl"]
        )

        self.assertEqual(
            config["cpu_warning_percent"],
            90,
        )

        self.assertEqual(
            config["memory_warning_percent"],
            85,
        )


if __name__ == "__main__":
    unittest.main()
