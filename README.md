# Home Lab Infrastructure

Personal infrastructure project built around a Proxmox VE virtualization
environment.

The goal of this lab is to provide a realistic environment for experimenting
with virtualization, Linux, networking, automation, monitoring, containers,
and self-hosted services.

## Hardware

| Component | Specification |
|---|---|
| CPU | AMD Ryzen 9 7900 |
| CPU Cores | 12C / 24T |
| Memory | 128 GB DDR5 ECC |
| Storage | 1 TB NVMe + 2 × 2 TB NVMe |
| Network | 10 GbE |
| Public Network | Dedicated IP |
| Hypervisor | Proxmox VE |

## Planned Infrastructure

- Proxmox VE
- Linux virtual machines
- LXC containers
- Docker
- Internal DNS
- Reverse proxy
- Monitoring
- Automated backups
- Infrastructure as Code
- Network segmentation
- Self-hosted services

## Architecture

```text
                         Internet
                            │
                     Dedicated IP
                            │
                       10 GbE NIC
                            │
                     ┌──────▼──────┐
                     │   Proxmox   │
                     │     VE      │
                     └──────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
          ┌───▼───┐     ┌───▼───┐     ┌───▼───┐
          │ Linux │     │ Docker│     │  LXC  │
          │  VM   │     │  VM   │     │       │
          └───────┘     └───────┘     └───────┘
