#!/usr/bin/env python3
"""
Dynamic inventory script — queries GNS3 REST API and returns Ansible host list.
Usage:
  ansible-inventory -i dynamic_inventory.py --list
  ansible-inventory -i dynamic_inventory.py --host <hostname>
"""

import json
import sys

import requests

GNS3_API = "http://localhost:3080/v2"
PROJECT_ID = "REPLACE_WITH_YOUR_GNS3_PROJECT_ID"

MGMT_IPS = {
    "hq-router":       "172.16.0.1",
    "branch-a-router": "172.16.0.2",
    "branch-b-router": "172.16.0.3",
    "hq-switch":       "172.16.0.10",
    "branch-a-switch": "172.16.0.11",
    "branch-b-switch": "172.16.0.12",
}


def get_nodes():
    url = f"{GNS3_API}/projects/{PROJECT_ID}/nodes"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


def build_inventory(nodes):
    inventory = {
        "routers": {"hosts": [], "vars": {}},
        "switches": {"hosts": [], "vars": {}},
        "_meta": {"hostvars": {}},
    }

    for node in nodes:
        name = node.get("name", "").lower()
        if node.get("status") != "started":
            continue

        mgmt_ip = MGMT_IPS.get(name)
        if not mgmt_ip:
            continue

        hostvars = {
            "ansible_host": mgmt_ip,
            "ansible_network_os": "cisco.ios.ios",
            "ansible_connection": "network_cli",
            "ansible_user": "admin",
            "gns3_node_id": node["node_id"],
        }

        if "router" in name:
            inventory["routers"]["hosts"].append(name)
        elif "switch" in name:
            inventory["switches"]["hosts"].append(name)

        inventory["_meta"]["hostvars"][name] = hostvars

    return inventory


def main():
    if "--list" in sys.argv:
        try:
            nodes = get_nodes()
            print(json.dumps(build_inventory(nodes), indent=2))
        except requests.exceptions.ConnectionError:
            # GNS3 not running — fall back to static hosts so playbooks still work
            fallback = {
                "routers": {"hosts": ["hq-router", "branch-a-router", "branch-b-router"]},
                "switches": {"hosts": ["hq-switch", "branch-a-switch", "branch-b-switch"]},
                "_meta": {
                    "hostvars": {h: {"ansible_host": ip} for h, ip in MGMT_IPS.items()}
                },
            }
            print(json.dumps(fallback, indent=2))
    elif "--host" in sys.argv:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
