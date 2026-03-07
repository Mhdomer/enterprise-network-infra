#!/usr/bin/env python3
"""
Audit script — pulls structured data from all devices using NAPALM,
saves JSON audit files to configs/<hostname>-audit-<date>.json.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from napalm import get_network_driver
from napalm.base.exceptions import ConnectionException


DEVICES = [
    {"hostname": "172.16.0.1",  "name": "hq-router",       "driver": "ios"},
    {"hostname": "172.16.0.2",  "name": "branch-a-router",  "driver": "ios"},
    {"hostname": "172.16.0.3",  "name": "branch-b-router",  "driver": "ios"},
    {"hostname": "172.16.0.10", "name": "hq-switch",        "driver": "ios"},
]

CREDS = {
    "username": "admin",
    "password": "ADMIN_PASS",
}

CONFIGS_DIR = Path(__file__).parent.parent / "configs"


def audit_device(device: dict) -> dict:
    driver = get_network_driver(device["driver"])
    dev = driver(
        hostname=device["hostname"],
        username=CREDS["username"],
        password=CREDS["password"],
    )

    try:
        dev.open()
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "device": device["name"],
            "host": device["hostname"],
            "facts": dev.get_facts(),
            "interfaces": dev.get_interfaces(),
            "interfaces_ip": dev.get_interfaces_ip(),
            "lldp_neighbors": dev.get_lldp_neighbors(),
            "environment": dev.get_environment(),
            "ntp_servers": dev.get_ntp_servers(),
            "ntp_stats": dev.get_ntp_stats(),
            "route_to_default": dev.get_route_to("0.0.0.0/0"),
        }
    finally:
        dev.close()

    return audit


def save_audit(name: str, data: dict):
    date_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    device_dir = CONFIGS_DIR / name
    device_dir.mkdir(parents=True, exist_ok=True)

    output_path = device_dir / f"audit-{date_str}.json"
    output_path.write_text(json.dumps(data, indent=2, default=str))
    print(f"Saved: {output_path}")
    return output_path


def main():
    errors = []
    for device in DEVICES:
        print(f"Auditing {device['name']} ({device['hostname']})...")
        try:
            audit = audit_device(device)
            save_audit(device["name"], audit)
        except ConnectionException as e:
            msg = f"{device['name']}: connection failed — {e}"
            print(f"ERROR: {msg}", file=sys.stderr)
            errors.append(msg)

    if errors:
        print(f"\n{len(errors)} device(s) failed audit.", file=sys.stderr)
        sys.exit(1)

    print("\nAll audits complete.")


if __name__ == "__main__":
    main()
