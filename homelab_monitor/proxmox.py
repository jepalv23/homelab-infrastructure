import json
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProxmoxClient:
    """
    Minimal Proxmox API client.

    This intentionally uses Python's standard library so the project
    can communicate with Proxmox without requiring a large dependency.
    """

    def __init__(
        self,
        host,
        user,
        token,
        verify_ssl=False,
    ):
        self.host = host.rstrip("/")
        self.user = user
        self.token = token
        self.verify_ssl = verify_ssl

    def _request(self, endpoint):
        url = f"{self.host}/api2/json/{endpoint.lstrip('/')}"

        request = Request(url)

        if self.token:
            request.add_header(
                "Authorization",
                f"PVEAPIToken={self.user}={self.token}",
            )

        context = None

        if not self.verify_ssl:
            context = ssl._create_unverified_context()

        try:
            with urlopen(
                request,
                timeout=10,
                context=context,
            ) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except HTTPError as exc:
            raise RuntimeError(
                f"Proxmox API returned HTTP {exc.code}"
            ) from exc

        except URLError as exc:
            raise RuntimeError(
                f"Unable to connect to Proxmox: {exc.reason}"
            ) from exc

    def get_node_status(self):
        """
        Return basic information about the first Proxmox node.
        """

        response = self._request("nodes")

        nodes = response.get("data", [])

        if not nodes:
            raise RuntimeError(
                "No Proxmox nodes were returned."
            )

        node = nodes[0]

        memory_total = node.get("maxmem", 0)
        memory_used = node.get("mem", 0)

        memory_total_gb = memory_total / 1024**3
        memory_used_gb = memory_used / 1024**3

        memory_percent = 0

        if memory_total:
            memory_percent = (
                memory_used / memory_total
            ) * 100

        return {
            "name": node.get("node", "unknown"),
            "status": (
                "online"
                if node.get("status") == "online"
                else "offline"
            ),
            "cpu_percent": (
                node.get("cpu", 0) * 100
            ),
            "memory_used_gb": memory_used_gb,
            "memory_total_gb": memory_total_gb,
            "memory_percent": memory_percent,
        }

    def get_virtual_machines(self):
        """
        Return the VM list from the first Proxmox node.
        """

        response = self._request("cluster/resources?type=vm")

        vms = []

        for item in response.get("data", []):
            if item.get("type") != "qemu":
                continue

            vms.append(
                {
                    "vmid": item.get("vmid"),
                    "name": item.get(
                        "name",
                        f"vm-{item.get('vmid')}",
                    ),
                    "status": item.get(
                        "status",
                        "unknown",
                    ),
                    "cpu_percent": (
                        item.get("cpu", 0) * 100
                    ),
                    "memory_percent": self._memory_percent(
                        item
                    ),
                }
            )

        return vms

    @staticmethod
    def _memory_percent(vm):
        max_memory = vm.get("maxmem", 0)
        memory = vm.get("mem", 0)

        if not max_memory:
            return 0

        return (
            memory / max_memory
        ) * 100
