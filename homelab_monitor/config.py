import os


def _get_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in ("1", "true", "yes", "on")


def load_config():
    """
    Load application configuration from environment variables.
    """

    return {
        "proxmox_host": os.getenv(
            "PROXMOX_HOST",
            "https://127.0.0.1:8006",
        ),
        "proxmox_user": os.getenv(
            "PROXMOX_USER",
            "monitor@pam",
        ),
        "proxmox_token": os.getenv(
            "PROXMOX_TOKEN",
            "",
        ),
        "verify_ssl": _get_bool(
            "PROXMOX_VERIFY_SSL",
            default=False,
        ),
        "cpu_warning_percent": float(
            os.getenv(
                "CPU_WARNING_PERCENT",
                "80",
            )
        ),
        "memory_warning_percent": float(
            os.getenv(
                "MEMORY_WARNING_PERCENT",
                "80",
            )
        ),
    }
