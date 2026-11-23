import json
import ssl
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ProxmoxAPIError(RuntimeError):
    """Raised when a Proxmox API request fails."""


class ProxmoxClient:
    """
    Lightweight Proxmox VE API client.

    Uses Python's standard library to avoid requiring external
    dependencies. The client supports API token authentication,
    configurable SSL verification, and basic node/VM monitoring.
    """

    def __init__(
        self,
        host: str,
        user: str,
        token: str,
        verify_ssl: bool = True,
        timeout: int = 10,
    ) -> None:
        self.host = host.rstrip("/")
        self.user = user
        self.token = token
        self.verify_ssl = verify_ssl
        self.timeout = timeout

    def _request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request to the Proxmox JSON API."""

        endpoint = endpoint.lstrip("/")

        if params:
            endpoint = f"{endpoint}?{urlencode(params)}"

        url = f"{self.host}/api2/json/{endpoint}"

        request = Request(
            url,
            method=method,
        )

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
                timeout=self.timeout,
                context=context,
            ) as response:
                body = response.read().decode("utf-8")

                return json.loads(body)

        except HTTPError as exc:
            try:
                response_body = exc.read().decode("utf-8")
                details = json.loads(response_body)

                message = details.get(
                    "errors",
                    details.get("message", "Unknown API error"),
                )
            except (ValueError, UnicodeDecodeError):
                message = exc.reason

            raise ProxmoxAPIError(
                f"Proxmox API returned HTTP {exc.code}: {message}"
            ) from exc

        except URLError as exc:
            raise ProxmoxAPIError(
                f"Unable to connect to Proxmox: {exc.reason}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise ProxmoxAPIError(
                "Proxmox returned an invalid JSON response."
            ) from exc

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Return all nodes in the Proxmox cluster."""

        response = self._request("nodes")

        return response.get("data", [])

    def get_node_status(
        self,
        node_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return basic status information for a Proxmox node.

        If no node name is provided, the first available node is used.
        """

        nodes = self.get_nodes()

        if not nodes:
            raise ProxmoxAPIError(
                "No Proxmox nodes were returned."
            )

        node = None

        if node_name:
            for candidate in nodes:
                if candidate.get("node") == node_name:
                    node = candidate
                    break

            if node is None:
                raise ProxmoxAPIError(
                    f"Proxmox node '{node_name}' was not found."
                )
        else:
            node = nodes[0]

        memory_total = node.get("maxmem", 0)
        memory_used = node.get("mem", 0)

        memory_total_gb = memory_total / 1024**3
        memory_used_gb = memory_used / 1024**3

        memory_percent = 0.0

        if memory_total:
            memory_percent = (
                memory_used / memory_total
            ) * 100

        return {
            "name": node.get("node", "unknown"),
            "status": node.get("status", "unknown"),
            "cpu_percent": node.get("cpu", 0) * 100,
            "memory_used_gb": round(memory_used_gb, 2),
            "memory_total_gb": round(memory_total_gb, 2),
            "memory_percent": round(memory_percent, 2),
            "uptime": node.get("uptime", 0),
        }

    def get_virtual_machines(
        self,
        node_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return QEMU virtual machines from the Proxmox cluster.

        Optionally filter results to a specific node.
        """

        params = {"type": "vm"}

        if node_name:
            params["node"] = node_name

        response = self._request(
            "cluster/resources",
            params=params,
        )

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
                    "node": item.get("node"),
                    "status": item.get(
                        "status",
                        "unknown",
                    ),
                    "cpu_percent": round(
                        item.get("cpu", 0) * 100,
                        2,
                    ),
                    "cpu_count": item.get("maxcpu", 0),
                    "memory_used_mb": round(
                        item.get("mem", 0) / 1024**2,
                        2,
                    ),
                    "memory_total_mb": round(
                        item.get("maxmem", 0) / 1024**2,
                        2,
                    ),
                    "memory_percent": self._memory_percent(
                        item
                    ),
                    "uptime": item.get("uptime", 0),
                }
            )

        return vms

    @staticmethod
    def _memory_percent(
        vm: Dict[str, Any],
    ) -> float:
        """Calculate VM memory utilization percentage."""

        max_memory = vm.get("maxmem", 0)
        memory = vm.get("mem", 0)

        if not max_memory:
            return 0.0

        return round(
            (memory / max_memory) * 100,
            2,
        )
