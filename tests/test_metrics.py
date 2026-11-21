import unittest

from homelab_monitor.proxmox import ProxmoxClient


class TestMetrics(unittest.TestCase):

    def test_memory_percentage(self):
        vm = {
            "maxmem": 8 * 1024**3,
            "mem": 4 * 1024**3,
        }

        result = ProxmoxClient._memory_percent(vm)

        self.assertEqual(result, 50)

    def test_memory_percentage_zero_memory(self):
        vm = {
            "maxmem": 0,
            "mem": 0,
        }

        result = ProxmoxClient._memory_percent(vm)

        self.assertEqual(result, 0)

    def test_memory_percentage_full_memory(self):
        vm = {
            "maxmem": 16 * 1024**3,
            "mem": 16 * 1024**3,
        }

        result = ProxmoxClient._memory_percent(vm)

        self.assertEqual(result, 100)


if __name__ == "__main__":
    unittest.main()
