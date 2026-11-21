#!/usr/bin/env python3

from homelab_monitor.config import load_config
from homelab_monitor.proxmox import ProxmoxClient


def print_header():
    print("=" * 40)
    print("          HOMELAB MONITOR")
    print("=" * 40)
    print()


def print_node_status(node):
    print(f"Proxmox Host: {node['name']}")
    print(f"Status:       {node['status'].upper()}")
    print()

    if node["status"] != "online":
        return

    print(f"CPU Usage:    {node['cpu_percent']:.1f}%")
    print(
        f"Memory:       "
        f"{node['memory_used_gb']:.1f} GB / "
        f"{node['memory_total_gb']:.1f} GB"
    )
    print(f"Memory Usage: {node['memory_percent']:.1f}%")
    print()


def print_vms(vms):
    print("Virtual Machines")
    print("-" * 40)

    for vm in vms:
        print(f"{vm['name']:<14} {vm['status'].upper()}")

    print()


def print_alerts(node, vms, config):
    alerts = []

    if node["status"] != "online":
        alerts.append("Proxmox host is offline.")

    if node["cpu_percent"] >= config["cpu_warning_percent"]:
        alerts.append(
            f"CPU usage is above "
            f"{config['cpu_warning_percent']}%."
        )

    if node["memory_percent"] >= config["memory_warning_percent"]:
        alerts.append(
            f"Memory usage is above "
            f"{config['memory_warning_percent']}%."
        )

    for vm in vms:
        if vm["status"] != "running":
            alerts.append(
                f"{vm['name']} is {vm['status']}."
            )

    print("Alerts")
    print("-" * 40)

    if not alerts:
        print("No alerts.")
    else:
        for alert in alerts:
            print(f"WARNING: {alert}")

    print()


def main():
    config = load_config()

    client = ProxmoxClient(
        host=config["proxmox_host"],
        user=config["proxmox_user"],
        token=config["proxmox_token"],
        verify_ssl=config["verify_ssl"],
    )

    print_header()

    try:
        node = client.get_node_status()
        vms = client.get_virtual_machines()

        print_node_status(node)
        print_vms(vms)
        print_alerts(node, vms, config)

    except Exception as exc:
        print(f"ERROR: Unable to collect Proxmox data.")
        print(f"Details: {exc}")


if __name__ == "__main__":
    main()
